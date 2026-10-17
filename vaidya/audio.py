"""Local CPU automatic speech recognition with explicit dependencies and model provenance.

This service performs speech transcription only. It does not diagnose. Models may
require a download the first time they are run; operators must arrange/approve it.
"""
from __future__ import annotations
from dataclasses import dataclass, field
from pathlib import Path
import os

@dataclass
class Transcription:
    text: str
    segments: list[dict] = field(default_factory=list)
    detected_languages: list[str] = field(default_factory=list)
    provider: str = 'faster-whisper'
    model: str = ''

class FasterWhisperTranscriber:
    def __init__(self, model=None, engine=None):
        self.model_name=model or os.getenv('WHISPER_MODEL_PATH') or os.getenv('WHISPER_MODEL_SIZE','base')
        self.engine=engine

    def _engine(self):
        if self.engine is None:
            try:
                from faster_whisper import WhisperModel
            except ImportError as exc:
                raise RuntimeError('Install requirements-audio.txt for audio transcription. No simulated ASR fallback.') from exc
            self.engine=WhisperModel(self.model_name,device='cpu',compute_type='int8',cpu_threads=min(4,os.cpu_count() or 2))
        return self.engine

    def transcribe(self, files:list[str], language:str|None=None)->Transcription:
        if not files or len(files)>5:raise ValueError('Between 1 and 5 voice notes required')
        segs=[]; languages=[]; pieces=[]
        for i, name in enumerate(files):
            path=Path(name)
            if not path.is_file():raise FileNotFoundError('Uploaded voice note not found')
            # Keep auto detection for genuine Tamil-English mixed speech; the ASR
            # language selection is exposed for repeatable testing only.
            result, info=self._engine().transcribe(str(path),language=language,beam_size=3,
                vad_filter=True,condition_on_previous_text=False)
            lang=getattr(info,'language','und')
            languages.append(lang)
            for segment in result:
                text=segment.text.strip()
                if text:
                    segs.append({'note_index':i,'start':round(float(segment.start),2),
                                 'end':round(float(segment.end),2),'text':text,'language':lang})
                    pieces.append(text)
        return Transcription(text=' '.join(pieces),segments=segs,
                             detected_languages=languages,model=self.model_name)


def transcriber():
    kind=os.getenv('ASR_PROVIDER','faster-whisper').strip().lower()
    if kind=='faster-whisper':return FasterWhisperTranscriber()
    raise ValueError('Unsupported ASR_PROVIDER. Supported: faster-whisper')
