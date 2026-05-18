from django.urls import path

from apps.api.views.cart import CartClearAPIView, CartDetailAPIView, CartItemCreateAPIView, CartItemDetailAPIView
from apps.api.views.catalog import ProductDetailAPIView, ProductListAPIView
from apps.api.views.orders import OrderDetailAPIView, OrderListCreateAPIView
from apps.api.views.reviews import ProductReviewListCreateAPIView
from apps.api.views.users import UserRegistrationAPIView

app_name = "api"

urlpatterns = [
    path("products/", ProductListAPIView.as_view(), name="product-list"),
    path("products/<slug:slug>/", ProductDetailAPIView.as_view(), name="product-detail"),
    path("products/<slug:slug>/reviews/", ProductReviewListCreateAPIView.as_view(), name="product-review-list-create"),
    path("cart/", CartDetailAPIView.as_view(), name="cart-detail"),
    path("cart/items/", CartItemCreateAPIView.as_view(), name="cart-item-create"),
    path("cart/items/<int:product_id>/", CartItemDetailAPIView.as_view(), name="cart-item-detail"),
    path("cart/clear/", CartClearAPIView.as_view(), name="cart-clear"),
    path("orders/", OrderListCreateAPIView.as_view(), name="order-list"),
    path("orders/<int:pk>/", OrderDetailAPIView.as_view(), name="order-detail"),
    path("users/register/", UserRegistrationAPIView.as_view(), name="user-register"),
]
