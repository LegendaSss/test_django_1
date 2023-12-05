from typing import Any
from django.db.models import Sum
from django.db.models.query import QuerySet
from django.shortcuts import render
from django.views.generic import ListView

from dashboard.models import Category

def BASE(request):
    return render(request, 'base.html')

class HomePageView(ListView):
    template_name = 'index.html'
    context_object_name = 'categories'

    def get_queryset(self) -> QuerySet[Any]:
        queryset = Category.objects.filter(author=self.request.user).prefetch_related('payments').annotate(payment_sum=Sum('payments__summa'))
        return queryset
