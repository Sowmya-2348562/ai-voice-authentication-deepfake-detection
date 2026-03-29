import os
from dotenv import load_dotenv
import requests

# Load environment variables from .env
load_dotenv()
groq_api_key = os.getenv("GROQ_API_KEY", "")
if not groq_api_key:
    raise ValueError("GROQ_API_KEY is not set in the environment.")

class Agent:
    """
    A generic agent that processes either text or audio.
    We simulate text-based queries with a chat completions endpoint
    and audio-based queries with an audio transcription endpoint.
    """
    def __init__(self, name, model_id, description=""):
        self.name = name
        self.model_id = model_id
        self.description = description
        self.groq_api_key = groq_api_key

    def ask(self, query_or_audio):
        headers = {
            "Authorization": f"Bearer {self.groq_api_key}",
        }
        try:
            if isinstance(query_or_audio, str):
                # Text-based query
                endpoint = "https://api.groq.com/openai/v1/chat/completions"
                payload = {
                    "model": self.model_id,
                    "messages": [
                        {"role": "user", "content": query_or_audio}
                    ],
                    "temperature": 0.3
                }
                headers["Content-Type"] = "application/json"
                response = requests.post(endpoint, json=payload, headers=headers)
                response.raise_for_status()
                result = response.json()
                choices = result.get("choices", [])
                if choices and "message" in choices[0]:
                    return choices[0]["message"].get("content", "No response content provided by the API.")
                else:
                    return "No valid response from GroqAPI."
            else:
                # Audio-based query
                endpoint = "https://api.groq.com/openai/v1/audio/transcriptions"
                data = {
                    "model": "whisper-large-v3",
                    "language": "en"
                }
                files = {
                    "file": (query_or_audio.filename, query_or_audio, "audio/wav")
                }
                response = requests.post(endpoint, data=data, headers=headers, files=files)
                response.raise_for_status()
                result = response.json()
                return result.get("text", "No transcription provided by the API.")
        except requests.exceptions.RequestException as e:
            return f"Error calling GroqAPI: {str(e)}"

# Instantiate the four agents
qwen_agent = Agent(name="Qwen Agent", model_id="qwen-2.5-32b", description="General conversation agent")
multi_agent = Agent(name="Multi-Agent Team", model_id="qwen-2.5-32b", description="A team of specialized agents")
whisper_agent = Agent(name="Whisper Agent", model_id="whisper-large-v3", description="Speech transcription agent")
deepseek_agent = Agent(name="Deepseek Agent", model_id="deepseek-r1-distill-llama-70b", description="Deep research agent")
