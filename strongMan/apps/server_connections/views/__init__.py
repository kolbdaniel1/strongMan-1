from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from .connectionHandler import ConnectionHandler


@login_required
@require_http_methods('GET')
def server_connections(request):
    handler = ConnectionHandler(request)
    return handler.handle()
