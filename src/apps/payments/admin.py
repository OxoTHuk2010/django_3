from django.contrib import admin

from apps.payments.models import Payment


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    """
    Административная панель платежей.
    """

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
