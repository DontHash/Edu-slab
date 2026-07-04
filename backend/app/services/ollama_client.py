"""
HTTP client for local Ollama inference (RTX 2050 / offline evaluation).
"""
import json
from typing import Any, Dict, List, Optional

import requests

from app.core.config import settings


class OllamaClient:
    def __init__(
        self,
        base_url: str | None = None,
        model: str | None = None,
        timeout: int = 180,
    ):
        self.base_url = (base_url or settings.OLLAMA_BASE_URL).rstrip("/")
        self.model = model or settings.OLLAMA_MODEL
        self.timeout = timeout

    def is_available(self) -> bool:
        try:
            resp = requests.get(f"{self.base_url}/api/tags", timeout=5)
            return resp.status_code == 200
        except requests.RequestException:
            return False

    def list_models(self) -> List[str]:
        try:
            resp = requests.get(f"{self.base_url}/api/tags", timeout=5)
            resp.raise_for_status()
            return [m.get("name", "") for m in resp.json().get("models", [])]
        except requests.RequestException:
            return []

    def is_model_ready(self, model: Optional[str] = None) -> bool:
        """True when Ollama is up and the configured model is installed."""
        if not self.is_available():
            return False
        target = (model or self.model).split(":")[0]
        installed = self.list_models()
        return any(
            m == (model or self.model)
            or m.split(":")[0] == target
            or (model or self.model) in m
            for m in installed
        )

    def readiness_message(self) -> str:
        if not self.is_available():
            return (
                "Ollama is not running. Start the Ollama app or run: ollama serve"
            )
        if not self.is_model_ready():
            return (
                f"Model '{self.model}' is not installed. Run: "
                f"ollama pull {self.model}"
            )
        return "ready"

    def chat_json(
        self,
        system: str,
        user: str,
        model: Optional[str] = None,
        temperature: float = 0.2,
    ) -> Dict[str, Any]:
        payload = {
            "model": model or self.model,
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
            "stream": False,
            "format": "json",
            "options": {"temperature": temperature},
        }
        resp = requests.post(
            f"{self.base_url}/api/chat",
            json=payload,
            timeout=self.timeout,
        )
        resp.raise_for_status()
        content = resp.json().get("message", {}).get("content", "{}")
        return json.loads(content)
