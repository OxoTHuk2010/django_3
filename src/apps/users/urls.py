from django.contrib.auth.views import LogoutView
from django.urls import path

from apps.users.views import (
    UserLoginView,
    UserOrderDetailView,
    UserOrderListView,
    UserPasswordChangeView,
    UserProfileUpdateView,
    UserProfileView,
    UserRegisterView,
)

app_name = "users"

urlpatterns = [
    path("accounts/register/", UserRegisterView.as_view(), name="register"),
    path("accounts/login/", UserLoginView.as_view(), name="login"),
    path("accounts/logout/", LogoutView.as_view(), name="logout"),
    path("account/", UserProfileView.as_view(), name="profile"),
    path("account/edit/", UserProfileUpdateView.as_view(), name="profile_edit"),
    path("account/password/", UserPasswordChangeView.as_view(), name="password_change"),
    path("account/orders/", UserOrderListView.as_view(), name="order_list"),
    path("account/orders/<int:pk>/", UserOrderDetailView.as_view(), name="order_detail"),
]
