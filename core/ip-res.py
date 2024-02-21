from django.shortcuts import redirect
from django.http import HttpResponse

class AllowOnlyOneIPAddressMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):

        allowed_ip = '85.111.28.15'  
        

        client_ip = request.META.get('REMOTE_ADDR')
        

        if client_ip == allowed_ip:
            response = self.get_response(request)
            return response

        return HttpResponse('Erişim reddedildi.', status=403)