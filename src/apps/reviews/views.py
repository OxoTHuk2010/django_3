from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from django.views import View

from apps.catalog.selectors import get_product_detail_queryset
from apps.reviews.forms import ReviewForm
from apps.reviews.services import ReviewCreateError, create_product_review


class ProductReviewCreateView(LoginRequiredMixin, View):
    """HTTP-слой создания отзыва на товар."""

    def post(self, request, slug: str):
        """Проверить форму, создать отзыв через service-layer и вернуть пользователя к товару."""

        product = get_object_or_404(
            get_product_detail_queryset(),
            slug=slug,
        )
        redirect_url = f"{reverse('catalog:product_detail', kwargs={'slug': product.slug})}#reviews"
        form = ReviewForm(request.POST)

        if not form.is_valid():
            messages.error(request, "Проверьте оценку и текст отзыва.")
            return redirect(redirect_url)

        try:
            create_product_review(
                user=request.user,
                product=product,
                rating=form.cleaned_data["rating"],
                title=form.cleaned_data["title"],
                text=form.cleaned_data["text"],
            )
        except ReviewCreateError as exc:
            messages.error(request, str(exc))
            return redirect(redirect_url)

        messages.success(request, "Отзыв отправлен и будет опубликован после проверки.")
        return HttpResponseRedirect(redirect_url)
