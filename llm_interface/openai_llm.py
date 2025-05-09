import openai
from typing import Dict, Any
from .base_llm import BaseLLM

class OpenAILLM(BaseLLM):
    """
    LLM interface implementation for OpenAI's GPT models.
    """
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize the OpenAI LLM interface.
        
        Args:
            config: Configuration dictionary containing:
                - api_key: OpenAI API key.
                - model_name: The OpenAI model to use (e.g., "gpt-3.5-turbo", "text-davinci-003").
                - default_max_tokens: Default maximum tokens for generation.
                - default_temperature: Default temperature for generation.
        """
        super().__init__(config)
        if not self.config.get("api_key"):
            raise ValueError("OpenAI API key not found in config.")
        openai.api_key = self.config["api_key"]
        self.model_name = self.config.get("model_name", "gpt-3.5-turbo")
        self.default_max_tokens = self.config.get("default_max_tokens", 1024)
        self.default_temperature = self.config.get("default_temperature", 0.7)

    def generate(self, prompt: str, **kwargs) -> str:
        """
        Generate text using the configured OpenAI model.

        Args:
            prompt: The input prompt string.
            **kwargs: Override default parameters like 'max_tokens', 'temperature'.
                      Can also include other valid OpenAI API parameters.

        Returns:
            The generated text string from the LLM.
        """
        max_tokens = kwargs.get("max_tokens", self.default_max_tokens)
        temperature = kwargs.get("temperature", self.default_temperature)
        
        try:
            # For chat models like gpt-3.5-turbo or gpt-4
            if "chat" in self.model_name or "gpt-3.5-turbo" in self.model_name or "gpt-4" in self.model_name:
                response = openai.ChatCompletion.create(
                    model=self.model_name,
                    messages=[{"role": "user", "content": prompt}],
                    temperature=temperature,
                    max_tokens=max_tokens,
                    **{k: v for k, v in kwargs.items() if k not in ["max_tokens", "temperature"]}
                )
                return response.choices[0].message.content.strip()
            else: # For older completion models like text-davinci-003
                response = openai.Completion.create(
                    model=self.model_name,
                    prompt=prompt,
                    temperature=temperature,
                    max_tokens=max_tokens,
                    **{k: v for k, v in kwargs.items() if k not in ["max_tokens", "temperature"]}
                )
                return response.choices[0].text.strip()
        except Exception as e:
            print(f"[OpenAILLM] Error during API call: {e}")
            return f"Error generating response: {e}"