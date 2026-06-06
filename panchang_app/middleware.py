from django.utils.translation import activate

class VaidikLocaleMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        lang = request.session.get('lang', 'mr')
        activate(lang)
        response = self.get_response(request)
        return response
