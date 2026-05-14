from django.contrib import admin
from django.utils import timezone

from apps.payments.models import Payment


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    """
    Административная панель платежей.
    """

    @admin.action(description="Подтвердить выбранные платежи")
    def confirm_payments(self, request, queryset) -> None:
        """
        Перевести выбранные платежи в успешный статус через Django Admin.
        """

        updated_count = queryset.update(
            status=Payment.Status.SUCCEEDED,
            paid_at=timezone.now(),
        )

        self.message_user(
            request,
            f"Подтверждено платежей: {updated_count}",
        )

    @admin.action(description="Отменить выбранные платежи")
    def cancel_payments(self, request, queryset) -> None:
        """
        Перевести выбранные платежи в статус отмены через Django Admin.
        """

        updated_count = queryset.update(
            status=Payment.Status.CANCELLED,
            paid_at=None,
        )

        self.message_user(
            request,
            f"Отменено платежей: {updated_count}",
        )

    list_display = (
        "id",
        "order",
        "status",
        "method",
        "amount",
        "currency",
        "provider",
        "provider_payment_id",
        "paid_at",
        "created_at",
    )
    list_filter = (
        "status",
        "method",
        "currency",
        "provider",
        "created_at",
        "paid_at",
    )
    search_fields = (
        "order__id",
        "provider",
        "provider_payment_id",
        "failure_reason",
    )
    readonly_fields = (
        "created_at",
        "updated_at",
    )
    ordering = ("-created_at",)
    actions = (
        "confirm_payments",
        "cancel_payments",
    )
