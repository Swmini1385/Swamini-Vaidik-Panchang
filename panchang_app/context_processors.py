from .translations import TRANSLATIONS

def translation_context(request):
    # Retrieve language choice from session, default to Marathi
    lang = request.session.get('lang', 'mr')
    if lang not in ['mr', 'en']:
        lang = 'mr'
        
    return {
        'trans': TRANSLATIONS[lang],
        'current_lang': lang
    }
