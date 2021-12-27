from django.shortcuts import render
from django.views.generic import TemplateView

from . import models
from . import forms


class InterfaceView(TemplateView):
    """Interface view for operator"""

    template_name = 'interfaces/index.html'
    model = models.Order
    form_class = forms.OrderForm
    
    def post(self, request, *args, **kwargs):
        """
        Method for processing POST request
        """
        print(args)
        print(kwargs)
        print(request.POST)

    def get_context_data(self, **kwargs):
        """
        Method for processing GET request
        """
        context = super().get_context_data(**kwargs)
        context['form'] = self.form_class()
        context['table_fields'] = [
            'Timestamp', 'Transaction id', 'Protocol id', 'Length',
            'Unit id', 'Function', 'Starting address', 'Quantity',
        ]
        return context