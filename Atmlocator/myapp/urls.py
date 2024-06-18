from django.urls import path
from . import views

urlpatterns = [
    path('',views.login_signup_view,name='login'),
   path('login_signup/', views.login_signup_view, name='login_signup_view'),
    path('home/',views.home_view,name='home_view'),
    path('get_districts/', views.get_districts, name='get_districts'),
    path('select_ward/', views.select_ward, name='select_ward'),
    path('ward_population/',views.ward_population,name='ward_population')
]

