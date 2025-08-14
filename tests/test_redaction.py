from ai.core.llm import build_redactor
from ai.core.config import Config, DEFAULT_CONFIG

def test_redaction():
    cfg = Config(dict(DEFAULT_CONFIG))
    redactor = build_redactor(cfg)
    text = 'My api-key: ABC123 should hide. Passport 999999'
    out = redactor(text)
    assert '[REDACTED]' in out
