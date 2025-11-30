#!/usr/bin/env python3
"""
Unified API Clients for all model providers
Handles real API calls with error handling and retry logic
"""

import os
import json
import time
import asyncio
from typing import Dict, List, Optional, Any, Union, AsyncIterator
import aiohttp
import requests
from tenacity import retry, stop_after_attempt, wait_exponential
import logging

from .types import APIResponse

logger = logging.getLogger(__name__)

class BaseAPIClient:
    """Base class for all API clients"""
    
    def __init__(self, api_key: str, base_url: str):
        self.api_key = api_key
        self.base_url = base_url
        self.session = None
        
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
    async def _make_request(self, 
                           method: str, 
                           endpoint: str, 
                           headers: Dict, 
                           payload: Dict) -> Dict:
        """Make API request with retry logic"""
        if not self.session:
            self.session = aiohttp.ClientSession()
            
        url = f"{self.base_url}/{endpoint}"
        start_time = time.time()
        
        try:
            async with self.session.request(method, url, headers=headers, json=payload) as response:
                latency_ms = int((time.time() - start_time) * 1000)
                
                if response.status != 200:
                    error_text = await response.text()
                    raise Exception(f"API Error {response.status}: {error_text}")
                
                data = await response.json()
                return data, latency_ms
                
        except Exception as e:
            logger.error(f"Request failed: {e}")
            raise

class GrokAPIClient(BaseAPIClient):
    """xAI Grok API client with all models support"""
    
    def __init__(self, api_key: Optional[str] = None):
        api_key = api_key or os.getenv('XAI_API_KEY')
        if not api_key:
            raise ValueError("XAI_API_KEY not found")
        super().__init__(api_key, "https://api.x.ai/v1")
        
    async def chat_completion(self, 
                             model: str,
                             messages: List[Dict[str, str]],
                             temperature: float = 0.7,
                             max_tokens: Optional[int] = None,
                             stream: bool = False,
                             **kwargs) -> APIResponse:
        """Send chat completion request to Grok"""
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
            "stream": stream,
            **kwargs
        }
        
        if max_tokens:
            payload["max_tokens"] = max_tokens
            
        if stream:
            return self._stream_completion(headers, payload)
        
        data, latency_ms = await self._make_request("POST", "chat/completions", headers, payload)
        
        return APIResponse(
            content=data['choices'][0]['message']['content'],
            model=model,
            provider="xai",
            usage={
                'input_tokens': data['usage']['prompt_tokens'],
                'output_tokens': data['usage']['completion_tokens']
            },
            latency_ms=latency_ms,
            raw_response=data
        )
    
    async def _stream_completion(self, headers: Dict, payload: Dict) -> AsyncIterator[str]:
        """Stream completion responses"""
        payload['stream'] = True
        
        async with self.session.post(
            f"{self.base_url}/chat/completions",
            headers=headers,
            json=payload
        ) as response:
            async for line in response.content:
                if line:
                    line = line.decode('utf-8').strip()
                    if line.startswith("data: ") and line != "data: [DONE]":
                        try:
                            chunk = json.loads(line[6:])
                            if 'choices' in chunk and chunk['choices']:
                                delta = chunk['choices'][0].get('delta', {})
                                if 'content' in delta:
                                    yield delta['content']
                        except json.JSONDecodeError:
                            continue

class OpenAIAPIClient(BaseAPIClient):
    """OpenAI API client"""
    
    def __init__(self, api_key: Optional[str] = None):
        api_key = api_key or os.getenv('OPENAI_API_KEY')
        if not api_key:
            raise ValueError("OPENAI_API_KEY not found")
        super().__init__(api_key, "https://api.openai.com/v1")
        
    async def chat_completion(self,
                             model: str,
                             messages: List[Dict[str, str]],
                             temperature: float = 0.7,
                             max_tokens: Optional[int] = None,
                             stream: bool = False,
                             **kwargs) -> APIResponse:
        """Send chat completion request to OpenAI"""
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
            **kwargs
        }
        
        if max_tokens:
            payload["max_tokens"] = max_tokens
            
        data, latency_ms = await self._make_request("POST", "chat/completions", headers, payload)
        
        return APIResponse(
            content=data['choices'][0]['message']['content'],
            model=model,
            provider="openai",
            usage={
                'input_tokens': data['usage']['prompt_tokens'],
                'output_tokens': data['usage']['completion_tokens']
            },
            latency_ms=latency_ms,
            raw_response=data
        )

