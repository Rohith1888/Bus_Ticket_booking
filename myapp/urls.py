from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name="home"),
    path('findbus', views.findbus, name="findbus"),
    path('bookings', views.bookings, name="bookings"),
    path('cancellings', views.cancellings, name="cancellings"),
    path('seebookings', views.seebookings, name="seebookings"),
    path('register', views.signup, name="register"),
    path('signin', views.signin, name="signin"),
    path('success', views.success, name="success"),
    path('signout', views.signout, name="signout"),
    path('admin_dash',views.admin_dash,name="admin_dash"),
    path('seat_confirmation',views.seat_confirmation,name="seat_confirmation"),
    path('seat_selection/<int:bus_id>/', views.seat_selection, name='seat_selection'),


]
