"""OpenRouter API client for making LLM requests."""

import httpx
from typing import List, Dict, Any, Optional

from models import CouncilModel

#code matheo
import asyncio

async def query_model(
    model: CouncilModel,
    messages: List[Dict[str, str]],
    timeout: float = 120.0,
) -> Optional[Dict[str, Any]]:
    """
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
    }

    payload = {
        "model": model,
        "messages": messages,
    }

    try:
        async with httpx.AsyncClient(timeout=timeout) as client:
            response = await client.post(
                OPENROUTER_API_URL,
                headers=headers,
                json=payload
            )
            response.raise_for_status()

            data = response.json()
            message = data['choices'][0]['message']

            return {
                'content': message.get('content'),
                'reasoning_details': message.get('reasoning_details')
            }

    except Exception as e:
        print(f"Error querying model {model}: {e}")
        return None
    """
    
    #code (à modifier)
    """Envoie une requête à l'instance Ollama locale."""

    headers = {
        "Content-Type": "application/json"
    }

    payload = {
        "model": model.model_name,
        "messages": messages,
        "stream": False  
    }

    try:
        async with httpx.AsyncClient() as client:
            
            url: str = f"http://{model.ip}:{model.port}/api/chat"

            # Augmenter le timeout car les modèles locaux peuvent mettre du temps à répondre
            response = await client.post(
                url, 
                json=payload,
                headers=headers,
                timeout=300.0 

            )
            response.raise_for_status()

            data = response.json()

            return {
                'content': data['message']['content'],
                'reasoning_details': None
            }
        
    except Exception as e:
        print(f"Erreur lors de la requête vers {model}: {e}")
        return None


async def query_models_parallel(
    models: List[CouncilModel],
    messages: List[Dict[str, str]],
    timeout: float = 120.0,
) -> Dict[str, Optional[Dict[str, Any]]]:

    async def _call(model: CouncilModel):
        return await query_model(model, messages, timeout=timeout)

    tasks = [_call(model) for model in models]
    results = await asyncio.gather(*tasks, return_exceptions=True)

    responses: Dict[str, Optional[Dict[str, Any]]] = {}

    for model, result in zip(models, results):
        if isinstance(result, Exception):
            print(f"[query_models_parallel] Error for {model.model_name}: {result}")
            responses[model.model_name] = None
        else:
            responses[model.model_name] = result

    return responses
