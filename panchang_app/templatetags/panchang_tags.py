from django import template
from panchang_app.translations import TRANSLATIONS

register = template.Library()

@register.filter
def translate_val(value, lang):
    if not value:
        return ""
    val_str = str(value).strip()
    
    lang_dict = TRANSLATIONS.get(lang, TRANSLATIONS['mr'])
    
    # 1. Exact match
    if val_str in lang_dict:
        return lang_dict[val_str]
        
    # 2. Case-insensitive exact match
    for k, v in lang_dict.items():
        if k.lower() == val_str.lower():
            return v
            
    # 3. Composite strings (e.g., "Shukla Paksha Pratipada" or "Krishna Paksha Chaturthi")
    # split into words and translate each word.
    words = val_str.split()
    translated_words = []
    for word in words:
        translated_word = word
        # Strip any trailing punctuation/whitespace
        cleaned_word = word.strip(',.!:;()')
        matched = False
        for k, v in lang_dict.items():
            if k.lower() == cleaned_word.lower():
                # Replace the cleaned part but preserve the punctuation if there was any
                translated_word = word.replace(cleaned_word, v)
                matched = True
                break
        translated_words.append(translated_word)
        
    return " ".join(translated_words)
