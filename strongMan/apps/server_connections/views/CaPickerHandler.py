from django.shortcuts import render
from ..forms import Ike2CertificateForm


class CaPickerHandler:
    def __init__(self, request):
        self.request = request

    def handle(self):
        form = Ike2CertificateForm()
        return render(self.request,
                      'server_connections/forms/CaPicker.html', {"form": form})
