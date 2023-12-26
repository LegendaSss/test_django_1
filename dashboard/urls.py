from django.urls import path
from dashboard.views import (
    HomePageView, CategoryAddView, IncomeAddView, PaymentAddView,
    RegisterUserView, LoginUserView,
    logout_user, portfolio_list, transaction_list,
    portfolio_create, portfolio_update, portfolio_delete,
    add_transaction, TransferView, IncomeListView)


urlpatterns = [
    path('', HomePageView.as_view(), name='home'),
    path('category_add/', CategoryAddView.as_view(), name='category_add'),
    path('payment_add/<int:pk>', PaymentAddView.as_view(), name='payment_add'),
    path('register/', RegisterUserView.as_view(), name='register'),
    path('login/', LoginUserView.as_view(), name='login'),
    path('logout/', logout_user, name='logout'),
    path('portfolios/', portfolio_list, name='portfolio_list'),
    path(
        'transactions/<int:portfolio_id>/',
        transaction_list,
        name='transaction_list'),
    path('portfolio/add/', portfolio_create, name='portfolio_create'),
    path('portfolio/<int:pk>/edit/', portfolio_update, name='portfolio_edit'),
    path(
        'portfolio/<int:pk>/delete/',
        portfolio_delete,
        name='portfolio_delete'),
    path('transaction/add/<int:portfolio_id>/',
         add_transaction, name='add_transaction'),
    path('transfer/', TransferView.as_view(), name='transfer'),
    path('income/add/<int:pk>/', IncomeAddView.as_view(), name='income_add'),
    path('income/list/', IncomeListView.as_view(), name='income_list'),
]
