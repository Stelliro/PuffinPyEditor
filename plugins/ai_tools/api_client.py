# PuffinPyEditor/plugins/ai_tools/api_client.py
import requests
import json
from typing import Dict, Tuple
from utils.logger import log


class ApiClient:
    """A client to interact with various AI model APIs."""

    PROVIDER_CONFIG = {
        "OpenAI": {
            "endpoint": "https://api.openai.com/v1/chat/completions",
            "models": ["gpt-4o", "gpt-4-turbo", "gpt-3.5-turbo"],
        }
        # Other providers like Anthropic or Gemini could be added here
    }

    def __init__(self, settings_manager):
        self.settings_manager = settings_manager

    def get_api_key(self, provider: str) -> str | None:
        """Retrieves an API key for a given provider from settings."""
        api_keys = self.settings_manager.get("api_keys", {})
        return api_keys.get(provider)

    def send_request(
        self, provider: str, model: str, system_prompt: str, user_prompt: str
    ) -> Tuple[bool, str]:
        """
        Sends a request to the specified AI provider.

        Returns a tuple: (success: bool, response_content: str)
        """
        api_key = self.get_api_key(provider)
        if not api_key:
            msg = (
                f"API Key for {provider} not found. Please configure it in "
                "the settings."
            )
            return False, msg

        config = self.PROVIDER_CONFIG.get(provider)
        if not config:
            return False, f"Configuration for provider '{provider}' not found."

        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        }

        payload = {
            "model": model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            "max_tokens": 4096,
        }

        try:
            log.info(f"Sending request to {provider} model {model}...")
            response = requests.post(
                config["endpoint"],
                headers=headers,
                data=json.dumps(payload),
                timeout=120  # 2-minute timeout
            )
            response.raise_for_status()

            data = response.json()
            content = data['choices'][0]['message']['content']
            log.info("Successfully received response from AI.")
            return True, content.strip()

        except requests.exceptions.RequestException as e:
            error_message = f"API request failed: {e}"
            if e.response is not None:
                error_message += f"\nResponse: {e.response.text}"
            log.error(error_message)
            return False, error_message
        except (KeyError, IndexError) as e:
            error_message = f"Failed to parse AI response: {e}"
            log.error(f"{error_message}\nFull Response: {response.text}")
            return False, error_message
        except Exception as e:
            error_message = f"An unexpected error occurred: {e}"
            log.error(error_message)
            return False, error_message