from django.contrib import messages
from django.shortcuts import redirect
from django.core.urlresolvers import reverse
from ..models import Pool
from ..forms import AddOrEditForm
from django.db import IntegrityError
from strongMan.helper_apps.vici.wrapper.exception import ViciException
from strongMan.helper_apps.vici.wrapper.wrapper import ViciWrapper
from django.shortcuts import render


class AddHandler:
    def __init__(self, is_add_form=False):
        self.form = None
        self.request = None
        self.is_add_form = is_add_form

    @classmethod
    def by_request(cls, request, is_add_form=False):
        handler = cls(is_add_form)
        handler.request = request
        return handler

    def handle(self):
        self.form = AddOrEditForm(self.request.POST)
        if not self.form.is_valid():
            messages.add_message(self.request, messages.ERROR,
                                 'Form was not valid')
            return render(self.request, 'pools/add.html', {"form": self.form})

        if self.form.my_attribute == 'None':
            pool = Pool(poolname=self.form.my_poolname, addresses=self.form.my_addresses)
            vici_pool = {self.form.my_poolname: {'addrs': self.form.my_addresses}}
        else:
            attr = self.form.my_attribute
            pool = Pool(poolname=self.form.my_poolname, addresses=self.form.my_addresses,
                        attribute=attr,
                        attributevalues=self.form.my_attributevalues)
            vici_pool = {self.form.my_poolname: {'addrs': self.form.my_addresses, attr: [self.form.my_attributevalues]}}
        try:
            pool.clean()
            pool.save()
            vici = ViciWrapper()
            vici.load_pool(vici_pool)

        except ViciException as e:
            messages.add_message(self.request, messages.ERROR, str(e))
            pool.delete()
            return render(self.request, 'pools/add.html', {"form": self.form})
        except IntegrityError:
            messages.add_message(self.request, messages.ERROR,
                                 'Poolname already in use.')
            return render(self.request, 'pools/add.html', {"form": self.form})

        messages.add_message(self.request, messages.SUCCESS, 'Successfully added pool')
        return redirect(reverse("pools:index"))

