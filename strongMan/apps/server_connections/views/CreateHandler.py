from ..forms.SubForms import HeaderForm
from strongMan.apps.server_connections.forms.ConnectionForms import AbstractDynamicForm
from ..forms import ChooseTypeForm
from django.shortcuts import render, redirect
from django.core.urlresolvers import reverse

from .. import forms


class AddHandler:
    def __init__(self, request, connection_type):
        self.request = request
        self.connection_type = connection_type

    def _render(self, form=ChooseTypeForm()):
        if isinstance(form, ChooseTypeForm):
            form = ChooseTypeForm(None, self.connection_type)
        form.connection_type = self.connection_type
        return render(self.request, 'server_connections/Detail.html', {"form": form})

    def _abstract_form(self):
        '''
        Intiates and validates the Abstract form
        :return Valid abstract form
        '''
        form = AbstractDynamicForm(self.request.POST)
        if not form.is_valid():
            raise Exception("No valid form detected." + str(form.errors))
        return form

    def handle(self):
        if self.request.method == "GET":
            return self._render()
        elif self.request.method == "POST":
            abstract_form = self._abstract_form()
            form_class = abstract_form.current_form_class

            form = form_class(self.request.POST, self.connection_type)
            form.update_certs()
            if not form.is_valid():
                return self._render(form)

            if form_class == forms.ChooseTypeForm:
                return self._render(form=form.selected_form_class())

            if isinstance(form, HeaderForm):
                form.create_connection(self.connection_type)
                return redirect(reverse("server_connections:index"))
