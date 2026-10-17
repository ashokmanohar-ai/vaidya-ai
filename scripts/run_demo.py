"""Start synthetic demo. Run from repository root with python scripts/run_demo.py."""
import os,sys
from pathlib import Path
root=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(root))
from dotenv import load_dotenv
load_dotenv(root/'.env', override=False)
os.environ['DEMO_MODE']='true'
os.environ['LLM_PROVIDER']=os.environ.get('LLM_PROVIDER','demo')
from app import app,DB
from vaidya.learning import create_seed_learning
from vaidya.presentation import seed_story
DB.seed_demo()
create_seed_learning(DB)
if os.getenv("VAIDYA_EMPTY_DEMO") != "1":
    count=seed_story(DB,root/"instance")
    if count: print(f"Seeded {count} clearly labeled synthetic report examples for presentation.")
# LangGraph is mandatory for the full multi-agent build; do not silently fall back.
from app import graph_runtime
runtime=graph_runtime()
# Seeded synthetic proposals are given a durable admin approval interrupt at startup.
for suggestion in DB.query("SELECT id FROM learnings WHERE status='suggested' AND supporting_jobs>=5"):
    runtime.prepare_learning_review(suggestion['id'])
port=int(os.getenv('PORT','5055'))
print(f'VAIDYA AI multi-agent synthetic demo: http://127.0.0.1:{port}')
print(f'Persistent LangGraph checkpoint DB: {runtime.checkpoint_path}')
from vaidya.providers import bedrock_settings
settings=bedrock_settings()
print(f"Extraction provider: {settings['provider']} | Model: {settings['model']} | AWS Region: {settings['region']}")
print('Parent graph: Orchestrator | Specialist subgraphs: Pathology and Learner')
print('Doctor: doctor@vaidya.demo / DemoDoctor!2026')
print('Administrator: admin@vaidya.demo / DemoAdmin!2026')
print('NOT FOR REAL PATIENT DATA; launch is intentionally local-only.')
app.run(host='127.0.0.1',port=port,debug=False)
