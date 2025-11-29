from transformers import MarianMTModel, MarianTokenizer

# French to English
model_fr_en = MarianMTModel.from_pretrained("Helsinki-NLP/opus-mt-fr-en")
tokenizer_fr_en = MarianTokenizer.from_pretrained("Helsinki-NLP/opus-mt-fr-en")

# English to French
model_en_fr = MarianMTModel.from_pretrained("Helsinki-NLP/opus-mt-en-fr")
tokenizer_en_fr = MarianTokenizer.from_pretrained("Helsinki-NLP/opus-mt-en-fr")


def translate_fr_to_en(text:str) -> str:
    inputs = tokenizer_fr_en(text, return_tensors="pt", padding=True)
    translated = model_fr_en.generate(**inputs)
    return tokenizer_fr_en.decode(translated[0], skip_special_tokens=True)
    
    
def translate_en_to_fr(text: str) -> str:
    inputs = tokenizer_en_fr(text, return_tensors="pt", padding=True)
    translated = model_en_fr.generate(**inputs)
    return tokenizer_en_fr.decode(translated[0], skip_special_tokens=True)
