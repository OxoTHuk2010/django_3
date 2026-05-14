from unittest.mock import Mock

import pytest
from django.contrib import admin
from django.contrib.admin.sites import AdminSite
from django.test import RequestFactory

from apps.cart.models import Cart, CartItem
from apps.catalog.admin import ProductAdmin
from apps.catalog.models import Category, Product, ProductImage
from apps.orders.admin import OrderAdmin
from apps.orders.models import Order, OrderItem
from apps.payments.admin import PaymentAdmin
from apps.payments.models import Payment
from apps.reviews.models import Review
from apps.users.models import User

pytestmark = pytest.mark.django_db


def make_admin_request():
    """Создать минимальный request для прямого вызова admin action."""
    return RequestFactory().get("/admin/")


def build_model_admin(admin_class, model):
    """Создать изолированный ModelAdmin и заглушить отправку сообщений пользователю."""
    model_admin = admin_class(model, AdminSite())
    model_admin.message_user = Mock()
    return model_admin


def test_main_models_are_registered_in_admin_site():
    """Все ключевые модели этапа 5 зарегистрированы в Django Admin."""
    registered_models = admin.site._registry

    assert User in registered_models
    assert Category in registered_models
    assert Product in registered_models
    assert ProductImage in registered_models
    assert Cart in registered_models
    assert CartItem in registered_models
    assert Order in registered_models
    assert OrderItem in registered_models
    assert Payment in registered_models
    assert Review in registered_models


def test_product_admin_can_activate_products(product):
    """Action `activate_products` массово включает выбранные товары."""
    product.is_active = False
    product.save(update_fields=["is_active"])

    model_admin = build_model_admin(ProductAdmin, Product)
    request = make_admin_request()

    model_admin.activate_products(
        request,
        Product.objects.filter(pk=product.pk),
    )
    product.refresh_from_db()

    assert product.is_active is True
    model_admin.message_user.assert_called_once()


def test_product_admin_can_deactivate_products(product):
    """Action `deactivate_products` массово выключает выбранные товары."""
    product.is_active = True
    product.save(update_fields=["is_active"])

    model_admin = build_model_admin(ProductAdmin, Product)
    request = make_admin_request()

    model_admin.deactivate_products(
        request,
        Product.objects.filter(pk=product.pk),
    )
    product.refresh_from_db()

    assert product.is_active is False
    model_admin.message_user.assert_called_once()


def test_order_admin_can_cancel_orders(order):
    """Action `cancel_orders` переводит выбранные заказы в статус отмены."""
    order.status = Order.Status.PROCESSING
    order.save(update_fields=["status"])

    model_admin = build_model_admin(OrderAdmin, Order)
    request = make_admin_request()

    model_admin.cancel_orders(
        request,
        Order.objects.filter(pk=order.pk),
    )
    order.refresh_from_db()

    assert order.status == Order.Status.CANCELLED
    model_admin.message_user.assert_called_once()


def test_payment_admin_can_confirm_payments(payment):
    """Action `confirm_payments` подтверждает платежи и фиксирует время оплаты."""
    payment.status = Payment.Status.PENDING
    payment.paid_at = None
    payment.save(update_fields=["status", "paid_at"])

    model_admin = build_model_admin(PaymentAdmin, Payment)
    request = make_admin_request()

    model_admin.confirm_payments(
        request,
        Payment.objects.filter(pk=payment.pk),
    )
    payment.refresh_from_db()

    assert payment.status == Payment.Status.SUCCEEDED
    assert payment.paid_at is not None
    model_admin.message_user.assert_called_once()


def test_payment_admin_can_cancel_payments(payment):
    """Action `cancel_payments` отменяет платежи и очищает дату оплаты."""
    payment.status = Payment.Status.SUCCEEDED
    payment.save(update_fields=["status"])

    model_admin = build_model_admin(PaymentAdmin, Payment)
    request = make_admin_request()

    model_admin.cancel_payments(
        request,
        Payment.objects.filter(pk=payment.pk),
    )
    payment.refresh_from_db()

    assert payment.status == Payment.Status.CANCELLED
    assert payment.paid_at is None
    model_admin.message_user.assert_called_once()
