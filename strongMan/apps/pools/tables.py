import django_tables2 as tables
from django.template.loader import render_to_string
from strongMan.helper_apps.vici.wrapper.wrapper import ViciWrapper
# from ..forms import OverviewDetailForm


class PoolsTable(tables.Table):
    detail_collapse_column = tables.Column(accessor="id", verbose_name="", orderable=False)
    poolname = tables.Column(accessor="poolname", verbose_name="Name")
    addresses = tables.Column(accessor="addresses", verbose_name="Addresses")
    removebtn = tables.Column(accessor="id", verbose_name='Remove Pool', orderable=False)

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop("request")
        super(PoolsTable, self).__init__(*args, **kwargs)

    def render_removebtn(self, record):
        return render_to_string('pools/widgets/remove_column.html', {'poolname': record.poolname},
                                request=self.request)

    def render_poolname(self, record):
        return render_to_string('pools/widgets/name_column.html', {'record': record},
                                request=self.request)

    def render_detail_collapse_column(self, record):
        vici_wrapper = ViciWrapper()
        pools = vici_wrapper.get_pools()
        # self.detail_table = pools  # tables.DetailPoolTable(pools, request=self.request)
        # detail_form = OverviewDetailForm(pools)
        # for item in pools['items']
        return render_to_string('pools/widgets/detail_collapse_column.html', {'record': record, 'detail': pools},
                                request=self.request)

    class Meta:
        attrs = {"class": "table"}

