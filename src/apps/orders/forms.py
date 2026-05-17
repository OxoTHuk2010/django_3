from django import forms


class CheckoutForm(forms.Form):
    """Форма подтверждения контактных данных и адреса доставки при checkout."""

    customer_name = forms.CharField(
        label="Имя покупателя",
        max_length=255,
    )
    customer_email = forms.EmailField(
        label="Email покупателя",
    )
    customer_phone = forms.CharField(
        label="Телефон покупателя",
        max_length=32,
    )
    delivery_address = forms.CharField(
        label="Адрес доставки",
        widget=forms.Textarea(attrs={"rows": 4}),
    )
    comment = forms.CharField(
        label="Комментарий к заказу",
        required=False,
        widget=forms.Textarea(attrs={"rows": 3}),
    )

    def clean_customer_phone(self) -> str:
        """Вернуть телефон без пробелов по краям."""

        return self.cleaned_data["customer_phone"].strip()
