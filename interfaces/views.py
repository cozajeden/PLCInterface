from typing import Dict, Any

from django.shortcuts import render
from django.views.generic import TemplateView, ListView

from . import models
from . import forms


TABLE_HEADERS = [
            'Type', 'Transaction id', 'Protocol id',
            'Length', 'Unit id', 'Function', 'Data',
        ]
NO_CONNECTED_PLC_ERROR = 'Brak połączenia z PLC'


class IndexView(ListView):
    template_name = 'interfaces/index.html'
    model = models.Interface

class InterfaceView(TemplateView):
    """Interface view for operator"""

    template_name = 'interfaces/interface.html'
    form_class = forms.OrderForm

    def get_context_data(self, **kwargs) -> Dict[str, Any]:
        """
        Method for processing GET request
        """
        context = super().get_context_data(**kwargs)
        context['form'] = self.form_class()
        context['table_fields'] = TABLE_HEADERS
        context['status'] = NO_CONNECTED_PLC_ERROR
        context['order'] = 0
        context['amount'] = 0
        return context