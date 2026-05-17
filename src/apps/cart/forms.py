from django import forms


class CartQuantityForm(forms.Form):
    """Форма количества товара для операций добавления и изменения корзины."""

    quantity = forms.IntegerField(
        min_value=1,
        required=True,
        error_messages={
            "required": "Укажите количество товара.",
            "invalid": "Количество должно быть числом.",
            "min_value": "Количество должно быть больше нуля.",
        },
    )
