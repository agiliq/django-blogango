from django.core.urlresolvers import reverse

class XPingMiddleware:
    xmlrpc_url = reverse('xmlrpc')

    def process_response(self, request, response):
        if response.status_code == 200:
            response['X-Pingback'] = request.build_absolute_uri(self.xmlrpc_url)
        return response

