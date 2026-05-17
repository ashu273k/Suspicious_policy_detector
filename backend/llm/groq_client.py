"""
Groq Client — OpenAI-compatible HTTP client with header-aware throttling.
"""

import json
import re
import threading
import time

import requests

from config import GROQ_API_KEY, GROQ_MODEL


_RATE_LIMIT_LOCK = threading.Lock()
_RATE_LIMIT_STATE = {
    "remaining_tokens": None,
    "remaining_requests": None,
    "reset_tokens": None,
    "reset_requests": None,
    "updated_at": 0.0,
}


def _get_headers():
    if not GROQ_API_KEY:
        raise ValueError("GROQ_API_KEY not set. Get a key at https://console.groq.com")
    return {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json",
    }


def _estimate_tokens(text: str) -> int:
    return max(1, len(text) // 4)


def _parse_duration_seconds(value: str | None) -> float | None:
    if not value:
        return None
    value = value.strip()
    if not value:
        return None

    if value.isdigit():
        return float(value)

    total = 0.0
    matched = False
    for amount, unit in re.findall(r"(\d+(?:\.\d+)?)([smh])", value):
        matched = True
        number = float(amount)
        if unit == "s":
            total += number
        elif unit == "m":
            total += number * 60
        elif unit == "h":
            total += number * 3600

    if matched:
        return total

    try:
        return float(value)
    except ValueError:
        return None


def _update_rate_limit_state(headers: dict) -> None:
    with _RATE_LIMIT_LOCK:
        remaining_tokens = headers.get("x-ratelimit-remaining-tokens")
        remaining_requests = headers.get("x-ratelimit-remaining-requests")
        reset_tokens = headers.get("x-ratelimit-reset-tokens")
        reset_requests = headers.get("x-ratelimit-reset-requests")

        _RATE_LIMIT_STATE["remaining_tokens"] = int(remaining_tokens) if remaining_tokens and remaining_tokens.isdigit() else None
        _RATE_LIMIT_STATE["remaining_requests"] = int(remaining_requests) if remaining_requests and remaining_requests.isdigit() else None
        _RATE_LIMIT_STATE["reset_tokens"] = _parse_duration_seconds(reset_tokens)
        _RATE_LIMIT_STATE["reset_requests"] = _parse_duration_seconds(reset_requests)
        _RATE_LIMIT_STATE["updated_at"] = time.time()


def _sleep_if_needed(estimated_tokens: int) -> None:
    with _RATE_LIMIT_LOCK:
        remaining_tokens = _RATE_LIMIT_STATE["remaining_tokens"]
        reset_tokens = _RATE_LIMIT_STATE["reset_tokens"]
        remaining_requests = _RATE_LIMIT_STATE["remaining_requests"]
        reset_requests = _RATE_LIMIT_STATE["reset_requests"]

    waits = []
    if remaining_tokens is not None and estimated_tokens >= remaining_tokens and reset_tokens is not None:
        waits.append(reset_tokens)
    if remaining_requests is not None and remaining_requests <= 0 and reset_requests is not None:
        waits.append(reset_requests)

    if waits:
        wait = max(1.0, max(waits))
        print(f"⚠️ Groq budget low; waiting {wait:.1f}s before next request")
        time.sleep(wait)


def call_groq(
    prompt: str,
    temperature: float = 0.1,
    max_retries: int = 4,
    system_message: str = "",
    doc_token_count: int = 0,
) -> str:
    """Call Groq's OpenAI-compatible chat completions endpoint.

    Uses response headers to throttle before the next request when the last
    observed rate-limit state indicates the budget is nearly exhausted.
    """
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = _get_headers()

    messages = []
    if system_message:
        messages.append({"role": "system", "content": system_message})
    messages.append({"role": "user", "content": prompt})

    estimated_tokens = max(doc_token_count, _estimate_tokens(prompt)) + 1024
    payload = {
        "model": GROQ_MODEL,
        "messages": messages,
        "temperature": temperature,
        "max_tokens": 2048,
    }

    for attempt in range(max_retries):
        _sleep_if_needed(estimated_tokens)

        try:
            resp = requests.post(url, headers=headers, data=json.dumps(payload), timeout=60)

            if resp.status_code == 200:
                _update_rate_limit_state(resp.headers)
                try:
                    data = resp.json()
                    return data["choices"][0]["message"]["content"]
                except Exception as e:
                    raise RuntimeError(f"Groq returned invalid JSON: {e} - raw: {resp.text}")

            if resp.status_code == 429:
                _update_rate_limit_state(resp.headers)
                retry_after = _parse_duration_seconds(resp.headers.get("retry-after"))
                if retry_after is None:
                    try:
                        body = resp.json()
                        retry_after = _parse_duration_seconds(
                            str(body.get("retry_after") or body.get("retry_after_seconds") or "")
                        )
                    except Exception:
                        retry_after = None

                if retry_after is None:
                    retry_after = min(60.0, 2 ** attempt)

                print(
                    f"⚠️ Groq rate limit hit; attempt {attempt + 1}/{max_retries}; waiting {retry_after:.1f}s before retry"
                )
                time.sleep(retry_after)
                continue

            if resp.status_code in (500, 502, 503, 504):
                wait = min(30.0, 2 ** attempt)
                print(f"⚠️ Groq {resp.status_code}; retrying in {wait:.1f}s")
                time.sleep(wait)
                continue

            raise RuntimeError(f"Groq API error {resp.status_code}: {resp.text}")

        except requests.RequestException as e:
            if attempt < max_retries - 1:
                wait = min(30.0, 2 ** attempt)
                print(f"⚠️ Network error calling Groq: {e}; retrying in {wait:.1f}s")
                time.sleep(wait)
                continue
            raise RuntimeError(f"Groq request failed after {max_retries} attempts: {e}")

    raise RuntimeError(f"Groq API failed after {max_retries} attempts")