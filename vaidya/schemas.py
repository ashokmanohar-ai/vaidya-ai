"""Typed, bounded Bedrock extraction contract. Schema correctness is not clinical correctness."""
from __future__ import annotations
from pydantic import BaseModel, ConfigDict, Field, field_validator

class ClinicalFinding(BaseModel):
    model_config=ConfigDict(extra='forbid',str_strip_whitespace=True)
    text: str=Field(min_length=1,max_length=1200)

class FormattingInstruction(BaseModel):
    model_config=ConfigDict(extra='forbid',str_strip_whitespace=True)
    instruction: str=Field(min_length=1,max_length=300)

class ReportExtractionSchema(BaseModel):
    model_config=ConfigDict(extra='forbid')
    findings:list[ClinicalFinding]=Field(max_length=50)
    instructions:list[FormattingInstruction]=Field(max_length=30)
    review_flags:list[str]=Field(max_length=20)

    @field_validator('review_flags')
    @classmethod
    def validate_flags(cls,values):
        if not all(isinstance(v,str) and len(v.strip())<=300 for v in values):
            raise ValueError('Review flags must be strings up to 300 characters')
        return values
