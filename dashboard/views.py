import decimal
from django.db import transaction
import requests
from typing import Any
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.db.models import Sum, Q, Subquery, OuterRef
from django.db.models.query import QuerySet
from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView, View, DetailView, CreateView
from django.urls import reverse_lazy, reverse
from django.contrib.auth.views import LoginView
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import logout, login
from .forms import CustomUserCreationForm, IncomeForm, PaymentForm, PortfolioForm, TransactionForm
from dashboard.models import Category, Income, Payment, Portfolio, Transaction, CustomUser, Transfer
from bs4 import BeautifulSoup
from datetime import datetime
from django.contrib import messages
from decimal import Decimal


@method_decorator(login_required, name='dispatch')
class HomePageView(ListView):
    template_name = 'index.html'
    context_object_name = 'categories'

    def get_queryset(self) -> QuerySet[Any]:
        if self.request.user.is_anonymous:
            return Category.objects.none()

        payment_subquery = Payment.objects.filter(category=OuterRef('pk')).order_by().values('category').annotate(
            payment_sum=Sum('summa')
        ).values('payment_sum')[:1]

        queryset = Category.objects.filter(author=self.request.user).annotate(
            payment_sum=Subquery(payment_subquery),
            income_sum=Sum('incomes__amount'),
            user_balance=Sum(
                'payments__summa', filter=Q(
                    author=self.request.user))
        )

        return queryset

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)

        total_sum = Category.objects.filter(
            author=self.request.user).aggregate(
            total_sum=Sum('payments__summa'))['total_sum']
        context['total_sum'] = total_sum

        payment_history = Payment.objects.filter(
            category__author=self.request.user).values(
            'category__name', 'summa', 'payment_date')
        context['payment_history'] = payment_history

        income_history = Income.objects.filter(
            user=self.request.user).values(
            'category__name', 'amount', 'income_date')
        context['income_history'] = income_history

        total_income = Income.objects.filter(
            user=self.request.user).aggregate(
            total_income=Sum('amount'))['total_income']
        context['total_income'] = total_income if total_income else 0

        income_categories = Category.objects.filter(
            author=self.request.user).annotate(
            payment_sum=Sum('incomes__amount'))
        context['income_categories'] = income_categories

        return context


class CategoryAddView(View):
    def get(self, request, *args, **kwargs):
        return render(request, 'category_add.html')

    def post(self, request, *args, **kwargs):
        name = request.POST.get('category')
        category = Category(name=name, author=request.user)
        category.save()
        return redirect('home')


class PaymentAddView(DetailView):
    model = Category
    template_name = 'payment_add.html'

    def get(self, request, *args, **kwargs):
        category = self.get_object()
        form = PaymentForm(category=category, user=request.user)
        return render(request, self.template_name, {
                      'category': category, 'form': form})

    def post(self, request, *args, **kwargs):
        category = self.get_object()
        form = PaymentForm(request.POST, category=category, user=request.user)

        if form.is_valid():
            payment = form.save(commit=False)
            payment.user = request.user
            payment.category = category
            portfolio = payment.portfolio
            payment.save()
            portfolio.balance -= payment.summa
            portfolio.save()
            update_user_balance(request.user, payment.summa)
            messages.success(request, 'Expense added successfully.')

            return redirect('home')
        else:
            return render(request, self.template_name, {
                          'category': category, 'form': form})


class RegisterUserView(CreateView):
    form_class = CustomUserCreationForm
    template_name = 'register.html'
    success_url = reverse_lazy('login')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = "Регистрация"
        return context

    def form_valid(self, form):
        user = form.save()
        login(self.request, user)
        return redirect('login')


class LoginUserView(LoginView):
    form_class = AuthenticationForm
    template_name = 'login.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = "Авторизация"
        return context

    def get_success_url(self):
        return reverse_lazy('home')


class IncomeListView(View):
    template_name = 'income_list.html'

    def get(self, request, *args, **kwargs):
        incomes = Income.objects.filter(user=request.user)
        return render(request, self.template_name, {'incomes': incomes})


class IncomeAddView(View):
    template_name = 'income_add.html'

    def get(self, request, *args, **kwargs):
        user = request.user
        income_categories = Category.objects.filter(author=user)
        portfolios = Portfolio.objects.filter(user=user)
        form = IncomeForm(user=user)
        return render(request, self.template_name, {
                      'income_categories': income_categories, 'portfolios': portfolios, 'form': form})

    def post(self, request, *args, **kwargs):
        user = request.user
        form = IncomeForm(user, request.POST)

        if form.is_valid():
            income = form.save(commit=False)
            income.user = user
            income.save()

            # Обновление баланса счета
            portfolio = income.portfolio
            portfolio.balance += income.amount
            portfolio.save()
            

            # Обновление общего баланса пользователя
            update_user_balance(request.user, income.amount, is_payment=False)

            return redirect('home')  # Измените на ваш путь, если необходимо
        else:
            # Вывести ошибки формы в консоль для анализа
            print(form.errors)

        income_categories = Category.objects.filter(author=user)
        portfolios = Portfolio.objects.filter(user=user)
        return render(request, self.template_name, {
                      'income_categories': income_categories, 'portfolios': portfolios, 'form': form})


