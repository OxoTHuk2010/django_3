from django.urls import path

from apps.cart.views import (
    CartAddView,
    CartClearView,
    CartDetailView,
    CartRemoveView,
    CartUpdateView,
)

app_name = "cart"

urlpatterns = [
    path("cart/", CartDetailView.as_view(), name="detail"),
    path("cart/add/<int:product_id>/", CartAddView.as_view(), name="add"),
    path("cart/update/<int:product_id>/", CartUpdateView.as_view(), name="update"),
    path("cart/remove/<int:product_id>/", CartRemoveView.as_view(), name="remove"),
    path("cart/clear/", CartClearView.as_view(), name="clear"),
]
