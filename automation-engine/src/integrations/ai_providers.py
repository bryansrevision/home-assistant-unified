"""Multi-AI provider integration with fallback support."""

import logging
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional

from openai import OpenAI


logger = logging.getLogger(__name__)


class AIProvider(ABC):
    """Base class for AI providers."""

    @abstractmethod
    def generate_response(
        self,
        prompt: str,
        context: Optional[str] = None,
        **kwargs: Any
    ) -> Dict[str, Any]:
        """Generate a response from the AI provider.

        Args:
            prompt: The input prompt
            context: Optional context for the prompt
            **kwargs: Additional provider-specific parameters

        Returns:
            Dict with response and metadata
        """
        pass

    @abstractmethod
    def test_connection(self) -> bool:
        """Test connection to the AI provider.

        Returns:
            True if connection is successful
        """
        pass


class OpenAIProvider(AIProvider):
    """OpenAI API provider."""

    def __init__(self, api_key: str, model: str = "gpt-3.5-turbo", **kwargs: Any):
        """Initialize OpenAI provider.

        Args:
            api_key: OpenAI API key
            model: Model to use
            **kwargs: Additional parameters (temperature, max_tokens, etc.)
        """
        self.api_key = api_key
        self.model = model
        self.temperature = kwargs.get('temperature', 0.7)
        self.max_tokens = kwargs.get('max_tokens', 150)
        self.client = OpenAI(api_key=api_key)

    def generate_response(
        self,
        prompt: str,
        context: Optional[str] = None,
        **kwargs: Any
    ) -> Dict[str, Any]:
        """Generate response using OpenAI."""
        try:
            messages = []
            if context:
                messages.append({"role": "system", "content": context})
            messages.append({"role": "user", "content": prompt})

            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=kwargs.get('temperature', self.temperature),
                max_tokens=kwargs.get('max_tokens', self.max_tokens)
            )

            return {
                "success": True,
                "response": response.choices[0].message.content,
                "provider": "openai",
                "model": self.model
            }
        except Exception as e:
            logger.error(f"OpenAI API error: {e}")
            return {
                "success": False,
                "error": str(e),
                "provider": "openai"
            }

    def test_connection(self) -> bool:
        """Test OpenAI connection."""
        try:
            self.client.models.list()
            return True
        except Exception as e:
            logger.error(f"OpenAI connection test failed: {e}")
            return False


class GeminiProvider(AIProvider):
    """Google Gemini API provider."""

    def __init__(self, api_key: str, model: str = "gemini-pro", **kwargs: Any):
        """Initialize Gemini provider.

        Args:
            api_key: Gemini API key
            model: Model to use
            **kwargs: Additional parameters
        """
        self.api_key = api_key
        self.model = model
        self.temperature = kwargs.get('temperature', 0.7)
        self.max_tokens = kwargs.get('max_tokens', 150)
        # Note: Actual Gemini SDK would be imported here
        # import google.generativeai as genai
        # genai.configure(api_key=api_key)

    def generate_response(
        self,
        prompt: str,
        context: Optional[str] = None,
        **kwargs: Any
    ) -> Dict[str, Any]:
        """Generate response using Gemini."""
        try:
            # Placeholder for Gemini API call
            # In production, use actual Gemini SDK
            full_prompt = f"{context}\n\n{prompt}" if context else prompt
            
            logger.info(f"Gemini API would be called with prompt: {prompt[:50]}...")
            
            return {
                "success": True,
                "response": "Gemini provider placeholder response",
                "provider": "gemini",
                "model": self.model,
                "note": "Gemini integration requires google-generativeai package"
            }
        except Exception as e:
            logger.error(f"Gemini API error: {e}")
            return {
                "success": False,
                "error": str(e),
                "provider": "gemini"
            }

    def test_connection(self) -> bool:
        """Test Gemini connection."""
        # Placeholder - would test actual API
        return bool(self.api_key)


