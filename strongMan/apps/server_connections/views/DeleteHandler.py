from django.contrib import messages
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from strongMan.helper_apps.vici.wrapper.exception import ViciException

from strongMan.apps.server_connections.models.connections import Connection
from strongMan.helper_apps.vici.wrapper.wrapper import ViciWrapper


class DeleteHandler:
    def __init__(self, request, id):
        self.request = request
        self.id = id

    def handle(self):
        connection = Connection.objects.get(id=self.id).subclass()
        try:
            vici_wrapper = ViciWrapper()
            if vici_wrapper.is_connection_loaded(connection.profile) is True:
                vici_wrapper.unload_connection(connection.profile)
        except ViciException as e:
            messages.warning(self.request, str(e))
        finally:
            profilname = connection.profile
            connection.delete()
            messages.info(self.request, "Connection " + profilname + " deleted.")
            return HttpResponseRedirect(reverse("server_connections:index"))
