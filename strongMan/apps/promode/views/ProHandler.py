from collections import OrderedDict
from django.shortcuts import render
from django.contrib import messages

from strongMan.apps.vici.wrapper.exception import ViciLoadException
from strongMan.apps.vici.wrapper.wrapper import ViciWrapper

from strongMan.apps.promode.prowrapper.prowrapper import ProViciWrapper


class ProHandler:
    def __init__(self, request):
        self.request = request

    def handle(self):
        if self.request.method == "GET":
            context = OrderedDict()
            try:
                vici_wrapper = ViciWrapper()
                context['status'] = vici_wrapper.get_status()
                context['version'] = vici_wrapper.get_version()
                context['certs'] = vici_wrapper.get_certificates()

                context['pprint'] = dict(context.items())

                pro_vici_wrapper = ProViciWrapper()
                list_conns = pro_vici_wrapper.list_conns()
                get_conns = pro_vici_wrapper.get_conns()
                list_certs = pro_vici_wrapper.list_certs()

                context['list_conns'] = list_conns
                context['get_conns'] = get_conns
                context['list_certs'] = list_certs

            except ViciLoadException as e:
                messages.warning(self.request, str(e))
            messages.info(self.request, "Cooli sach, jetzt bisch profi! ;)")
            return self._render(context)

    def _render(self, context):
        return render(self.request, 'promode/overview.html', context)
