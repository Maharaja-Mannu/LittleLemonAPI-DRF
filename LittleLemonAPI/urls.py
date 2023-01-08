from django.urls import path
from . import views
from rest_framework.authtoken.views import obtain_auth_token

urlpatterns = [
    path("welcome", views.welcome),
    path("menu", views.menu),
    # path("menu-items", views.MenuItemsView.as_view()),
    path("menu-items", views.menu_items, name="menu-items"),
    path("menu-items/<int:pk>", views.SingleMenuItemView.as_view()),
    path("category", views.category, name="category"),
    path("category/<int:pk>", views.category_detail, name="category-detail"),
    path("secret", views.secret),
    path("api-token-auth", obtain_auth_token),
]
