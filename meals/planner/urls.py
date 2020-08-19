
from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("pantry/submit", views.add_items, name="add_items"),
    path("pantry/edit/<int:id>", views.edit_quantity, name="edit_quantity"),
    path("generate/<int:number>", views.generate_report, name="generate_report"),
    path("recipe/<int:id>", views.get_recipe, name="get_recipe"),
    path("error/", views.error, name="error")
]
