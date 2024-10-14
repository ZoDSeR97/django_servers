from django.urls import path, include
from .views import (
    start_cash_payment,
    check_payment_status,
    reset_bill_acceptor,
    stop_cash_payment,
    create_cash_payment,
    get_mac_address,
)

urlpatterns = [
    path('start/', start_cash_payment, name='start_cash_payment'),
    path('status/', check_payment_status, name='check_payment_status'),
    path('reset/', reset_bill_acceptor, name='reset_bill_acceptor'),
    path('stop/', stop_cash_payment, name='stop_cash_payment'),
    path('create/', create_cash_payment, name='create_cash_payment'),
    path('mac-address/', get_mac_address, name='get_mac_address'),
]