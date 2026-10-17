"""True Flask client integration; requires Flask to be installed in the target environment."""
import os
import sys
from pathlib import Path
import pytest

pytest.importorskip('flask')

@pytest.fixture
def client(tmp_path,monkeypatch):
    monkeypatch.setenv('VAIDYA_DATA_DIR',str(tmp_path/'runtime'))
    monkeypatch.setenv('DEMO_MODE','true')
    monkeypatch.setenv('LLM_PROVIDER','demo')
    sys.modules.pop('app',None)
    import app as module
    module.app.config['TESTING']=True
    module.DB.seed_demo()
    return module.app.test_client()


def login(client,email='doctor@vaidya.demo',pw='DemoDoctor!2026'):
    resp=client.get('/login')
    import re
    html=resp.data.decode()
    token=re.search(r'name="_csrf" value="([a-f0-9]+)"',html).group(1)
    resp=client.post('/login',data={'email':email,'password':pw,'_csrf':token},follow_redirects=True)
    return resp


def token_for(client,url):
    import re
    body=client.get(url).data.decode()
    return re.search(r'name="_csrf" value="([a-f0-9]+)"',body).group(1)


def test_public_health_and_demo_login(client):
    assert client.get('/health/live').status_code==200
    assert client.get('/health/ready').json['clinical_ready'] is False
    assert b'Sign in' in client.get('/login').data
    assert b'Good day' in login(client).data


def test_doctor_complete_workflow(client):
    from vaidya.database import Database
    login(client)
    token=token_for(client,'/reports/new')
    payload={'patient_id':'1','transcript':'Synthetic appendix specimen. Please bold appendix in the report.','_csrf':token}
    res=client.post('/reports/create',data=payload,follow_redirects=False)
    assert res.status_code==302 and '/reports/' in res.location
    review=client.get(res.location)
    assert review.status_code==200
    assert b'Download DOCX draft' in review.data
    token=token_for(client,res.location)
    jobid=res.location.rstrip('/').split('/')[-1]
    doc=client.get(f'/reports/{jobid}/download')
    assert doc.status_code==200 and doc.data[:2]==b'PK'
    graph=client.get(f'/api/v1/jobs/{jobid}/graph')
    assert graph.status_code==200
    assert graph.json['checkpoint']['exists']
    assert graph.json['checkpoint']['pending_nodes']
    assert any(x['agent']=='pathology_agent' for x in graph.json['stages'])
    approved=client.post(f'/reports/{jobid}/approve',data={
       '_csrf':token,'final_text':'Synthetic appendix specimen.\nSignature: Dr. Brindha','attest':'yes'
    },follow_redirects=True)
    assert b'Doctor approved' in approved.data
    assert client.get(f'/reports/{jobid}/final-download').data[:2]==b'PK'
    assert client.get(f'/api/v1/jobs/{jobid}').json['status']=='approved'
    after=client.get(f'/api/v1/jobs/{jobid}/graph').json['checkpoint']
    assert after['pending_nodes']==[]
    assert after['stage']=='doctor_review_completed'
    assert client.post(f'/reports/{jobid}/approve',data={'_csrf':token,'final_text':'x','attest':'yes'}).status_code==409


def test_no_cross_role_access(client):
    login(client)
    assert client.get('/admin').status_code==403
    login(client,'admin@vaidya.demo','DemoAdmin!2026')
    assert client.get('/dashboard').status_code==403
    assert client.get('/admin').status_code==200


def test_csrf_enforced(client):
    login(client)
    assert client.post('/reports/create',data={'patient_id':'1','transcript':'synthetic'}).status_code==400
    assert client.post('/logout').status_code==400


def test_hospital_scoping(client):
    login(client)
    token=token_for(client,'/reports/new')
    assert client.post('/reports/create',data={'_csrf':token,'patient_id':'999999','transcript':'synthetic'}).status_code==403


def test_admin_model_configuration_never_exposes_token(client,monkeypatch):
    monkeypatch.setenv('AWS_BEARER_TOKEN_BEDROCK','SECRET_SHOULD_NOT_LEAK')
    login(client,'admin@vaidya.demo','DemoAdmin!2026')
    response=client.get('/api/v1/admin/model-configuration')
    assert response.status_code==200
    assert response.json['credential_configured'] is True
    assert b'SECRET_SHOULD_NOT_LEAK' not in response.data
    page=client.get('/admin')
    assert page.status_code==200
    assert b'SECRET_SHOULD_NOT_LEAK' not in page.data
    assert b'LLM provider configuration' in page.data


def test_doctor_audio_to_approved_docx_end_to_end_mock_asr(client, monkeypatch):
    """True Flask + real LangGraph; only ASR engine is stubbed for deterministic CI."""
    import io
    import vaidya.multi_agent as multi
    from vaidya.audio import Transcription
    class FakeTranscriber:
        def transcribe(self, files, language=None):
            assert len(files)==1
            return Transcription(text='Synthetic appendix section shows inflammation.',
                segments=[{'note_index':0,'start':0.0,'end':1.0,'text':'Synthetic appendix section shows inflammation.','language':'en'}],
                detected_languages=['en'],model='stubbed-asr-for-integration-test')
    monkeypatch.setattr(multi,'transcriber',lambda:FakeTranscriber())
    login(client)
    csrf=token_for(client,'/reports/new')
    wav=b'RIFF'+(40).to_bytes(4,'little')+b'WAVEfmt '+b'\x00'*32
    res=client.post('/reports/create',data={
        'patient_id':'1','_csrf':csrf,'transcript':'', 'language_config':'en',
        'audio_notes':(io.BytesIO(wav),'synthetic.wav')
    },content_type='multipart/form-data',follow_redirects=False)
    assert res.status_code==302 and '/reports/' in res.location
    jid=res.location.split('/')[-1]
    meta=client.get(f'/api/v1/jobs/{jid}').json
    assert meta['audio_note_count']==1 and meta['status']=='draft_ready'
    trace=client.get(f'/api/v1/jobs/{jid}/graph').json['stages']
    assert any(x['stage']=='transcribe_voice_notes' for x in trace)
    assert any(x['stage']=='translate_voice_notes' for x in trace)
    review=client.get(res.location).data
    assert b'Synthetic appendix section shows inflammation.' in review
    doc=client.get(f'/reports/{jid}/download')
    assert doc.status_code==200 and doc.data[:2]==b'PK'


def test_admin_audited_skill_rollback(client):
    import app as app_module
    from vaidya.database import utcnow
    with app_module.DB.connect() as c:
        c.execute('INSERT INTO skills(version,content,learning_id,approved_by,created_at) VALUES(?,?,?,?,?)',
                  (2,'APPROVED: Add signature block',None,2,utcnow()))
    login(client,'admin@vaidya.demo','DemoAdmin!2026')
    csrf=token_for(client,'/admin')
    result=client.post('/admin/skills/rollback',data={'_csrf':csrf,'target_version':'1'},
                       follow_redirects=True)
    assert result.status_code==200
    latest=app_module.DB.query('SELECT version,content FROM skills ORDER BY version DESC LIMIT 1',one=True)
    assert latest['version']==3 and 'Baseline' in latest['content']
    audit=app_module.DB.query("SELECT action FROM audit_events WHERE action='rollback_skill'",one=True)
    assert audit
