from django.db import models

from apps.common.models import TimeStampedModel
from apps.orders.models import Order


class Payment(TimeStampedModel):
    """
    Платёж по заказу.

    Модель хранит не саму банковскую карту и не чувствительные платёжные данные,
    а только безопасную информацию о платёжной операции.

    Важные принципы:
    - не храним номер карты;
    - не храним CVV;
    - не храним полный ответ платёжного провайдера, если там могут быть секреты;
    - сохраняем внешний идентификатор платежа для сверки с платёжной системой;
    - допускаем несколько платежей на один заказ.
    """

    class Status(models.TextChoices):
        """
        Возможные статусы платежа.
        """

        PENDING = "pending", "Ожидает оплаты"
        SUCCEEDED = "succeeded", "Успешно оплачен"
        FAILED = "failed", "Ошибка оплаты"
        CANCELLED = "cancelled", "Отменён"
        REFUNDED = "refunded", "Возвращён"

    class Method(models.TextChoices):
        """
        Способы оплаты.

        На старте это просто справочник значений.
        Реальную интеграцию с платёжными шлюзами возможно будет позже,
        когда будет готов базовый API заказов.
        """

        CARD = "card", "Банковская карта"
        CASH = "cash", "Наличные"
        SBP = "sbp", "СБП"
        OTHER = "other", "Другое"

    order = models.ForeignKey(
        Order,
        on_delete=models.PROTECT,
        related_name="payments",
        verbose_name="Заказ",
        help_text="Заказ, к которому относится платёж.",
    )
    status = models.CharField(
        max_length=32,
        choices=Status.choices,
        default=Status.PENDING,
        verbose_name="Статус платежа",
        help_text="Текущий статус платёжной операции.",
    )
    method = models.CharField(
        max_length=32,
        choices=Method.choices,
        default=Method.CARD,
        verbose_name="Способ оплаты",
        help_text="Способ, выбранный пользователем для оплаты заказа.",
    )
    amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        verbose_name="Сумма платежа",
        help_text="Сумма, которую пользователь должен оплатить или оплатил.",
    )
    currency = models.CharField(
        max_length=3,
        default="RUB",
        verbose_name="Валюта",
        help_text="Валюта платежа в формате ISO 4217, например RUB.",
    )

    provider = models.CharField(
        max_length=64,
        blank=True,
        verbose_name="Платёжный провайдер",
        help_text="Название платёжного провайдера, например yookassa, tinkoff, sberbank.",
    )
    provider_payment_id = models.CharField(
        max_length=255,
        blank=True,
        verbose_name="ID платежа у провайдера",
        help_text="Внешний идентификатор платежа в системе платёжного провайдера.",
    )

    paid_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Дата оплаты",
        help_text="Дата и время успешной оплаты.",
    )
    failure_reason = models.TextField(
        blank=True,
        verbose_name="Причина ошибки",
        help_text="Описание причины неуспешной оплаты, если она известна.",
    )

    class Meta:
        verbose_name = "Платёж"
        verbose_name_plural = "Платежи"
        ordering = [
            "-created_at",
        ]
        indexes = [
            models.Index(
                fields=[
                    "order",
                    "status",
                ],
                name="payments_order_status_idx",
            ),
            models.Index(
                fields=[
                    "status",
                    "created_at",
                ],
                name="payments_status_date_idx",
            ),
            models.Index(
                fields=[
                    "provider",
                    "provider_payment_id",
                ],
                name="payments_provider_id_idx",
            ),
        ]
        constraints = [
            models.CheckConstraint(
                condition=models.Q(
                    amount__gte=0,
                ),
                name="payments_amount_gte_0",
            ),
        ]

    def __str__(self) -> str:
        """
        Строковое представление платежа.
        """

        return f"Платёж #{self.id} по заказу #{self.order_id}"

    @property
    def is_successful(self) -> bool:
        """
        Проверить, является ли платёж успешным.
        """

        return self.status == self.Status.SUCCEEDED

    @property
    def is_final(self) -> bool:
        """
        Проверить, находится ли платёж в финальном статусе.

        Финальные статусы:
        - успешная оплата;
        - ошибка;
        - отмена;
        - возврат.
        """

        return self.status in {
            self.Status.SUCCEEDED,
            self.Status.FAILED,
            self.Status.CANCELLED,
            self.Status.REFUNDED,
        }
