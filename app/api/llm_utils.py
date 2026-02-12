"""Shared LLM utility functions for Ollama integration."""

import os
import re
import json
import hashlib
from flask import current_app


def get_model():
    """Get the configured LLM model name."""
    try:
        return current_app.config.get('LLM_MODEL', 'phi3')
    except RuntimeError:
        return os.environ.get('LEARNQUEST_MODEL', 'phi3')


def load_prompt(prompt_file, **kwargs):
    """Load a system prompt template and fill in variables."""
    prompts_dir = current_app.config['PROMPTS_DIR']
    filepath = os.path.join(prompts_dir, prompt_file)
    if not os.path.exists(filepath):
        return "You are a friendly and helpful tutor for K-12 students."
    with open(filepath, 'r') as f:
        template = f.read()
    for key, value in kwargs.items():
        template = template.replace('{' + key + '}', str(value))
    return template


def call_ollama(messages, model=None, temperature=0.7, max_tokens=500, stream=False):
    if model is None:
        model = get_model()
    """Call Ollama API for chat completion."""
    import requests
    try:
        resp = requests.post(
            'http://localhost:11434/api/chat',
            json={
                'model': model,
                'messages': messages,
                'stream': stream,
                'options': {
                    'temperature': temperature,
                    'num_predict': max_tokens,
                }
            },
            stream=stream,
            timeout=120
        )
        if stream:
            return resp
        data = resp.json()
        return data.get('message', {}).get('content', '')
    except Exception as e:
        return f"I'm having trouble thinking right now. Try again in a moment! (Error: {str(e)[:100]})"


def call_ollama_streaming(messages, model=None, temperature=0.7, max_tokens=500):
    if model is None:
        model = get_model()
    """Call Ollama and return a streaming response object."""
    return call_ollama(messages, model=model, temperature=temperature,
                       max_tokens=max_tokens, stream=True)


def parse_json_response(text):
    """Robustly extract JSON from LLM output (handles markdown code blocks, etc.)."""
    if not text:
        return None

    # Try to find JSON in markdown code blocks
    code_block = re.search(r'```(?:json)?\s*\n?([\s\S]*?)\n?```', text)
    if code_block:
        text = code_block.group(1).strip()

    # Try to find JSON array or object
    json_match = re.search(r'(\[[\s\S]*\]|\{[\s\S]*\})', text)
    if json_match:
        raw = json_match.group(1)
    else:
        raw = text.strip()

    # Clean up common LLM JSON issues
    raw = re.sub(r',\s*([}\]])', r'\1', raw)  # trailing commas
    raw = re.sub(r"'", '"', raw)  # single to double quotes (risky but common)

    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        return None


def get_cached_response(db, cache_key):
    """Check for cached LLM response."""
    try:
        row = db.execute('SELECT response FROM llm_cache WHERE cache_key = ?', (cache_key,)).fetchone()
        return row['response'] if row else None
    except Exception:
        return None


def cache_response(db, cache_key, response):
    """Cache an LLM response."""
    try:
        db.execute(
            'INSERT OR REPLACE INTO llm_cache (cache_key, response) VALUES (?, ?)',
            (cache_key, response)
        )
        db.commit()
    except Exception:
        pass


def make_cache_key(*parts):
    """Create a deterministic cache key from parts."""
    raw = json.dumps(parts, sort_keys=True)
    return hashlib.md5(raw.encode()).hexdigest()
