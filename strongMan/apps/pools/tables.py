import django_tables2 as tables
from django.template.loader import render_to_string


class PoolsTable(tables.Table):
    poolname = tables.Column(accessor="name", verbose_name="Name")
    addresses = tables.Column(accessor="addresses.first.value", verbose_name="Addresses", orderable=False)

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop("request")
        super(PoolsTable, self).__init__(*args, **kwargs)

    def render_name(self, record):
        return render_to_string('pools/widgets/name_column.html', {'record': record}, request=self.request)

    def render_addresses(self, record):
        return render_to_string('pools/widgets/address_column.html', {'record': record}, request=self.request)

    class Meta:
        attrs = {"class": "table"}
