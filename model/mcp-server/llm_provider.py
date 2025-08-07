"""
Dynamic LLM Provider Selection for RAG Doc Chain
Supports OpenAI GPT and Google Gemini models
"""

import os
from typing import Optional
from langchain_core.language_models.chat_models import BaseChatModel


def get_llm(provider: Optional[str] = None, model_name: Optional[str] = None, **kwargs) -> BaseChatModel:
    """
    Get LLM instance based on provider selection.
    
    Args:
        provider: LLM provider ("openai", "gemini"). If None, uses LLM_PROVIDER env var.
        model_name: Specific model name. If None, uses defaults.
        **kwargs: Additional arguments passed to the LLM constructor.
    
    Returns:
        BaseChatModel: Configured LLM instance
        
    Raises:
        ValueError: If provider is unsupported or required dependencies are missing
        ImportError: If required packages are not installed
    """
    provider = provider or os.getenv("LLM_PROVIDER", "openai")
    temperature = kwargs.pop("temperature", 0.2)
    
    if provider.lower() == "openai":
        return _get_openai_llm(model_name, temperature, **kwargs)
    
    elif provider.lower() == "gemini":
        return _get_gemini_llm(model_name, temperature, **kwargs)
    
    else:
        raise ValueError(f"Unsupported provider: {provider}. Supported: 'openai', 'gemini'")


def _get_openai_llm(model_name: Optional[str], temperature: float, **kwargs) -> BaseChatModel:
    """Get OpenAI GPT model."""
    try:
        from langchain_openai import ChatOpenAI
    except ImportError:
        raise ImportError("Please install langchain-openai: pip install langchain-openai")
    
    model = model_name or os.getenv("OPENAI_MODEL", "gpt-4")
    api_key = kwargs.pop("api_key", None) or os.getenv("OPENAI_API_KEY")
    
    if not api_key:
        raise ValueError("OPENAI_API_KEY environment variable is required for OpenAI provider")
    
    return ChatOpenAI(
        model=model,
        temperature=temperature,
        openai_api_key=api_key,
        **kwargs
    )


def _get_gemini_llm(model_name: Optional[str], temperature: float, **kwargs) -> BaseChatModel:
    """Get Google Gemini model."""
    try:
        from langchain_google_genai import ChatGoogleGenerativeAI
    except ImportError:
        raise ImportError("Please install langchain-google-genai: pip install langchain-google-genai")
    
    model = model_name or os.getenv("GEMINI_MODEL", "gemini-1.5-pro")
    api_key = kwargs.pop("google_api_key", None) or os.getenv("GOOGLE_API_KEY")
    
    if not api_key:
        raise ValueError("GOOGLE_API_KEY environment variable is required for Gemini provider")
    
    return ChatGoogleGenerativeAI(
        model=model,
        temperature=temperature,
        google_api_key=api_key,
        **kwargs
    )


def list_available_models() -> dict:
    """
    List available models for each provider.
    
    Returns:
        dict: Available models organized by provider
    """
    return {
        "openai": [
            "gpt-4",
            "gpt-4-turbo",
            "gpt-4o",
            "gpt-4o-mini",
            "gpt-3.5-turbo"
        ],
        "gemini": [
            "gemini-1.5-pro",
            "gemini-1.5-flash",
            "gemini-1.0-pro"
        ]
    }


def get_provider_info() -> dict:
    """
    Get information about each provider including costs and characteristics.
    
    Returns:
        dict: Provider information
    """
    return {
        "openai": {
            "description": "OpenAI GPT models - industry standard with excellent quality",
            "cost": "Medium to High ($3-60 per 1M tokens)",
            "speed": "Medium",
            "quality": "Excellent",
            "best_for": "Complex reasoning, general purpose",
            "requires_api_key": True
        },
        "gemini": {
            "description": "Google's Gemini models - cost-effective with large context",
            "cost": "Low to Medium ($0.35-21 per 1M tokens)",
            "speed": "Fast",
            "quality": "Excellent",
            "best_for": "Technical content, cost-sensitive applications",
            "requires_api_key": True
        }
    }


# Convenience functions for common configurations
def get_fast_llm(**kwargs) -> BaseChatModel:
    """Get a fast, cost-effective model (Gemini Flash or GPT-4o-mini)."""
    provider = os.getenv("LLM_PROVIDER", "openai")
    
    if provider == "gemini":
        return get_llm("gemini", "gemini-1.5-flash", **kwargs)
    elif provider == "openai":
        return get_llm("openai", "gpt-4o-mini", **kwargs)
    else:
        # Fallback to default model for the current provider
        return get_llm(provider, **kwargs)


def get_quality_llm(**kwargs) -> BaseChatModel:
    """Get a high-quality model (GPT-4 or Gemini Pro)."""
    provider = os.getenv("LLM_PROVIDER", "openai")
    
    if provider == "openai":
        return get_llm("openai", "gpt-4", **kwargs)
    elif provider == "gemini":
        return get_llm("gemini", "gemini-1.5-pro", **kwargs)
    else:
        # Fallback to default model for the current provider
        return get_llm(provider, **kwargs)


if __name__ == "__main__":
    # Demo usage
    print("🤖 LLM Provider Demo\n")
    
    # Show available providers
    print("📋 Available Providers:")
    for provider, info in get_provider_info().items():
        print(f"  • {provider.upper()}: {info['description']}")
    
    print("\n🔧 Available Models:")
    for provider, models in list_available_models().items():
        print(f"  • {provider.upper()}: {', '.join(models[:3])}...")
    
    # Example usage
    print("\n💡 Example Usage:")
    print("  from llm_provider import get_llm")
    print("  llm = get_llm('gemini')  # Uses default Gemini model")
    print("  llm = get_llm('openai', 'gpt-4o')  # Specific OpenAI model")
    print("  llm = get_fast_llm()  # Fast model (Gemini Flash or GPT-4o-mini)")
    print("  llm = get_quality_llm()  # Quality model (GPT-4 or Gemini Pro)")
