"""Bedrock smoke-test safety gates; no test executes a real AWS request."""
from __future__ import annotations

import sys
from types import SimpleNamespace

from botocore.exceptions import ClientError

from scripts import bedrock_smoke_test as smoke


def _settings(**changes):
    values = {
        "region": "ap-south-1",
        "model": "in.openai.gpt-5.6-terra",
        "provider": "bedrock",
        "credential_configured": False,
        "remote_opt_in": True,
        "structured_output": False,
        "allowed_models": ["in.openai.gpt-5.6-terra"],
    }
    values.update(changes)
    return values


def _no_network(*args, **kwargs):
    raise AssertionError("Bedrock provider must not be invoked")


def test_no_cost_confirmation_never_calls_bedrock(monkeypatch, capsys):
    monkeypatch.setattr(smoke, "bedrock_settings", lambda: _settings())
    monkeypatch.setattr(smoke, "BedrockConverseProvider", _no_network)
    monkeypatch.setattr(sys, "argv", ["bedrock_smoke_test.py"])
    assert smoke.main() == 2
    assert "No request sent" in capsys.readouterr().out


def test_missing_opt_in_never_calls_bedrock(monkeypatch, capsys):
    monkeypatch.setattr(smoke, "bedrock_settings", lambda: _settings(remote_opt_in=False))
    monkeypatch.setattr(smoke, "BedrockConverseProvider", _no_network)
    monkeypatch.setattr(sys, "argv", ["bedrock_smoke_test.py", "--confirm-cost"])
    assert smoke.main() == 2
    assert "No request sent" in capsys.readouterr().out


def test_model_not_allowlisted_never_calls_bedrock(monkeypatch, capsys):
    monkeypatch.setattr(smoke, "bedrock_settings", lambda: _settings(model="invalid-model"))
    monkeypatch.setattr(smoke, "BedrockConverseProvider", _no_network)
    monkeypatch.setattr(sys, "argv", ["bedrock_smoke_test.py", "--confirm-cost"])
    assert smoke.main() == 2
    assert "not listed" in capsys.readouterr().out


def test_explicit_approval_passes_only_fixed_synthetic_text(monkeypatch, capsys):
    monkeypatch.setattr(smoke, "bedrock_settings", lambda: _settings())
    monkeypatch.setattr(sys, "argv", ["bedrock_smoke_test.py", "--confirm-cost"])
    sent = []

    class FakeProvider:
        def extract(self, text):
            sent.append(text)
            return SimpleNamespace(provider="mock", model="synthetic", latency_ms=1,
                                   usage={"inputTokens": 1}, findings=[], instructions=[],
                                   review_flags=["Human review required"])

    monkeypatch.setattr(smoke, "BedrockConverseProvider", FakeProvider)
    assert smoke.main() == 0
    assert sent == [smoke.SYNTHETIC_TEXT]
    assert "PASS:" in capsys.readouterr().out


def test_boto3_service_errors_cannot_leak_message(capsys):
    secret = "SECRET_FROM_SERVICE_NOT_FOR_LOGS"
    error = ClientError({"Error": {"Code": "ValidationException", "Message": secret},
                         "ResponseMetadata": {"HTTPStatusCode": 400}}, "Converse")
    smoke._diagnose(error)
    output = capsys.readouterr().out
    assert secret not in output
    assert "ValidationException" in output
    assert "HTTP status: 400" in output


def test_unknown_exception_redacts_message(capsys):
    smoke._diagnose(RuntimeError("PRIVATE_DICTATION_NOT_FOR_LOGS"))
    output = capsys.readouterr().out
    assert "PRIVATE_DICTATION_NOT_FOR_LOGS" not in output
    assert "UNCLASSIFIED" in output


def test_schema_path_and_error_code_redaction():
    assert smoke._safe_schema_location(("untrusted-field", 0, "text")) == "<unexpected-field>[0].text"
    assert smoke._safe_code("AccessDeniedException") == "AccessDeniedException"
    assert smoke._safe_code("error\nsecret") == "<unavailable>"