def logout_user(request):
    logout(request)
    return redirect('login')


def portfolio_list(request):
    portfolios = Portfolio.objects.filter(user=request.user)
    return render(request, 'portfolio_list.html', {'portfolios': portfolios})


def transaction_list(request, portfolio_id):
    portfolio = Portfolio.objects.get(pk=portfolio_id, user=request.user)
    transactions = Transaction.objects.filter(portfolio=portfolio)

    # Получение курса валюты (здесь используется 'USD' в качестве примера, вы
    # можете заменить его на нужный код валюты)
    currency_code = portfolio.currency
    date_to_query = datetime.now()
    exchange_rate = get_currency_exchange_rate_on_date(
        currency_code, date_to_query)

    return render(request, 'transaction_list.html', {
                  'portfolio': portfolio, 'transactions': transactions, 'exchange_rate': exchange_rate})


def portfolio_create(request):
    if request.method == 'POST':
        form = PortfolioForm(request.POST)
        if form.is_valid():
            portfolio = form.save(commit=False)
            portfolio.user = request.user
            portfolio.save()
            return redirect('portfolio_list')
    else:
        form = PortfolioForm()

    return render(request, 'portfolio_create.html', {'form': form})


def portfolio_update(request, pk):
    portfolio = get_object_or_404(Portfolio, pk=pk, user=request.user)
    if request.method == 'POST':
        form = PortfolioForm(request.POST, instance=portfolio)
        if form.is_valid():
            form.save()
            return redirect('portfolio_list')
    else:
        form = PortfolioForm(instance=portfolio)

    return render(request, 'portfolio_edit.html', {
                  'form': form, 'portfolio': portfolio})


def portfolio_delete(request, pk):
    portfolio = get_object_or_404(Portfolio, pk=pk, user=request.user)
    if request.method == 'POST':

        deleted_portfolio_balance = portfolio.balance
        portfolio.delete()
        update_user_balance(request.user, deleted_portfolio_balance)

        return redirect('portfolio_list')

    return render(request, 'portfolio_delete.html', {'portfolio': portfolio})


def portfolio_edit(request, pk):
    portfolio = get_object_or_404(Portfolio, pk=pk, user=request.user)

    if request.method == 'POST':

        if form.is_valid():
            form.save()
            return redirect('portfolio_list')
    else:
        form = PortfolioForm(instance=portfolio)

    return render(request, 'portfolio_edit.html', {'portfolio': portfolio})


def get_currency_exchange_rate_on_date(currency_code, date):
    try:
        # Если код валюты 'RUB', возвращаем базовый курс (1.0)
        if currency_code == 'RUB':
            return 1.0

        # Формируем URL для запроса курса валюты на указанную дату
        url = f"http://www.cbr.ru/scripts/XML_daily.asp?date_req={date.strftime('%d/%m/%Y')}"

        # Отправляем GET-запрос и обрабатываем ошибки HTTP
        response = requests.get(url)
        response.raise_for_status()

        # Используем BeautifulSoup для парсинга XML-ответа от Центрального
        # Банка России
        soup = BeautifulSoup(response.content, 'html.parser')

        # Ищем тег 'valute' с нужным кодом валюты
        for valute_tag in soup.find_all('valute'):
            code = valute_tag.find('charcode').text
            if code == currency_code:
                rate = valute_tag.find('value').text.replace(',', '.')
                return float(rate)

        # Если код валюты не найден, вызываем исключение
        raise ValueError(
            f"Курс обмена для валюты с кодом '{currency_code}' не найден на {date.strftime('%d/%m/%Y')}")
    except requests.RequestException as req_ex:
        # Обрабатываем ошибки запроса (например, проблемы с сетью)
        print(f"Ошибка запроса: {req_ex}")
        return None
    except Exception as e:
        # Обрабатываем остальные исключения
        print(f"Ошибка в get_currency_exchange_rate_on_date: {e}")
        return None


# Пример использования:
currency_code = 'USD'  # Замените на код нужной валюты
date_to_query = datetime(2023, 12, 15)  # Замените на нужную дату

try:
    exchange_rate = get_currency_exchange_rate_on_date(
        currency_code, date_to_query)
    if exchange_rate is not None:
        print(
            f"Курс {currency_code} к рублю на {date_to_query.strftime('%d/%m/%Y')}: {exchange_rate}")
    else:
        print(
            f"Курс {currency_code} не найден на {date_to_query.strftime('%d/%m/%Y')}")
except Exception as e:
    print(f"Произошла ошибка: {e}")

# =====================================#
# Обновленный код для добавления транзакции и обновления балансов


