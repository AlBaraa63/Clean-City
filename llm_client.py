"""
LLM Client Abstraction Layer

Provides unified interface to multiple LLM providers (Anthropic, OpenAI, Google Gemini).
Includes offline fallback mode for demos without API keys.

Configuration via environment variables:
- LLM_PROVIDER: "anthropic" | "openai" | "gemini" | "offline"
- ANTHROPIC_API_KEY
- OPENAI_API_KEY
- GEMINI_API_KEY
"""

import os
from typing import Optional
from dotenv import load_dotenv

load_dotenv()


class LLMClient:
    """Unified LLM client with multi-provider support and offline mode."""
    
    def __init__(self):
        self.provider = os.getenv("LLM_PROVIDER", "offline").lower()
        self._client = None
        self._initialize_client()
    
    def _initialize_client(self):
        """Initialize the appropriate LLM client based on provider setting."""
        if self.provider == "anthropic":
            api_key = os.getenv("ANTHROPIC_API_KEY")
            if api_key:
                try:
                    import anthropic
                    self._client = anthropic.Anthropic(api_key=api_key)
                    print("✓ Anthropic client initialized")
                except ImportError:
                    print("⚠ Anthropic package not installed, falling back to offline mode")
                    self.provider = "offline"
            else:
                print("⚠ ANTHROPIC_API_KEY not set, using offline mode")
                self.provider = "offline"
        
        elif self.provider == "openai":
            api_key = os.getenv("OPENAI_API_KEY")
            if api_key:
                try:
                    import openai
                    self._client = openai.OpenAI(api_key=api_key)
                    print("✓ OpenAI client initialized")
                except ImportError:
                    print("⚠ OpenAI package not installed, falling back to offline mode")
                    self.provider = "offline"
            else:
                print("⚠ OPENAI_API_KEY not set, using offline mode")
                self.provider = "offline"
        
        elif self.provider == "gemini":
            api_key = os.getenv("GEMINI_API_KEY")
            if api_key:
                try:
                    import google.generativeai as genai
                    genai.configure(api_key=api_key)
                    self._client = genai.GenerativeModel('gemini-pro')
                    print("✓ Gemini client initialized")
                except ImportError:
                    print("⚠ Google GenAI package not installed, falling back to offline mode")
                    self.provider = "offline"
            else:
                print("⚠ GEMINI_API_KEY not set, using offline mode")
                self.provider = "offline"
        
        else:
            print("ℹ Running in offline mode (mock responses)")
            self.provider = "offline"
    
    def generate_text(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        max_tokens: int = 1024,
        temperature: float = 0.7
    ) -> str:
        """
        Generate text completion from the configured LLM.
        
        Args:
            prompt: User prompt/query
            system_prompt: Optional system instructions
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature (0-1)
            
        Returns:
            Generated text response
        """
        if self.provider == "offline":
            return self._offline_response(prompt)
        
        try:
            if self.provider == "anthropic":
                return self._anthropic_generate(prompt, system_prompt, max_tokens, temperature)
            elif self.provider == "openai":
                return self._openai_generate(prompt, system_prompt, max_tokens, temperature)
            elif self.provider == "gemini":
                return self._gemini_generate(prompt, system_prompt, max_tokens, temperature)
        except Exception as e:
            print(f"⚠ LLM API error: {e}, falling back to offline mode")
            return self._offline_response(prompt)
        
        return self._offline_response(prompt)
    
    def _anthropic_generate(self, prompt: str, system_prompt: Optional[str], max_tokens: int, temperature: float) -> str:
        """Generate using Anthropic Claude."""
        messages = [{"role": "user", "content": prompt}]
        
        kwargs = {
            "model": "claude-3-5-sonnet-20241022",
            "max_tokens": max_tokens,
            "temperature": temperature,
            "messages": messages
        }
        
        if system_prompt:
            kwargs["system"] = system_prompt
        
        response = self._client.messages.create(**kwargs)
        return response.content[0].text
    
    def _openai_generate(self, prompt: str, system_prompt: Optional[str], max_tokens: int, temperature: float) -> str:
        """Generate using OpenAI GPT."""
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        
        response = self._client.chat.completions.create(
            model="gpt-4o",
            messages=messages,
            max_tokens=max_tokens,
            temperature=temperature
        )
        return response.choices[0].message.content
    
    def _gemini_generate(self, prompt: str, system_prompt: Optional[str], max_tokens: int, temperature: float) -> str:
        """Generate using Google Gemini."""
        full_prompt = prompt
        if system_prompt:
            full_prompt = f"{system_prompt}\n\n{prompt}"
        
        response = self._client.generate_content(
            full_prompt,
            generation_config={
                "max_output_tokens": max_tokens,
                "temperature": temperature
            }
        )
        return response.text
    
    def _offline_response(self, prompt: str) -> str:
        """Generate mock responses for offline/demo mode."""
        prompt_lower = prompt.lower()
        
        # Pattern matching for common requests
        if "cleanup" in prompt_lower or "plan" in prompt_lower:
            return """Based on the detected trash, here's a recommended cleanup plan:

**Severity Level**: Medium

**Recommended Actions**:
- Deploy 2-3 volunteers with standard cleanup equipment
- Estimated time: 45-60 minutes
- Bring 3-4 heavy-duty trash bags
- Consider gloves and grabber tools for safety

**Environmental Impact**: Moderate littering with potential harm to local wildlife if not addressed.

**Urgency**: Should be cleaned within 1-2 days to prevent accumulation."""
        
        elif "report" in prompt_lower:
            return """**Trash Cleanup Report**

Location: [User-specified location]
Date: [Current date]

We have identified significant litter accumulation requiring attention. The area contains multiple pieces of trash including plastic bottles, food wrappers, and other waste materials.

Recommended immediate action by city services to maintain public health and environmental standards.

Contact: [Your community group]"""
        
        elif "severity" in prompt_lower or "analyze" in prompt_lower:
            return "Based on the number and type of trash items detected, this appears to be a **medium severity** situation requiring attention within 1-2 days."
        
        else:
            return """I've analyzed the image and detected several trash items. The situation requires moderate attention with a cleanup effort estimated at 2-3 volunteers for about 45-60 minutes. This will help maintain the cleanliness and environmental health of the area."""


# Global singleton instance
_llm_client: Optional[LLMClient] = None


def get_llm_client() -> LLMClient:
    """Get or create the global LLM client instance."""
    global _llm_client
    if _llm_client is None:
        _llm_client = LLMClient()
    return _llm_client


def generate_text(prompt: str, system_prompt: Optional[str] = None, **kwargs) -> str:
    """Convenience function for text generation."""
    client = get_llm_client()
    return client.generate_text(prompt, system_prompt, **kwargs)
