from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('', views.home, name='home'),
    path('api/classify/', views.classify_image, name='classify_image'),
    path('api/get-recipe-by-food/', views.get_recipe_by_food, name='get_recipe_by_food'),
    path('api/model-status/', views.check_model_status, name='check_model_status'),
    path('admin/dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('admin/recipe/create/', views.recipe_create, name='recipe_create'),
    path('admin/recipe/<int:pk>/edit/', views.recipe_edit, name='recipe_edit'),
    path('admin/recipe/<int:pk>/delete/', views.recipe_delete, name='recipe_delete'),
    # Add other URL patterns as needed

    path('register/', views.register, name="register"),
    path('login/', views.user_login, name='login'),
    path('user/dashboard/', views.user_dashboard, name='user_dashboard'),  # User dashboard
    path('confirm-email/<uidb64>/<token>/', views.confirm_email, name='confirm_email'),
]