def add_transaction(request, portfolio_id):
    portfolio = Portfolio.objects.get(pk=portfolio_id, user=request.user)

    if request.method == 'POST':
        form = TransactionForm(request.POST)
        if form.is_valid():
            transaction = form.save(commit=False)
            transaction.currency = portfolio.currency
            transaction.portfolio = portfolio
            transaction.save()

            messages.success(request, 'Транзакция успешно добавлена.')

            # Update both user balance and portfolio balance for the
            # transaction
            update_user_balance(
                request.user,
                transaction.amount,
                is_payment=False)
            update_portfolio_balance(
                portfolio, transaction.amount, is_payment=False)

            return redirect('transaction_list', portfolio_id=portfolio_id)
    else:
        form = TransactionForm()

    return render(request, 'add_transaction.html', {
                  'form': form, 'portfolio': portfolio})


# Вспомогательная функция для обновления общего баланса пользователя
def update_user_balance(user, amount, is_payment=True):
    # Получаем текущий баланс пользователя
    current_balance = user.balance
    try:
        if is_payment:
            # Если это платеж, вычитаем amount
            user.balance = Decimal(str(current_balance)) - amount
        else:
            # Если это транзакция, добавляем amount
            user.balance = Decimal(str(current_balance)) + amount

        user.save()
    except decimal.InvalidOperation as e:
        print(f"Ошибка в операции Decimal: {e}")

# Вспомогательная функция для обновления баланса портфеля


def update_portfolio_balance(portfolio, amount, is_payment=True):
    print("Updating portfolio balance...")
    # Получаем текущий баланс портфеля
    current_balance = portfolio.balance

    try:
        if is_payment:
            # Если это платеж, вычитаем amount
            portfolio.balance = Decimal(str(current_balance)) - amount
        else:
            # Если это транзакция, добавляем amount
            portfolio.balance = Decimal(str(current_balance)) + amount

        portfolio.save()
    except decimal.InvalidOperation as e:
        print(f"Ошибка в операции Decimal: {e}")


# =====================================#
class TransferView(View):
    template_name = 'transfer.html'

    def get(self, request, *args, **kwargs):
        # Получаем список портфелей пользователя
        portfolios = Portfolio.objects.filter(user=request.user)
        return render(request, self.template_name, {'portfolios': portfolios})

    def post(self, request, *args, **kwargs):
        # Получаем данные из формы POST-запроса
        sender_portfolio_id = request.POST.get('sender_portfolio')
        receiver_portfolio_id = request.POST.get('receiver_portfolio')
        amount = request.POST.get('amount')

        # Получаем портфели отправителя и получателя
        sender_portfolio = get_object_or_404(
            Portfolio, pk=sender_portfolio_id, user=request.user)
        receiver_portfolio = get_object_or_404(
            Portfolio, pk=receiver_portfolio_id, user=request.user)

        # Получаем курс обмена для валюты отправителя
        exchange_rate_sender = get_currency_exchange_rate_on_date(
            sender_portfolio.currency, datetime.now())

        # Получаем курс обмена для валюты получателя
        exchange_rate_receiver = get_currency_exchange_rate_on_date(
            receiver_portfolio.currency, datetime.now())

        try:
            # Конвертируем сумму из валюты отправителя в валюту получателя
            amount_decimal = Decimal(amount)
            exchange_rate_sender_decimal = Decimal(str(exchange_rate_sender))
            exchange_rate_receiver_decimal = Decimal(
                str(exchange_rate_receiver))

            amount_in_receiver_currency = (
                amount_decimal * exchange_rate_sender_decimal) / exchange_rate_receiver_decimal

            # Используем transaction.atomic Django для обеспечения атомарности
            # операции
            with transaction.atomic():
                # Вычитаем сумму с портфеля отправителя
                sender_portfolio.balance -= amount_decimal
                sender_portfolio.save()

                # Обновляем экземпляр sender_portfolio, чтобы получить
                # актуальное значение из базы данных
                sender_portfolio.refresh_from_db()

                # Добавляем сконвертированную сумму на портфель получателя
                receiver_portfolio.balance += amount_in_receiver_currency
                receiver_portfolio.save()

                # Сохраняем данные о переводе
                transfer = Transfer(
                    sender_portfolio=sender_portfolio,
                    receiver_portfolio=receiver_portfolio,
                    amount=amount)
                transfer.save()

            # Обновляем экземпляр receiver_portfolio, чтобы получить актуальное
            # значение из базы данных
            receiver_portfolio.refresh_from_db()

            # Выводим сообщение об успешном переводе
            messages.success(request, 'Перевод успешно выполнен.')
        except decimal.InvalidOperation as e:
            # Выводим сообщение об ошибке при конвертации валюты
            messages.error(request, f'Ошибка во время конвертации валюты: {e}')
        except Exception as e:
            # Выводим сообщение об неожиданной ошибке
            messages.error(request, f'Произошла неожиданная ошибка: {e}')

        # Перенаправляем пользователя на страницу перевода
        return redirect('transfer')