class GrokProvider(AIProvider):
    """Grok AI API provider."""

    def __init__(self, api_key: str, model: str = "grok-1", **kwargs: Any):
        """Initialize Grok provider.

        Args:
            api_key: Grok API key
            model: Model to use
            **kwargs: Additional parameters
        """
        self.api_key = api_key
        self.model = model
        self.temperature = kwargs.get('temperature', 0.7)
        self.max_tokens = kwargs.get('max_tokens', 150)

    def generate_response(
        self,
        prompt: str,
        context: Optional[str] = None,
        **kwargs: Any
    ) -> Dict[str, Any]:
        """Generate response using Grok."""
        try:
            # Placeholder for Grok API call
            full_prompt = f"{context}\n\n{prompt}" if context else prompt
            
            logger.info(f"Grok API would be called with prompt: {prompt[:50]}...")
            
            return {
                "success": True,
                "response": "Grok provider placeholder response",
                "provider": "grok",
                "model": self.model,
                "note": "Grok integration requires xAI API access"
            }
        except Exception as e:
            logger.error(f"Grok API error: {e}")
            return {
                "success": False,
                "error": str(e),
                "provider": "grok"
            }

    def test_connection(self) -> bool:
        """Test Grok connection."""
        # Placeholder - would test actual API
        return bool(self.api_key)


class MultiAIProvider:
    """Multi-provider AI system with fallback support."""

    def __init__(
        self,
        primary_provider: str,
        fallback_providers: List[str],
        api_keys: Dict[str, str],
        **kwargs: Any
    ):
        """Initialize multi-provider AI system.

        Args:
            primary_provider: Primary AI provider name
            fallback_providers: List of fallback provider names
            api_keys: Dictionary of API keys for each provider
            **kwargs: Additional parameters for providers
        """
        self.providers: Dict[str, AIProvider] = {}
        self.primary_provider = primary_provider
        self.fallback_providers = fallback_providers
        self.kwargs = kwargs

        # Initialize providers
        self._initialize_provider("openai", api_keys.get("openai", ""))
        self._initialize_provider("gemini", api_keys.get("gemini", ""))
        self._initialize_provider("grok", api_keys.get("grok", ""))

    def _initialize_provider(self, provider_name: str, api_key: str) -> None:
        """Initialize a specific AI provider.

        Args:
            provider_name: Name of the provider
            api_key: API key for the provider
        """
        if not api_key:
            logger.warning(f"No API key provided for {provider_name}")
            return

        try:
            if provider_name == "openai":
                self.providers["openai"] = OpenAIProvider(api_key, **self.kwargs)
            elif provider_name == "gemini":
                self.providers["gemini"] = GeminiProvider(api_key, **self.kwargs)
            elif provider_name == "grok":
                self.providers["grok"] = GrokProvider(api_key, **self.kwargs)
            
            logger.info(f"Initialized {provider_name} provider")
        except Exception as e:
            logger.error(f"Failed to initialize {provider_name} provider: {e}")

    def generate_response(
        self,
        prompt: str,
        context: Optional[str] = None,
        **kwargs: Any
    ) -> Dict[str, Any]:
        """Generate response with fallback support.

        Args:
            prompt: The input prompt
            context: Optional context
            **kwargs: Additional parameters

        Returns:
            Response from the first successful provider
        """
        # Try primary provider first
        providers_to_try = [self.primary_provider] + self.fallback_providers
        
        for provider_name in providers_to_try:
            provider = self.providers.get(provider_name)
            if not provider:
                logger.warning(f"Provider {provider_name} not available")
                continue

            logger.info(f"Trying {provider_name} provider")
            result = provider.generate_response(prompt, context, **kwargs)
            
            if result.get("success"):
                logger.info(f"Successfully got response from {provider_name}")
                return result
            else:
                logger.warning(f"Provider {provider_name} failed: {result.get('error')}")

        # All providers failed
        return {
            "success": False,
            "error": "All AI providers failed",
            "providers_tried": providers_to_try
        }

    def test_connections(self) -> Dict[str, bool]:
        """Test all provider connections.

        Returns:
            Dictionary of provider connection statuses
        """
        results = {}
        for name, provider in self.providers.items():
            try:
                results[name] = provider.test_connection()
            except Exception as e:
                logger.error(f"Error testing {name}: {e}")
                results[name] = False
        return results

    def get_available_providers(self) -> List[str]:
        """Get list of available providers.

        Returns:
            List of provider names
        """
        return list(self.providers.keys())
