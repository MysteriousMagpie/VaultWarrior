from __future__ import annotations
import os
import re
from typing import Iterable, Callable
from openai import OpenAI  # type: ignore
from .config import Config

Redactor = Callable[[str], str]


def build_redactor(cfg: Config) -> Redactor:
    patterns = [re.compile(p) for p in cfg.data.get('privacy', {}).get('redact', [])]
    def redact(text: str) -> str:
        for pat in patterns:
            text = pat.sub('[REDACTED]', text)
        return text
    return redact


def stream_completion(cfg: Config, prompt: str) -> Iterable[str]:
    provider = cfg.data['provider']
    if provider['type'] != 'openai':  # future extension point
        raise ValueError('Unsupported provider type')
    api_key = os.environ.get(provider['api_key_env'])
    if not api_key:
        raise EnvironmentError(f"Missing API key env {provider['api_key_env']}")
    client = OpenAI(api_key=api_key)
    model = provider['model']
    # Using responses streaming API (placeholder). Actual call may differ per openai sdk version.
    stream = client.chat.completions.create(model=model, messages=[{"role": "user", "content": prompt}], stream=True)
    for chunk in stream:
        delta = getattr(chunk.choices[0].delta, 'content', None)  # type: ignore
        if delta:
            yield delta
