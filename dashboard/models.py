from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.db import models
from datetime import datetime


class CustomUser(AbstractUser):
    email = models.EmailField(unique=True)
    balance = models.DecimalField('Общий баланс в рублях', max_digits=10, decimal_places=2, default=0)

    def __str__(self):
        return self.email

class AccountType(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name


class Category(models.Model):
    name = models.CharField('Название', max_length=100)
    author = models.ForeignKey(CustomUser, on_delete=models.CASCADE, verbose_name='Хозяин' )

    def __str__(self) -> str:
        return self.name
    
    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'


class Portfolio(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, null=True, verbose_name='Владелец')
    name = models.CharField(max_length=30, verbose_name= 'Имя')
    currency = models.CharField(max_length=3, choices=[('RUB', 'RUB'), ('EUR', 'EUR'), ('USD', 'USD')], default='RUB', verbose_name='валюта')
    account_type = models.ForeignKey(AccountType, on_delete=models.SET_NULL, null=True, blank=True)
    balance = models.DecimalField('Баланс в валюте', max_digits=10, decimal_places=2, default=0)

    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name = 'Портфолио'
        verbose_name_plural = 'Портфолио'


class Payment(models.Model):
    category = models.ForeignKey(
        'Category',
        on_delete=models.CASCADE,
        related_name='payments', verbose_name='Категории'
    )
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, verbose_name='Владелец', null=True)
    portfolio = models.ForeignKey(Portfolio, on_delete=models.CASCADE, verbose_name='Портфель')
    summa = models.DecimalField('Сумма', max_digits=10, decimal_places=2)
    payment_date = models.DateField('Дата платежа', default=datetime.today)
    comment = models.TextField('Комментарий', blank=True, null=True)
    currency = models.CharField('Валюта', max_length=3, choices=[('RUB', 'RUB'), ('EUR', 'EUR'), ('USD', 'USD')], default='RUB')

    class Meta:
        verbose_name = 'Платеж'
        verbose_name_plural = 'Платежи'
  

class Transaction(models.Model):
    trans_name = models.CharField(max_length=30, verbose_name='Имя транзакции')
    portfolio = models.ForeignKey(Portfolio, on_delete=models.CASCADE, verbose_name='Портфолио')
    account_type = models.ForeignKey(AccountType, on_delete=models.SET_NULL, null=True, blank=True)
    trans_type = models.CharField(max_length=20, verbose_name='Тип транзакции')
    amount = models.DecimalField(verbose_name='Сумма транзакции', max_digits=10, decimal_places=2)
    amount_rub = models.DecimalField(verbose_name='Сумма транзакции в рублях', max_digits=10, decimal_places=2, null=True, blank=True)
    date = models.DateField(verbose_name='Дата транзакции')
    currency = models.CharField(max_length=3, choices=[('RUB', 'RUB'), ('EUR', 'EUR'), ('USD', 'USD')], default='RUB', verbose_name='Валюта')
    
    
    def __str__(self):
        return self.trans_name
    

    class Meta:
        verbose_name = 'Транзакция'
        verbose_name_plural = 'Транзакции'


class Transfer(models.Model):
    sender_portfolio = models.ForeignKey(Portfolio, on_delete=models.CASCADE, related_name='sender_transfers')
    receiver_portfolio = models.ForeignKey(Portfolio, on_delete=models.CASCADE, related_name='receiver_transfers')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=3, choices=[('RUB', 'RUB'), ('EUR', 'EUR'), ('USD', 'USD')])
    date = models.DateField(default=datetime.today)

    def __str__(self):
        return f"{self.sender_portfolio} -> {self.receiver_portfolio}: {self.amount} {self.currency}"




class Income(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, verbose_name='Владелец', null=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='incomes', verbose_name='Категории')
    portfolio = models.ForeignKey(Portfolio, on_delete=models.CASCADE, related_name='incomes', null=True, blank=True, verbose_name='Портфолио')
    amount = models.DecimalField('сумма', max_digits=10, decimal_places=2)
    income_date = models.DateField('Дата дохода', default=datetime.today)
    currency = models.CharField('Валюта', max_length=3, choices=[('RUB', 'RUB'), ('EUR', 'EUR'), ('USD', 'USD')], default='RUB')

    class Meta:
        verbose_name = 'Доход'
        verbose_name_plural = 'Доходы'

       