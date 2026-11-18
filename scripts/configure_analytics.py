"""Create local read-only analytics credentials; never prints the generated token."""
import argparse
import json
import os
from pathlib import Path
import secrets
import shlex
import tempfile


def configure(path, subject='analyst'):
    if not subject.strip():
        raise ValueError('Subject must not be empty')
    token = secrets.token_urlsafe(32)
    web_token = secrets.token_urlsafe(32)
    registry = json.dumps({token: dict(subject=subject, scopes=['balance:read']),
                          web_token: dict(subject='web-analyst', scopes=['balance:read'])}, ensure_ascii=False, separators=(',', ':'))
    # JSON is single-quoted so the file works with both Compose --env-file and
    # POSIX shell sourcing. JSON escapes work with both dotenv and shell.
    escaped = registry.replace("'", '\\u0027')
    content = "BALANCE_ANALYTICS_TOKENS='%s'\nBALANCE_ANALYTICS_TOKEN=%s\nBALANCE_ASSISTANT_TOKEN=%s\nBALANCE_ANALYTICS_URL=http://127.0.0.1:5001\nBALANCE_OLLAMA_MODEL=qwen3.5:4b-q4_K_M\n" % (escaped, token, web_token)
    descriptor = os.open(str(path), os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    with os.fdopen(descriptor, 'w') as stream:
        stream.write(content)


def enable_assistant(path):
    """Add a dedicated browser role without replacing existing credentials."""
    lines = path.read_text().splitlines()
    settings = {}
    for line in lines:
        if '=' in line and not line.lstrip().startswith('#'):
            key,value = line.split('=',1)
            parsed = shlex.split(value,comments=False)
            settings[key] = parsed[0] if parsed else ''
    registry = json.loads(settings.get('BALANCE_ANALYTICS_TOKENS','{}'))
    if settings.get('BALANCE_ASSISTANT_TOKEN'):
        return False
    base = registry.get(settings.get('BALANCE_ANALYTICS_TOKEN',''))
    if not isinstance(base,dict) or 'balance:read' not in base.get('scopes',[]):
        raise ValueError('Cannot infer browser permissions. Configure a separate read-only role in BALANCE_ANALYTICS_TOKENS and BALANCE_ASSISTANT_TOKEN.')
    web_token = secrets.token_urlsafe(32)
    role = dict(subject='web-analyst',scopes=['balance:read'])
    for key in ('product_ids','basis_ids'):
        if key in base:
            role[key] = base[key]
    registry[web_token] = role
    encoded = json.dumps(registry,ensure_ascii=False,separators=(',',':')).replace("'",'\\u0027')
    retained = [line for line in lines if not line.startswith(('BALANCE_ANALYTICS_TOKENS=','BALANCE_ASSISTANT_TOKEN='))]
    retained.extend(["BALANCE_ANALYTICS_TOKENS='%s'" % encoded,'BALANCE_ASSISTANT_TOKEN='+web_token])
    if 'BALANCE_OLLAMA_MODEL' not in settings:
        retained.append('BALANCE_OLLAMA_MODEL=qwen3.5:4b-q4_K_M')
    descriptor,temporary = tempfile.mkstemp(prefix='.analytics-',dir=str(path.parent))
    try:
        with os.fdopen(descriptor,'w') as stream:
            stream.write('\n'.join(retained)+'\n')
        os.replace(temporary,path)
    finally:
        if os.path.exists(temporary): os.unlink(temporary)
    return True


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--subject', default='analyst')
    parser.add_argument('--output', type=Path, default=Path(__file__).resolve().parents[1]/'.env.analytics')
    parser.add_argument('--enable-assistant',action='store_true',help='Add a browser role to an existing configuration, preserving its keys and scopes')
    args = parser.parse_args()
    if args.enable_assistant and args.output.exists():
        changed = enable_assistant(args.output)
        print('Added browser role:' if changed else 'Existing browser role retained:',args.output)
        raise SystemExit(0)
    try:
        configure(args.output, args.subject)
        print('Created local analytics configuration:', args.output)
    except FileExistsError:
        print('Existing configuration retained:', args.output)
