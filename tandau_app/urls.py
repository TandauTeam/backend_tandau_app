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

    # path('forgot-password/', views.ForgotPasswordView.as_view(), name='forgot_password'),
    path('register/', views.RegisterView.as_view(), name='register'),

    path('questions/', views.SelectQuestionsView.as_view(), name='select-questions'),
    path('questions/add/', views.SelectQuestionsAddView.as_view(), name='add-question'),

    path('api/location/', views.LocationAPIView.as_view(), name='location-api'),
    path('api/location/<int:state_id>/', views.LocationTownsApiView.as_view(), name='location_town_by_id'),
    path('api/location/school/<int:town_id>', views.LocationSchoolsApiView.as_view(), name='location_school_by_id'),

    path('random-user-quote/', views.RandomUserQuoteView.as_view(), name='random-user-quote'),


    path('calculate-percentages/', views.CalculatePercentageView.as_view(), name='calculate_percentages'),

    path('add-video/', views.AddVideoView.as_view(), name='add_video'),
    
    # path('api/select/',views.UserLocationCreateView.as_view(), name='user_location')

]
