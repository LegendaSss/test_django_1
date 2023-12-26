from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import Category, CustomUser, Income, Payment, Portfolio, Transaction


class CustomUserCreationForm(UserCreationForm):
    username = forms.CharField(label='Логин', widget=forms.TextInput)
    email = forms.EmailField(label='Email')
    password1 = forms.CharField(label='Пароль', widget=forms.PasswordInput)
    password2 = forms.CharField(
        label='Повторите пароль',
        widget=forms.PasswordInput)

    class Meta(UserCreationForm):
        model = CustomUser
        fields = ('email', 'username', 'password1', 'password2')


class CustomUserChangeForm(UserChangeForm):

    class Meta:
        model = CustomUser
        fields = ('email', 'username')


class PortfolioForm(forms.ModelForm):
    currency = forms.ChoiceField(
        choices=[('RUB', 'RUB'), ('EUR', 'EUR'), ('USD', 'USD')], label='Валюта')

    class Meta:
        model = Portfolio
        fields = ['name', 'currency']


class TransactionForm(forms.ModelForm):
    amount = forms.DecimalField(
        label='Сумма транзакции',
        max_digits=10,
        decimal_places=2)
    category = forms.ModelChoiceField(
        queryset=Category.objects.all(),
        label='Категория')
    portfolio = forms.ModelChoiceField(
        queryset=Portfolio.objects.all(), label='Портфель')
    trans_name = forms.CharField(label='Имя транзакции')
    trans_type = forms.CharField(label='Тип транзакции')
    date = forms.DateField(
        label='Дата транзакции',
        widget=forms.TextInput(
            attrs={
                'type': 'date'}))

    class Meta:
        model = Transaction
        fields = [
            'trans_name',
            'trans_type',
            'amount',
            'date',
            'category',
            'portfolio']


class IncomeForm(forms.ModelForm):
    amount = forms.DecimalField(label='Сумма', max_digits=10, decimal_places=2)
    category = forms.ModelChoiceField(
        queryset=Category.objects.all(),
        label='Категория')
    portfolio = forms.ModelChoiceField(
        queryset=Portfolio.objects.all(), label='Портфель')
    income_date = forms.DateField(
        label='Дата дохода',
        widget=forms.TextInput(
            attrs={
                'type': 'date'}))
    currency = forms.ChoiceField(
        choices=[('RUB', 'RUB'), ('EUR', 'EUR'), ('USD', 'USD')], label='Валюта')

    class Meta:
        model = Income
        fields = ['category', 'portfolio', 'amount', 'income_date', 'currency']

    def __init__(self, user, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['category'].queryset = Category.objects.filter(author=user)
        self.fields['portfolio'].queryset = Portfolio.objects.filter(user=user)


class PaymentForm(forms.ModelForm):
    summa = forms.DecimalField(
        label='Сумма транзакции',
        max_digits=10,
        decimal_places=2,
        widget=forms.TextInput(
            attrs={
                'placeholder': 'Введите сумму'}))
    date = forms.DateField(
        label='Дата транзакции',
        widget=forms.TextInput(
            attrs={
                'type': 'date',
                'placeholder': 'Выберите дату'}))
    portfolio = forms.ModelChoiceField(
        queryset=Portfolio.objects.all(),
        widget=forms.Select(
            attrs={
                'placeholder': 'Выберите портфель'}))
    category = forms.ModelChoiceField(
        queryset=Category.objects.all(),
        widget=forms.Select(
            attrs={
                'placeholder': 'Выберите категорию'}))

    class Meta:
        model = Payment
        fields = ['summa', 'date', 'portfolio', 'category']

    def __init__(self, *args, **kwargs):
        category = kwargs.pop('category', None)
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if category:
            self.fields['portfolio'].queryset = Portfolio.objects.filter(
                user=category.author)
            self.fields['category'].initial = category
        elif user:
            self.fields['portfolio'].queryset = Portfolio.objects.filter(
                user=user)
            self.fields['category'].queryset = Category.objects.filter(
                author=user)
