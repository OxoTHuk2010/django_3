from django.urls import path

from apps.reviews.views import ProductReviewCreateView

app_name = "reviews"

urlpatterns = [
    path(
        "reviews/products/<slug:slug>/add/",
        ProductReviewCreateView.as_view(),
        name="product_review_add",
    ),
]
