from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.LoginView.as_view(), name='login'),
    path('logout/', views.LogoutView.as_view(), name='logout'),
    path('register/', views.RegisterView.as_view(), name='register'),
    path('questions/', views.SelectQuestionsView.as_view(), name='select-questions'),
    path('questions/add/', views.SelectQuestionsAddView.as_view(), name='add-question'),

    path('api/location/', views.LocationAPIView.as_view(), name='location-api'),
    path('api/location/<int:id>/', views.LocationTownsApiView.as_view(), name='location_town_by_id'),
    path('api/location/school/<int:id>', views.LocationSchoolsApiView.as_view(), name='location_school_by_id'),


]
