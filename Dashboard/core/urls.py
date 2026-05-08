from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard_home, name='dashboard_home'),
    path('edit/<str:guild_id>/', views.edit_guild_config, name='edit_guild_config'),
]
