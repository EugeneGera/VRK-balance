"""Start local-only Ollama, or download the configured model once with --pull."""
import argparse
import os
from pathlib import Path
import shutil
import shlex
import subprocess

ROOT=Path(__file__).resolve().parents[1]


def main():
    configured_model='qwen3.5:4b-q4_K_M'
    settings=ROOT/'.env.analytics'
    if settings.is_file():
        line=next((line for line in settings.read_text().splitlines() if line.startswith('BALANCE_OLLAMA_MODEL=')),None)
        if line:
            values=shlex.split(line.partition('=')[2],comments=False)
            if values: configured_model=values[0]
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--pull',action='store_true',help='Download the model into the running local Ollama server')
    parser.add_argument('--model',default=os.environ.get('BALANCE_OLLAMA_MODEL',configured_model))
    args=parser.parse_args()
    portable=ROOT/'.runtime/ollama/ollama'
    candidates=[str(portable),shutil.which('ollama'),'/Applications/Ollama.app/Contents/Resources/ollama']
    binary=next((path for path in candidates if path and Path(path).is_file()),None)
    if not binary:
        parser.error('Install Ollama first: https://ollama.com/download/mac')
    env=dict(os.environ,OLLAMA_NO_CLOUD='1',OLLAMA_NUM_PARALLEL='1',OLLAMA_MAX_LOADED_MODELS='1',OLLAMA_CONTEXT_LENGTH='8192')
    env.setdefault('OLLAMA_HOST','127.0.0.1:11434')
    if portable.is_file():
        env.setdefault('OLLAMA_MODELS',str(ROOT/'.runtime/models'))
    command=[binary,'pull',args.model] if args.pull else [binary,'serve']
    raise SystemExit(subprocess.call(command,env=env))


if __name__=='__main__':main()
