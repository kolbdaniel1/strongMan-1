import django_tables2 as tables
from django.template.loader import render_to_string


class ConnectionTable(tables.Table):
    readonly = tables.Column(accessor='id', verbose_name='')
    name = tables.Column(accessor="profile", verbose_name='Name')
    remote_addrs = tables.Column(accessor="server_local_addresses.first.value", verbose_name="Server", orderable=False)
    type = tables.Column(accessor="subclass.choice_name", verbose_name="Authentication Type", orderable=False)
    connection_type = tables.Column(accessor='get_connection_type', verbose_name="Connection Type", orderable=False)
    state = tables.Column(accessor="state", verbose_name="State", orderable=False,
                          attrs={'th': {'class': "col-xs-2"}})

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop("request")
        super(ConnectionTable, self).__init__(*args, **kwargs)

    def render_readonly(self, record):
        return render_to_string('server_connections/widgets/readonly_column.html', {'record': record}, request=self.request)

    def render_name(self, record):
        return render_to_string('server_connections/widgets/name_column.html', {'record': record}, request=self.request)

    def render_state(self, record):
        return render_to_string('server_connections/widgets/state_column.html', {'record': record}, request=self.request)

    class Meta:
        attrs = {"class": "table"}
