from typing import Dict, Any

from django.shortcuts import render
from django.views.generic import TemplateView

from . import models
from . import forms


TABLE_HEADERS = [
            'Type', 'Transaction id', 'Protocol id',
            'Length', 'Unit id', 'Function', 'Data',
        ]
NO_CONNECTED_PLC_ERROR = 'Brak połączenia z PLC'


class IndexView(TemplateView):
    template_name = 'interfaces/index.html'

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        interfaces = models.Interface.objects.all()
        kwargs['interfaces'] = interfaces
        return super().get_context_data(**kwargs)

class InterfaceView(TemplateView):
    """Interface view for operator"""

    template_name = 'interfaces/interface.html'
    model = models.Order
    form_class = forms.OrderForm
    
    def post(self, request, *args, **kwargs):
        """
        Method for processing POST request
        """
        print(kwargs)
        form = forms.OrderForm(request.POST)
        return render(
            request,
            self.template_name,
            {
                'form': form,
                'table_fields': TABLE_HEADERS,
                'status': NO_CONNECTED_PLC_ERROR,
                'order': 0,
                'amount': 0
            }
        )

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