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
        print(kwargs)
        form = forms.OrderForm(request.POST)
        if form.is_valid():
            order = form.save(commit=False)
            order.interface = models.Interface.objects.get(name=kwargs['interface_name'])
            order.status = models.Status.objects.get(status='requested')
            order.completed_amount = 0
            order.save()
            form = forms.OrderForm()
            return render(request, self.template_name, {'form': form})

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