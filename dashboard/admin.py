from django.contrib import admin
from dashboard.forms import CustomUserChangeForm, CustomUserCreationForm
from dashboard.models import Category, CustomUser, Payment, Portfolio, Transaction, Income


class CustomUserAdmin(admin.ModelAdmin):
    add_form = CustomUserCreationForm
    form = CustomUserChangeForm
    model = CustomUser
    list_display = ['email', 'username']


class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'author')
    search_fields = ('name', 'author__username')
    list_filter = ('author',)


class IncomeAdmin(admin.ModelAdmin):
    list_display = ('amount', 'category', 'user', 'income_date')
    search_fields = ('category__name', 'user__username')
    list_filter = ('category', 'user', 'income_date')


class PaymentAdmin(admin.ModelAdmin):
    list_display = ('summa', 'category', 'user', 'payment_date')
    search_fields = ('category__name', 'user__username')
    list_filter = ('category', 'user', 'payment_date')


class PortfolioAdmin(admin.ModelAdmin):
    list_display = ('name', 'user', 'balance', 'currency')
    search_fields = ('name', 'user__username')
    list_filter = ('user', 'currency')


class TransactionAdmin(admin.ModelAdmin):
    list_display = ('amount', 'portfolio', 'currency', 'date')
    search_fields = ('portfolio__name', 'amount', 'currency')
    list_filter = ('portfolio', 'date')


admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(Transaction, TransactionAdmin)
admin.site.register(Portfolio, PortfolioAdmin)
admin.site.register(Payment, PaymentAdmin)
admin.site.register(Income, IncomeAdmin)
admin.site.register(Category, CategoryAdmin)
