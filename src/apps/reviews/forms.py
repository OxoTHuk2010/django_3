from django import forms


class ReviewForm(forms.Form):
    """Форма создания пользовательского отзыва на товар."""

    rating = forms.IntegerField(
        min_value=1,
        max_value=5,
        label="Оценка",
        help_text="Оцените товар от 1 до 5.",
        widget=forms.NumberInput(
            attrs={
                "min": "1",
                "max": "5",
            },
        ),
    )
    title = forms.CharField(
        max_length=255,
        required=False,
        label="Заголовок",
        help_text="Короткий заголовок отзыва, если он нужен.",
    )
    text = forms.CharField(
        label="Текст отзыва",
        help_text="Опишите опыт покупки и использования товара.",
        widget=forms.Textarea,
    )
