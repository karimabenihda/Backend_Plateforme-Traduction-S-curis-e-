import os
import requests
from dotenv import load_dotenv

load_dotenv()

HF_TOKEN = os.getenv("HF_TOKEN")

API_EN_TO_FR = "https://router.huggingface.co/hf-inference/models/Helsinki-NLP/opus-mt-en-fr"
API_FR_TO_EN = "https://router.huggingface.co/hf-inference/models/Helsinki-NLP/opus-mt-fr-en"

headers = {"Authorization": f"Bearer {HF_TOKEN}"}

def translate_en_to_fr(text: str) -> str:
    response = requests.post(API_EN_TO_FR, headers=headers, json={"inputs": text})
    result = response.json()
    # HuggingFace API returns [{"translation_text": "..."}]
    return result[0]["translation_text"] if isinstance(result, list) else str(result)

def translate_fr_to_en(text: str) -> str:
    response = requests.post(API_FR_TO_EN, headers=headers, json={"inputs": text})
    result = response.json()
    return result[0]["translation_text"] if isinstance(result, list) else str(result)
