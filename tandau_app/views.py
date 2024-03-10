from rest_framework import generics, permissions
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate, login, logout
from .serializers import *
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
import requests
import random
from string import digits
from random import sample
from .models import Question
from .models import CustomUser
from django.conf import settings
import os
import json
from random import sample
from django.db.models import Q
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes

from .utils import send_reset_password_email
from django.core.mail import send_mail


class LoginView(APIView):
    serializer_class = LoginSerializer
    permission_classes = [permissions.AllowAny]
    

    @swagger_auto_schema(request_body=LoginSerializer)
    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data.get('email')
            password = serializer.validated_data.get('password')
            user = authenticate(request, email=email, password=password)
            if user is not None:
                login(request, user)
                token, _ = Token.objects.get_or_create(user=user)
                return Response({'token': token.key})
            else:
                return Response({'error': 'Invalid credentials'}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class LogoutView(APIView):
    def post(self, request):
        logout(request)
        return Response({'message': 'Logged out successfully'})



@swagger_auto_schema(request_body=UserSerializer)
class RegisterView(generics.CreateAPIView):
    serializer_class = UserSerializer
    permission_classes = [permissions.AllowAny]


class SelectQuestionsView(APIView):

    def get(self, request):
        questions_per_type = {}
        for question in Question.objects.filter(person_type__range=(1, 9)):
            questions_per_type.setdefault(question.person_type, []).append(question)

        selected_questions = []

        for person_type, questions in questions_per_type.items():
            if len(questions) >= 5:
                selected_questions.extend(sample(questions, 5))
            else:
                selected_questions.extend(questions)  
        serializer = QuestionSerializer(selected_questions, many=True)
        return Response(serializer.data)


class SelectQuestionsAddView(APIView):
    serializer_class = QuestionSerializer
    permission_classes = [permissions.AllowAny]
    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_ARRAY,
            items=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'question_text_ru': openapi.Schema(type=openapi.TYPE_STRING),
                    'question_text_kz': openapi.Schema(type=openapi.TYPE_STRING),
                    'person_type': openapi.Schema(type=openapi.TYPE_INTEGER),
                    # Add other fields here if necessary
                }
            )
        )
    )
    def post(self, request):
        serializer = self.serializer_class(data=request.data, many=isinstance(request.data, list))
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LocationSchoolsApiView(APIView):
    def get(self, request, town_id, format=None):
        # URL to fetch location data for the specified ID
        url = f"https://edu-test-iam-service.azurewebsites.net/api/auth/location/school/{town_id}"

        try:
            # Send GET request to the URL
            response = requests.get(url)
            # Check if the request was successful
            if response.status_code == 200:
                # Extract JSON data from the response
                location_data = response.json()

                extracted_data = []
                

                return Response(location_data, status=status.HTTP_200_OK)
            else:
                # If the request was not successful, return an error response
                return Response({"error": "Failed to fetch location data"}, status=response.status_code)
        except Exception as e:
            # If an exception occurs during the request, return an error response
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class LocationTownsApiView(APIView):
    def get(self, request, state_id, format=None):
        # URL to fetch location data for the specified ID
        url = f"https://edu-test-iam-service.azurewebsites.net/api/auth/location/{state_id}/"

        try:
            # Send GET request to the URL
            response = requests.get(url)

            # Check if the request was successful
            if response.status_code == 200:
                # Extract JSON data from the response
                location_data = response.json()
                return Response(location_data, status=status.HTTP_200_OK)
            else:
                # If the request was not successful, return an error response
                return Response({"error": "Failed to fetch location data"}, status=response.status_code)
        except Exception as e:
            # If an exception occurs during the request, return an error response
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class LocationAPIView(APIView):
    def get(self, request, format=None):
        try:
            # Read data from the JSON file
            with open('tandau_app/location/state.json', 'r') as file:
                data = json.load(file)

            # Extract only required fields
            extracted_data = []
            for item in data:
                extracted_item = {
                    'state_id': item['id'],
                    'title_kz': item['title_kz'],
                    'title_ru': item['title_ru']
                }
                extracted_data.append(extracted_item)

            return Response(extracted_data, status=status.HTTP_200_OK)
        except Exception as e:
            current_directory = os.getcwd()
            for item in os.listdir(current_directory):
                print(item)
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        



# class ForgotPasswordView(APIView):
#     def post(self, request):
#         serializer = ForgotPasswordSerializer(data=request.data)
#         if serializer.is_valid():
#             email = serializer.validated_data['email']
#             otp = ''.join(random.choices(digits, k=6))  # Generate OTP
#             # You should associate this OTP with the user's email address for verification
#             # For now, I'll just print it for demonstration purposes.
#             # print("Generated OTP:", otp)
#             # You can also save the OTP to a database or cache for verification later

#             # Sending OTP to the user's email
#             send_reset_password_email(email, otp)
#             return Response({'message': 'An OTP has been sent to your email for password reset.'}, status=status.HTTP_200_OK)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)