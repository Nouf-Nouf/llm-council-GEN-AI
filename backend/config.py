import os
from dotenv import load_dotenv
from models import CouncilModel, Role

load_dotenv()

# Data directory for conversation storage
DATA_DIR = "data/conversations"

COUNCIL_MODELS = [
    CouncilModel(ip= "ollama", model_name="qwen2.5:1.5b", role=Role.CHAIRMAN),
    CouncilModel(ip= "ollama", model_name="llama3.2:3b", role=Role.COUNCILOR),
    CouncilModel(ip= "ollama", model_name="llama3.2:1b", role=Role.COUNCILOR)
]

# Data directory for conversation storage
DATA_DIR = "data/conversations"

PROMPT_PRE_INJECTION = f"""
Role : You are a helpful and knowledgeable council member AI model assisting in a multi-model council discussion.
Behavior : You must provide detailed and well-reasoned responses to user queries, drawing on your expertise. Always aim to contribute constructively to the council's deliberations.
    

"""