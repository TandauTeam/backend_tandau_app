from django.urls import path
from . import views
from rest_framework_simplejwt import views as jwt_views

urlpatterns = [


    path('profile/<str:user_id>/', views.UserProfileView.as_view(), name='user_profile'),
    path('register/location/<str:pk>', views.LocationUpdateAPIView.as_view(), name='update-location'),

    path('login/v1', jwt_views.TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('login/v1/refresh/', jwt_views.TokenRefreshView.as_view(), name='token_refresh'),
    path('login/v2', views.UserLoginAPIView.as_view(), name='user-login/v2'),

    path('logout/', views.LogoutView.as_view(), name='logout'),

    path('register/', views.RegisterView.as_view(), name='register'),

    path('questions/', views.SelectQuestionsView.as_view(), name='select-questions'),
    path('questions/add/', views.SelectQuestionsAddView.as_view(), name='add-question'),

    path('api/location/', views.LocationAPIView.as_view(), name='location-api'),
    path('api/location/<int:state_id>/', views.LocationTownsApiView.as_view(), name='location_town_by_id'),
    path('api/location/school/<int:town_id>', views.LocationSchoolsApiView.as_view(), name='location_school_by_id'),

    path('api/main/', views.MainAPIView.as_view(), name='main-page'),


    path('calculate-percentages/', views.CalculatePercentageView.as_view(), name='calculate_percentages'),
    path('api/person/',views.GetPersonView.as_view(),name='get_person_type'),
    path('add-video/', views.AddVideoView.as_view(), name='add_video'),

]
