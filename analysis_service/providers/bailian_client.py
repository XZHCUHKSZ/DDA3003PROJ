from __future__ import annotations

import json
import os
import urllib.request
from typing import Any


class BailianClient:
    def __init__(
        self,
        *,
        api_key: str = '',
        base_url: str = '',
        model: str = '',
    ) -> None:
        env_key = os.getenv('DASHSCOPE_API_KEY', '').strip()
        env_base = os.getenv('BAILIAN_BASE_URL', 'https://dashscope.aliyuncs.com/compatible-mode/v1').rstrip('/')
        env_model = os.getenv('BAILIAN_MODEL', 'qwen-plus')

        self.api_key = (api_key or env_key).strip()
        self.base_url = (base_url or env_base).rstrip('/')
        self.model = (model or env_model).strip() or 'qwen-plus'

    @property
    def enabled(self) -> bool:
        return bool(self.api_key)

    def chat_json(self, system_prompt: str, user_prompt: str, timeout: int = 60) -> dict[str, Any]:
        if not self.enabled:
            raise RuntimeError('DASHSCOPE_API_KEY is not set')

        payload = {
            'model': self.model,
            'temperature': 0.2,
            'messages': [
                {'role': 'system', 'content': system_prompt},
                {'role': 'user', 'content': user_prompt},
            ],
            'response_format': {'type': 'json_object'},
        }

        req = urllib.request.Request(
            url=f'{self.base_url}/chat/completions',
            data=json.dumps(payload).encode('utf-8'),
            headers={
                'Authorization': f'Bearer {self.api_key}',
                'Content-Type': 'application/json',
            },
            method='POST',
        )

        with urllib.request.urlopen(req, timeout=timeout) as resp:
            body = resp.read().decode('utf-8')
            data = json.loads(body)

        content = data['choices'][0]['message']['content']
        if isinstance(content, str):
            return json.loads(content)
        if isinstance(content, dict):
            return content
        raise RuntimeError('Unexpected content format from Bailian response')