class GoogleAPIClient(BaseAPIClient):
    """Google Gemini API client"""
    
    def __init__(self, api_key: Optional[str] = None):
        api_key = api_key or os.getenv('GOOGLE_API_KEY')
        if not api_key:
            raise ValueError("GOOGLE_API_KEY not found")
        super().__init__(api_key, "https://generativelanguage.googleapis.com/v1beta")
        
    async def chat_completion(self,
                             model: str,
                             messages: List[Dict[str, str]],
                             temperature: float = 0.7,
                             max_tokens: Optional[int] = None,
                             **kwargs) -> APIResponse:
        """Send chat completion request to Google Gemini"""
        
        headers = {
            "Content-Type": "application/json",
        }
        
        # Convert messages to Gemini format
        contents = []
        for msg in messages:
            contents.append({
                "parts": [{"text": msg["content"]}],
                "role": "user" if msg["role"] == "user" else "model"
            })
        
        payload = {
            "contents": contents,
            "generationConfig": {
                "temperature": temperature,
                "candidateCount": 1,
            }
        }
        
        if max_tokens:
            payload["generationConfig"]["maxOutputTokens"] = max_tokens
            
        endpoint = f"models/{model}:generateContent?key={self.api_key}"
        data, latency_ms = await self._make_request("POST", endpoint, headers, payload)
        
        return APIResponse(
            content=data['candidates'][0]['content']['parts'][0]['text'],
            model=model,
            provider="google",
            usage={
                'input_tokens': data['usageMetadata']['promptTokenCount'],
                'output_tokens': data['usageMetadata']['candidatesTokenCount']
            },
            latency_ms=latency_ms,
            raw_response=data
        )

class AnthropicAPIClient(BaseAPIClient):
    """Anthropic Claude API client (via DIAL or direct)"""
    
    def __init__(self, api_key: Optional[str] = None, use_dial: bool = False):
        if use_dial:
            api_key = api_key or os.getenv('DIAL_API_KEY')
            if not api_key:
                raise ValueError("DIAL_API_KEY not found")
            # Assuming DIAL endpoint - adjust as needed
            super().__init__(api_key, "https://dial.api.endpoint/v1")
        else:
            api_key = api_key or os.getenv('ANTHROPIC_API_KEY')
            if not api_key:
                raise ValueError("ANTHROPIC_API_KEY not found")
            super().__init__(api_key, "https://api.anthropic.com/v1")
        
        self.use_dial = use_dial
        
    async def chat_completion(self,
                             model: str,
                             messages: List[Dict[str, str]],
                             temperature: float = 0.7,
                             max_tokens: Optional[int] = None,
                             **kwargs) -> APIResponse:
        """Send chat completion request to Anthropic/DIAL"""
        
        if self.use_dial:
            # DIAL format (OpenAI-compatible)
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "model": model,
                "messages": messages,
                "temperature": temperature,
                **kwargs
            }
            
            if max_tokens:
                payload["max_tokens"] = max_tokens
                
            data, latency_ms = await self._make_request("POST", "chat/completions", headers, payload)
            
            return APIResponse(
                content=data['choices'][0]['message']['content'],
                model=model,
                provider="dial",
                usage={
                    'input_tokens': data['usage']['prompt_tokens'],
                    'output_tokens': data['usage']['completion_tokens']
                },
                latency_ms=latency_ms,
                raw_response=data
            )
        else:
            # Direct Anthropic API
            headers = {
                "x-api-key": self.api_key,
                "anthropic-version": "2023-06-01",
                "Content-Type": "application/json"
            }
            
            # Convert to Anthropic format
            system_msg = None
            claude_messages = []
            
            for msg in messages:
                if msg["role"] == "system":
                    system_msg = msg["content"]
                else:
                    claude_messages.append({
                        "role": msg["role"],
                        "content": msg["content"]
                    })
            
            payload = {
                "model": model,
                "messages": claude_messages,
                "temperature": temperature,
                "max_tokens": max_tokens or 4096,
                **kwargs
            }
            
            if system_msg:
                payload["system"] = system_msg
                
            data, latency_ms = await self._make_request("POST", "messages", headers, payload)
            
            return APIResponse(
                content=data['content'][0]['text'],
                model=model,
                provider="anthropic",
                usage={
                    'input_tokens': data['usage']['input_tokens'],
                    'output_tokens': data['usage']['output_tokens']
                },
                latency_ms=latency_ms,
                raw_response=data
            )

class AzureOpenAIClient(BaseAPIClient):
    """Azure OpenAI Service API client"""
    
    def __init__(self, api_key: Optional[str] = None, endpoint: Optional[str] = None):
        api_key = api_key or os.getenv('AZURE_OPENAI_API_KEY')
        endpoint = endpoint or os.getenv('AZURE_OPENAI_ENDPOINT')
        if not api_key or not endpoint:
            raise ValueError("AZURE_OPENAI_API_KEY and AZURE_OPENAI_ENDPOINT required")
        super().__init__(api_key, endpoint)
        
    async def chat_completion(self,
                             model: str,
                             messages: List[Dict[str, str]],
                             temperature: float = 0.7,
                             max_tokens: Optional[int] = None,
                             **kwargs) -> APIResponse:
        """Send chat completion request to Azure OpenAI"""
        
        headers = {
            "api-key": self.api_key,
            "Content-Type": "application/json"
        }
        
        payload = {
            "messages": messages,
            "temperature": temperature,
            **kwargs
        }
        
        if max_tokens:
            payload["max_tokens"] = max_tokens
            
        # Azure OpenAI uses deployment names in the endpoint
        endpoint = f"openai/deployments/{model}/chat/completions?api-version=2024-02-15-preview"
        data, latency_ms = await self._make_request("POST", endpoint, headers, payload)
        
        return APIResponse(
            content=data['choices'][0]['message']['content'],
            model=model,
            provider="azure",
            usage={
                'input_tokens': data['usage']['prompt_tokens'],
                'output_tokens': data['usage']['completion_tokens']
            },
            latency_ms=latency_ms,
            raw_response=data
        )

