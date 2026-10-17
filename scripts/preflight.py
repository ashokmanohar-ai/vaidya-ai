"""Read-only environment preflight for the leadership demonstration."""
from importlib.util import find_spec
from pathlib import Path
import os,sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from dotenv import load_dotenv
load_dotenv(ROOT/'.env',override=False)
print('VAIDYA AI · SYNTHETIC LEADERSHIP DEMO · PRE-FLIGHT')
print('Python:',sys.version.split()[0])
required=['dotenv','flask','jinja2','docx','PIL','boto3','langgraph','langgraph.checkpoint.sqlite']
missing=[]
for mod in required:
    try: available=find_spec(mod) is not None
    except ModuleNotFoundError: available=False
    print(('PASS' if available else 'MISSING'),mod)
    if not available:missing.append(mod)
print('LangGraph orchestration: REQUIRED')
print('CPU audio ASR installed:',find_spec('faster_whisper') is not None)
print('ASR_PROVIDER:',os.getenv('ASR_PROVIDER','faster-whisper'))
print('TRANSLATION_PROVIDER:',os.getenv('TRANSLATION_PROVIDER','passthrough'))
print('ASR installation is optional for text-only demo but REQUIRED for uploaded voice notes.')
print('Demo mode will be enabled by scripts/run_demo.py')
from vaidya.providers import bedrock_settings
settings=bedrock_settings()
print('LLM provider:',settings['provider'])
print('Bedrock model:',settings['model'])
print('Bedrock region:',settings['region'])
print('Remote synthetic opt-in:',settings['remote_opt_in'])
print('Bedrock bearer token configured:',settings['credential_configured'])
print('Local instance disk exists:',(ROOT/'instance').exists())
if missing:
    print('NOT READY — install requirements-dev.txt in Python virtual environment')
    sys.exit(1)
print('DEPENDENCY CHECK PASSED. Persistent LangGraph enabled; proceed with python scripts/run_demo.py')
