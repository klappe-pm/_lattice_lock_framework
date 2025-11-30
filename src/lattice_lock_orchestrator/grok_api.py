#!/usr/bin/env python3
"""
Direct xAI Grok API Integration
Supports all Grok models including vision and image generation
"""

import os
import sys
import json
import yaml
import base64
import requests
from pathlib import Path
from typing import Optional, Dict, Any, List
from datetime import datetime

class GrokAPI:
    def __init__(self, api_key: Optional[str] = None, config_path: Optional[str] = None):
        """Initialize Grok API client with configuration"""
        self.api_key = api_key or os.getenv('XAI_API_KEY')
        if not self.api_key:
            raise ValueError("XAI_API_KEY environment variable not set")
        
        # Load configuration
        self.config_path = config_path or Path(__file__).parent / "grok_models_config.yaml"
        self.config = self._load_config()
        self.base_url = self.config['api']['base_url']
        
    def _load_config(self) -> Dict:
        """Load model configuration from YAML"""
        if not os.path.exists(self.config_path):
            raise FileNotFoundError(f"Config file not found: {self.config_path}")
        
        with open(self.config_path, 'r') as f:
            return yaml.safe_load(f)
    
    def list_models(self, category: Optional[str] = None) -> List[Dict]:
        """List available models, optionally filtered by category"""
        models = []
        
        for cat, model_list in self.config['models'].items():
            if category and cat != category:
                continue
            models.extend(model_list)
        
        return models
    
    def get_model_info(self, model_id: str) -> Optional[Dict]:
        """Get detailed information about a specific model"""
        # Check aliases first
        if model_id in self.config['aliases']:
            model_id = self.config['aliases'][model_id]
        
        for category in self.config['models'].values():
            for model in category:
                if model['id'] == model_id:
                    return model
        return None
    
    def chat_completion(self, 
                        model_id: str, 
                        messages: List[Dict[str, str]], 
                        **kwargs) -> Dict:
        """Send chat completion request to Grok API"""
        # Resolve aliases
        if model_id in self.config['aliases']:
            model_id = self.config['aliases'][model_id]
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": model_id,
            "messages": messages,
            **kwargs
        }
        
        response = requests.post(
            f"{self.base_url}/chat/completions",
            headers=headers,
            json=payload
        )
        
        if response.status_code != 200:
            raise Exception(f"API Error: {response.status_code} - {response.text}")
        
        return response.json()
    
    def vision_completion(self, 
                         model_id: str, 
                         messages: List[Dict], 
                         image_path: Optional[str] = None,
                         **kwargs) -> Dict:
        """Send vision completion request with image input"""
        if image_path:
            # Encode image to base64
            with open(image_path, 'rb') as img_file:
                image_data = base64.b64encode(img_file.read()).decode('utf-8')
            
            # Add image to the last user message
            for msg in reversed(messages):
                if msg['role'] == 'user':
                    if isinstance(msg['content'], str):
                        msg['content'] = [
                            {"type": "text", "text": msg['content']},
                            {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{image_data}"}}
                        ]
                    break
        
        return self.chat_completion(model_id, messages, **kwargs)
    
    def image_generation(self, 
                        prompt: str,
                        model_id: str = "grok-2-image-1212",
                        **kwargs) -> Dict:
        """Generate image using Grok image generation model"""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": model_id,
            "prompt": prompt,
            **kwargs
        }
        
        response = requests.post(
            f"{self.base_url}/images/generations",
            headers=headers,
            json=payload
        )
        
        if response.status_code != 200:
            raise Exception(f"API Error: {response.status_code} - {response.text}")
        
        return response.json()
    
    def stream_completion(self, 
                         model_id: str, 
                         messages: List[Dict[str, str]], 
                         **kwargs) -> Any:
        """Stream chat completion responses"""
        # Resolve aliases
        if model_id in self.config['aliases']:
            model_id = self.config['aliases'][model_id]
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": model_id,
            "messages": messages,
            "stream": True,
            **kwargs
        }
        
        response = requests.post(
            f"{self.base_url}/chat/completions",
            headers=headers,
            json=payload,
            stream=True
        )
        
        for line in response.iter_lines():
            if line:
                line = line.decode('utf-8')
                if line.startswith('data: '):
                    data = line[6:]
                    if data != '[DONE]':
                        yield json.loads(data)

def main():
    """CLI interface for Grok API"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Grok API Client')
    parser.add_argument('command', choices=['list', 'chat', 'vision', 'image', 'info'],
                       help='Command to execute')
    parser.add_argument('--model', '-m', help='Model ID or alias')
    parser.add_argument('--prompt', '-p', help='Prompt text')
    parser.add_argument('--image', '-i', help='Image file path for vision models')
    parser.add_argument('--category', '-c', help='Filter models by category')
    parser.add_argument('--stream', action='store_true', help='Stream responses')
    
    args = parser.parse_args()
    
    try:
        api = GrokAPI()
        
        if args.command == 'list':
            models = api.list_models(args.category)
            print(f"\n{'='*80}")
            print(f"{'Model ID':<30} {'Context':<15} {'Description':<35}")
            print(f"{'-'*80}")
            for model in models:
                context = str(model.get('context_window', 'N/A'))
                desc = model.get('description', '')[:35]
                print(f"{model['id']:<30} {context:<15} {desc:<35}")
            print(f"{'='*80}\n")
            
        elif args.command == 'info':
            if not args.model:
                print("Error: --model required for info command")
                sys.exit(1)
            info = api.get_model_info(args.model)
            if info:
                print(f"\nModel Information: {info['id']}")
                print(f"{'-'*40}")
                for key, value in info.items():
                    if key != 'id':
                        print(f"{key:<20}: {value}")
            else:
                print(f"Model '{args.model}' not found")
                
        elif args.command == 'chat':
            if not args.model or not args.prompt:
                print("Error: --model and --prompt required for chat")
                sys.exit(1)
            
            messages = [{"role": "user", "content": args.prompt}]
            
            if args.stream:
                for chunk in api.stream_completion(args.model, messages):
                    if 'choices' in chunk:
                        content = chunk['choices'][0].get('delta', {}).get('content', '')
                        print(content, end='', flush=True)
                print()
            else:
                response = api.chat_completion(args.model, messages)
                print(response['choices'][0]['message']['content'])
                
        elif args.command == 'vision':
            if not args.model or not args.prompt:
                print("Error: --model and --prompt required for vision")
                sys.exit(1)
            
            messages = [{"role": "user", "content": args.prompt}]
            response = api.vision_completion(args.model, messages, args.image)
            print(response['choices'][0]['message']['content'])
            
        elif args.command == 'image':
            if not args.prompt:
                print("Error: --prompt required for image generation")
                sys.exit(1)
            
            response = api.image_generation(args.prompt)
            print(f"Generated image URL: {response['data'][0]['url']}")
            
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()