class BedrockAPIClient(BaseAPIClient):
    """Amazon Bedrock API client"""
    
    def __init__(self, region: str = "us-east-1"):
        # Bedrock uses AWS credentials, not API keys
        super().__init__("", f"https://bedrock-runtime.{region}.amazonaws.com")
        self.region = region
        
    async def chat_completion(self,
                             model: str,
                             messages: List[Dict[str, str]],
                             temperature: float = 0.7,
                             max_tokens: Optional[int] = None,
                             **kwargs) -> APIResponse:
        """Send chat completion request to Amazon Bedrock"""
        
        # Note: This is a simplified implementation
        # Real Bedrock integration requires AWS signature V4 authentication
        
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
        
        # Format varies by model provider on Bedrock
        if model.startswith("anthropic."):
            # Claude format
            payload = {
                "anthropic_version": "bedrock-2023-05-31",
                "messages": messages,
                "temperature": temperature,
                "max_tokens": max_tokens or 4096
            }
        elif model.startswith("meta."):
            # Llama format
            prompt = "\n".join([f"{m['role']}: {m['content']}" for m in messages])
            payload = {
                "prompt": prompt,
                "temperature": temperature,
                "max_gen_len": max_tokens or 4096
            }
        elif model.startswith("amazon."):
            # Titan format
            prompt = "\n".join([f"{m['role']}: {m['content']}" for m in messages])
            payload = {
                "inputText": prompt,
                "textGenerationConfig": {
                    "temperature": temperature,
                    "maxTokenCount": max_tokens or 4096
                }
            }
            
        endpoint = f"model/{model}/invoke"
        # Note: This would need proper AWS authentication in real implementation
        raise NotImplementedError("Bedrock requires AWS authentication - use boto3 in production")

class LocalModelClient(BaseAPIClient):
    """Local model client (Ollama/vLLM compatible)"""
    
    def __init__(self, base_url: Optional[str] = None):
        base_url = base_url or os.getenv('CUSTOM_API_URL', 'http://localhost:11434/v1')
        # No API key needed for local models
        super().__init__("", base_url)
        
    async def chat_completion(self,
                             model: str,
                             messages: List[Dict[str, str]],
                             temperature: float = 0.7,
                             max_tokens: Optional[int] = None,
                             **kwargs) -> APIResponse:
        """Send chat completion request to local model"""
        
        headers = {"Content-Type": "application/json"}
        
        payload = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
            **kwargs
        }
        
        if max_tokens:
            payload["max_tokens"] = max_tokens
            
        try:
            data, latency_ms = await self._make_request("POST", "chat/completions", headers, payload)
            
            return APIResponse(
                content=data['choices'][0]['message']['content'],
                model=model,
                provider="local",
                usage={
                    'input_tokens': data.get('usage', {}).get('prompt_tokens', 0),
                    'output_tokens': data.get('usage', {}).get('completion_tokens', 0)
                },
                latency_ms=latency_ms,
                raw_response=data
            )
        except Exception as e:
            # Fallback for Ollama format
            try:
                ollama_payload = {
                    "model": model,
                    "prompt": messages[-1]["content"],
                    "temperature": temperature,
                }
                
                async with self.session.post(f"{self.base_url}/api/generate", json=ollama_payload) as response:
                    data = await response.json()
                    
                return APIResponse(
                    content=data['response'],
                    model=model,
                    provider="local",
                    usage={'input_tokens': 0, 'output_tokens': 0},
                    latency_ms=0,
                    raw_response=data
                )
            except:
                raise e

# Factory function to get appropriate client
def get_api_client(provider: str, **kwargs) -> BaseAPIClient:
    """Factory function to get the appropriate API client"""
    
    clients = {
        'xai': GrokAPIClient,
        'openai': OpenAIAPIClient,
        'google': GoogleAPIClient,
        'anthropic': AnthropicAPIClient,
        'dial': lambda: AnthropicAPIClient(use_dial=True),
        'local': LocalModelClient,
    }
    
    if provider not in clients:
        raise ValueError(f"Unknown provider: {provider}")
    
    return clients[provider](**kwargs)
