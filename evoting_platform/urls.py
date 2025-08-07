"""
URL configuration for evoting_platform project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from evoting_platform.accounts import views

urlpatterns = [
    # Django admin
    path('django-admin/', admin.site.urls),  # Changed to avoid conflict with custom admin
    
    # Public pages
    path('', views.landing_page, name='landing'),
    path('login/', views.auth_page, name='login'),
    path('contact/', views.contact_page, name='contact'),
    
    # Authentication
    path('register/', views.register, name='register'),
    path('do_login/', views.do_login, name='do_login'),
    path('logout/', views.logout_view, name='logout'),
    
    # Protected pages
    path('admin/', views.admin_page, name='admin_page'),
    path('voter/', views.voter_page, name='voter_page'),
    path('results/', views.results_page, name='results'),
]
