from django.contrib import messages
from django.shortcuts import render
from django_tables2 import RequestConfig
from collections import OrderedDict

from strongMan.apps.server_connections.models.connections import Connection

from strongMan.apps.vici.wrapper.exception import ViciException

from ..tables import ConnectionTable


class OverviewHandler:
    def __init__(self, request):
        self.request = request
        self.ENTRIES_PER_PAGE = 10

    def handle(self):
        try:
            return self._render()
        except ViciException as e:
            messages.warning(self.request, str(e))

    def _render(self):
        queryset = Connection.objects.all()
        table = ConnectionTable(queryset, request=self.request)
        RequestConfig(self.request, paginate={"per_page": self.ENTRIES_PER_PAGE}).configure(table)
        if len(queryset) == 0:
            table = None
        return render(self.request, 'server_connections/overview.html', {'table': table})
