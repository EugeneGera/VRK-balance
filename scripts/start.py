"""Start the local balance application and reuse its installed model and database."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import shlex
import shutil
import signal
import subprocess
import sys
import time
from urllib.error import URLError
from urllib.request import ProxyHandler, Request, build_opener
import webbrowser

ROOT = Path(__file__).resolve().parents[1]
RUNTIME = ROOT / '.runtime'
OLLAMA = 'http://127.0.0.1:11434'
APP = 'http://localhost:3000/balance_comission'
TRIAL_MODEL = 'qwen3:0.6b'
EXPERIMENT_MODEL = 'qwen3.5:4b-q4_K_M'
HTTP = build_opener(ProxyHandler({}))


def run(*args, capture=False, input_data=None, env=None):
    result = subprocess.run(args, cwd=ROOT, env=env, input=input_data,
                            stdout=subprocess.PIPE if capture else None, check=True)
    return result.stdout.decode().strip() if capture else ''


def available(*args):
    return subprocess.run(args, cwd=ROOT, stdout=subprocess.DEVNULL,
                          stderr=subprocess.DEVNULL).returncode == 0


def fetch(url, body=None, timeout=5):
    request = Request(url, data=json.dumps(body).encode() if body is not None else None,
                      headers={'Content-Type': 'application/json'})
    return HTTP.open(request, timeout=timeout)


def read_json(url, body=None, timeout=5):
    with fetch(url, body, timeout) as response:
        return json.load(response)


def wait_for(check, message, seconds):
    deadline = time.monotonic() + seconds
    print(message, flush=True)
    while time.monotonic() < deadline:
        try:
            result = check()
            if result:
                return result
        except (OSError, URLError, ValueError):
            pass
        time.sleep(1)
    raise RuntimeError(message + ' Время ожидания истекло.')


def inspect(name):
    result = subprocess.run(['docker', 'inspect', name], capture_output=True, cwd=ROOT)
    if result.returncode:
        return None
    return json.loads(result.stdout)[0]


def project_name():
    backend = inspect('bcp_backend')
    if backend:
        sources = [mount['Source'] for mount in backend['Mounts'] if mount['Destination'] == '/backend']
        if sources and Path(sources[0]).resolve() != (ROOT / 'backend').resolve():
            raise RuntimeError('Контейнер bcp_backend относится к другой папке проекта.')
    for service in (backend, inspect('bcp_PGDB')):
        if service:
            project = (service['Config']['Labels'] or {}).get('com.docker.compose.project')
            if project:
                return project
    return 'vkr-balance'


def installed_models():
    data = read_json(OLLAMA + '/api/tags')
    return {item['name'] for item in data['models']}


def start_model():
    try:
        installed_models()
        return
    except (OSError, URLError, ValueError):
        pass
    with (RUNTIME / 'ollama.log').open('ab') as log:
        process = subprocess.Popen([sys.executable, str(ROOT / 'scripts/run_local_model.py')], cwd=ROOT,
                                   stdin=subprocess.DEVNULL, stdout=log, stderr=subprocess.STDOUT,
                                   start_new_session=True)
    (RUNTIME / 'ollama.pid').write_text(str(process.pid))
    wait_for(lambda: read_json(OLLAMA + '/api/tags'), 'Запускаем локальную модель…', 45)


def stop_model():
    pid_file = RUNTIME / 'ollama.pid'
    if not pid_file.exists():
        return
    pid = int(pid_file.read_text())
    process = subprocess.run(['ps', '-p', str(pid), '-o', 'command='], capture_output=True, text=True)
    if pid > 1 and str(ROOT / 'scripts/run_local_model.py') in process.stdout:
        try:
            os.killpg(pid, signal.SIGTERM)
        except ProcessLookupError:
            pass
    pid_file.unlink(missing_ok=True)


def select_model(quality, experiment=False):
    settings = ROOT / '.env.analytics'
    preferred = 'qwen3.5:4b-q4_K_M'
    for line in settings.read_text().splitlines():
        if line.startswith('BALANCE_OLLAMA_MODEL='):
            preferred = shlex.split(line.partition('=')[2])[0]
            break
    installed = installed_models()
    model = EXPERIMENT_MODEL if experiment else preferred if quality or preferred in installed else TRIAL_MODEL
    if model in installed:
        return model
    print(f'Загружаем {model} для первого запуска…', flush=True)
    run(sys.executable, 'scripts/run_local_model.py', '--pull', '--model', model)
    if model not in installed_models():
        raise RuntimeError('Модель ещё не появилась в каталоге Ollama.')
    return model


def experiment_profile(status):
    """Pin the exact installed weights and inference settings for this experiment."""
    if status.get('model') != EXPERIMENT_MODEL or not status.get('digest') or not status.get('settings'):
        raise RuntimeError('Не удалось определить экспериментальную модель и её настройки.')
    profile = dict(model=EXPERIMENT_MODEL, digest=status['digest'], settings=status['settings'],
                   ollama_version=read_json(OLLAMA + '/api/version')['version'])
    path = RUNTIME / 'experiment-profile.json'
    if path.exists() and json.loads(path.read_text()) != profile:
        raise RuntimeError('Веса, настройки или версия Ollama отличаются от зафиксированного профиля эксперимента.')
    if not path.exists():
        with path.open('x') as file:
            json.dump(profile, file, indent=2)
    return profile


def build_services(compose, project, env, rebuild):
    for service in ('bcp_backend', 'bcp_client'):
        if rebuild or not available('docker', 'image', 'inspect', f'{project}-{service}'):
            run(*compose, 'build', service, env=env)
    digest = hashlib.sha256()
    for directory in ('agent_server', 'mcp_server'):
        for path in sorted((ROOT / directory).iterdir()):
            if path.is_file():
                digest.update(path.name.encode())
                digest.update(path.read_bytes())
    signature_path = RUNTIME / 'images.sha256'
    signature = project + ':' + digest.hexdigest()
    previous = signature_path.read_text() if signature_path.exists() else ''
    services = ('balance_agent', 'balance_mcp')
    if rebuild or previous != signature or any(not available('docker', 'image', 'inspect', f'{project}-{service}') for service in services):
        run(*compose, 'build', *services, env=env)
        signature_path.write_text(signature)


def prepare_database(compose):
    database = inspect('bcp_PGDB')
    if database:
        if not database['State']['Running']:
            run('docker', 'start', 'bcp_PGDB')
    else:
        run(*compose, 'up', '-d', '--no-deps', 'db')
    wait_for(lambda: available('docker', 'exec', 'bcp_PGDB', 'pg_isready', '-U', 'postgres', '-d', 'balance_comission'),
             'Ожидаем PostgreSQL…', 60)
    psql = ('docker', 'exec', '-i', 'bcp_PGDB', 'psql', '-X', '-U', 'postgres', '-d', 'balance_comission', '-v', 'ON_ERROR_STOP=1')
    if run(*psql, '-Atc', "SELECT to_regclass('public.tab_dataset_bk') IS NOT NULL", capture=True) == 't':
        return
    tables = run(*psql, '-Atc', "SELECT count(*) FROM information_schema.tables WHERE table_schema NOT IN ('pg_catalog', 'information_schema')", capture=True)
    if tables != '0':
        raise RuntimeError('В базе есть таблицы, но схема баланса неполна. Проверьте выбранную базу.')
    print('Загружаем демонстрационные данные в пустую базу…', flush=True)
    run(*psql, '--single-transaction', capture=True, input_data=(ROOT / 'BK.sql').read_bytes())


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group()
    group.add_argument('--quality', action='store_true')
    group.add_argument('--experiment', action='store_true')
    parser.add_argument('--stop', action='store_true')
    parser.add_argument('--rebuild', action='store_true')
    parser.add_argument('--no-browser', action='store_true')
    args = parser.parse_args()
    RUNTIME.mkdir(exist_ok=True)
    if not shutil.which('docker'):
        raise RuntimeError('Установите Docker Desktop.')
    docker_ready = lambda: available('docker', 'info')
    if not docker_ready() and not args.stop:
        if sys.platform == 'darwin':
            run('open', '-a', 'Docker')
        wait_for(docker_ready, 'Ожидаем Docker…', 180)
    if args.stop and not docker_ready():
        stop_model()
        return
    if args.stop and not (ROOT / '.env.analytics').exists():
        stop_model()
        return
    if not args.stop:
        run(sys.executable, 'scripts/configure_analytics.py', '--enable-assistant')
    project = project_name()
    compose = ('docker', 'compose', '-p', project, '--env-file', '.env.analytics',
               '-f', 'docker-compose.dev.yaml', '-f', 'docker-compose.mcp.yaml')
    services = ('bcp_backend', 'balance_mcp', 'balance_agent', 'bcp_client')
    if args.stop:
        run(*compose, 'stop', *services, 'db')
        stop_model()
        return
    start_model()
    model = select_model(args.quality, args.experiment)
    digest = ''
    if args.experiment:
        digest = next((item.get('digest') for item in read_json(OLLAMA + '/api/tags')['models']
                       if item['name'] == model), None)
        if not digest:
            raise RuntimeError('Не удалось получить контрольную сумму весов экспериментальной модели.')
        pinned = RUNTIME / 'experiment-profile.json'
        if pinned.exists() and json.loads(pinned.read_text())['digest'] != digest:
            raise RuntimeError('Веса модели отличаются от зафиксированного профиля эксперимента.')
    env = dict(os.environ, BALANCE_OLLAMA_MODEL=model, BALANCE_EXPERIMENT_DIGEST=digest)
    build_services(compose, project, env, args.rebuild)
    prepare_database(compose)
    run(*compose, 'up', '-d', '--no-deps', *services, env=env)

    def ready():
        result = read_json('http://127.0.0.1:5001/assistant/status')
        status = result.get('data', {})
        expected_profile = 'experiment' if args.experiment else 'local'
        if status.get('ready') and status.get('model') == model and status.get('profile') == expected_profile:
            return status

    status = wait_for(ready, 'Проверяем сервис отчётов…', 120)
    print('Проверяем пробный ответ модели…', flush=True)
    answer = read_json(OLLAMA + '/api/chat', {
        'model': model, 'messages': [{'role': 'user', 'content': 'Ответь одним словом: готово'}],
        'stream': False, 'think': False, 'keep_alive': '2m',
        'options': {key: status['settings'][key] for key in ('num_ctx', 'seed', 'temperature', 'num_predict')},
    }, timeout=120)
    if not answer['message'].get('content'):
        raise RuntimeError('Модель не вернула пробный ответ.')
    if args.experiment:
        experiment_profile(status)

    def frontend_ready():
        with fetch(APP) as response:
            return response.status == 200

    wait_for(frontend_ready, 'Ожидаем панель баланса…', 60)
    print(f'Готово. Откройте {APP} и нажмите «Подготовить отчёт».', flush=True)
    if not args.no_browser:
        webbrowser.open(APP)


if __name__ == '__main__':
    import fcntl

    RUNTIME.mkdir(exist_ok=True)
    try:
        with (RUNTIME / 'start.lock').open('a') as lock:
            fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
            main()
    except BlockingIOError:
        sys.exit('Другой запуск уже выполняется.')
    except (OSError, RuntimeError, ValueError, subprocess.CalledProcessError) as error:
        sys.exit(f'Не удалось завершить запуск. {error}')
