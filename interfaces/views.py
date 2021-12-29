from select import error
from django.shortcuts import render
from django.views.generic import TemplateView

from . import models
from . import forms


TABLE_HEADERS = [
            'Timestamp', 'Protocol id', 'Length',
            'Unit id', 'Function', 'Starting address', 'Data',
        ]
NO_CONNECTED_PLC_ERROR = 'Brak połączenia z PLC'

class InterfaceView(TemplateView):
    """Interface view for operator"""

    template_name = 'interfaces/index.html'
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
            }
        )

    def get_context_data(self, **kwargs):
        """
        Method for processing GET request
        """
        context = super().get_context_data(**kwargs)
        context['form'] = self.form_class()
        context['table_fields'] = TABLE_HEADERS
        context['status'] = NO_CONNECTED_PLC_ERROR
        return context