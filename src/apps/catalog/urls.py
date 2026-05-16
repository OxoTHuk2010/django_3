from django.urls import path

from apps.catalog.views import HomeView, ProductListView

app_name = "catalog"

urlpatterns = [
    path("", HomeView.as_view(), name="home"),
    path("products/", ProductListView.as_view(), name="product_list"),
]
