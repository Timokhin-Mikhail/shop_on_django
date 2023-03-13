from django.urls import path

from .views import (
    # ShopIndexView,
    ProductDetailsView,
    ProductsListView,
    # OrdersListView,
    # OrderDetailView,
    ProductCreateView,
    ShoppingCartDetailsView,
    ProductUpdateView,
    ProductDeleteView,
    TheMostPurchasedProductsView,
    update_products,
    ShopLictView
)

app_name = "shopapp"

urlpatterns = [
    # path("", ShopIndexView.as_view(), name="index"),
    path("stores/", ShopLictView.as_view(), name="shops_list"),
    path("products/", ProductsListView.as_view(), name="products_list"),
    path("products/create/", ProductCreateView.as_view(), name="product_create"),
    path("products/upload/", update_products, name="product_upload"),
    path("products/most_popular/", TheMostPurchasedProductsView.as_view(), name="popular_products"),
    path("products/<int:pk>/", ProductDetailsView.as_view(), name="product_details"),
    path("products/<int:pk>/update/", ProductUpdateView.as_view(), name="product_update"),
    path("products/<int:pk>/archive/", ProductDeleteView.as_view(), name="product_delete"),
    path("basket/<str:username>/", ShoppingCartDetailsView.as_view(), name="basket_details"),
    # path("orders/", OrdersListView.as_view(), name="orders_list"),
    # path("orders/<int:pk>/", OrderDetailView.as_view(), name="order_details"),
]
