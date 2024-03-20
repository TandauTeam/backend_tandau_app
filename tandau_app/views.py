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
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import ValidationError
import random
from rest_framework.exceptions import ValidationError
from .validators import CustomValidationException
from string import digits
from random import sample
from .models import Question
from .models import CustomUser
from rest_framework.authentication import TokenAuthentication

from django.conf import settings
import os
import json
from random import sample
# from django.db.models import Q
# from django.contrib.auth.tokens import default_token_generator
# from django.utils.http import urlsafe_base64_encode
# from django.utils.encoding import force_bytes

# from .utils import send_reset_password_email
# from django.core.mail import send_mail


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

    def create(self, request, *args, **kwargs):
        try:
            response = super().create(request, *args, **kwargs)
            return response
        except CustomValidationException as e:
            # Handle custom validation exception
            error_detail = e.error_dict
            
            return Response(error_detail, status=status.HTTP_400_BAD_REQUEST)
        except ValidationError as e:
            # Handle other validation errors
            if 'email' in e.detail and 'user with this email address already exists.' in e.detail['email']:
                error_detail = {'detail': 'Осы электрондық пошта мекенжайы бар пайдаланушы бұрыннан бар.'}
                return Response(error_detail, status=status.HTTP_400_BAD_REQUEST)
            elif 'phone_number' in e.detail and "Телефон нөмірі форматта енгізілуі керек: '+7(***)-***-**-**'." in e.detail['phone_number']:
                error_detail = {'detail':"Телефон нөмірі форматта енгізілуі керек: '+7(***)-***-**-**'."}
                return Response(error_detail, status=status.HTTP_400_BAD_REQUEST)
            elif 'phone_number' in e.detail:
                return Response({'detail':e},status=status.HTTP_400_BAD_REQUEST)
            else:
                # For other validation errors, return the default error response
                return super().handle_exception(e)

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
        


class LocationUpdateAPIView(generics.UpdateAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = LocationUpdateSerializer

    def get_object(self):
        user_id = self.request.data.get('user_id')  # Get the user_id from request data
        try:
            return CustomUser.objects.get(id=user_id)  # Retrieve the user based on user_id
        except CustomUser.DoesNotExist:
            return None  # Return None if user does not exist

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        if instance is None:
            return Response({'error': 'User does not exist'}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data, status=status.HTTP_200_OK)

class UserProfileView(generics.RetrieveAPIView):
    serializer_class = UserProfileSerializer

    def retrieve(self, request, *args, **kwargs):
        user_id = request.data.get('user_id')  # Get the user_id from request data
        if user_id is not None:
            try:
                user = CustomUser.objects.get(pk=user_id)  # Retrieve the user based on user_id
            except CustomUser.DoesNotExist:
                return Response({'error': 'User does not exist'}, status=404)

            serializer = self.get_serializer(user)
            return Response(serializer.data)
        else:
            return Response({'error': 'Please provide a user_id in the request body'}, status=400)

class CalculatePercentagesView(APIView):
    def post(self, request, *args, **kwargs):
        serializer = ResponseSerializer(data=request.data.get('responses', []), many=True)
        if serializer.is_valid():
            responses = serializer.validated_data
            person_types = {response['person_type'] for response in responses}
            percentages = self.calculate_percentages(responses, person_types)
            return Response(percentages, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def calculate_percentages(self, responses, person_types):
        person_type_counts = {ptype: {"agree": 0, "neutral": 0, "disagree": 0, "half_agree": 0, "half_disagree": 0} for ptype in person_types}
        total_responses = len(responses)

        for response in responses:
            person_type = response['person_type']
            if person_type is not None:
                category = self.categorize_response(response['person_answer'])
                person_type_counts[person_type][category] += 1

        percentages = {}
        for ptype in person_types:
            percentages[ptype] = {}
            for category in ['agree', 'neutral', 'disagree', 'half_agree', 'half_disagree']:
                count = person_type_counts[ptype][category]
                print( count)
                percentages[ptype][category] = (count / 5) * 100 if 5 > 0 else 0

        return percentages

    def categorize_response(self, response):
        if response == 'agree':
            return 'agree'
        elif response == 'neutral':
            return 'neutral'
        elif response == 'disagree':
            return 'disagree'
        elif response == 'half_agree':
            return 'half_agree'
        elif response == 'half_disagree':
            return 'half_disagree'
        else:
            return 'unknown'




class UserLoginAPIView(APIView):
    def post(self, request, format=None):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            password = serializer.validated_data['password']
            user = CustomUser.objects.get(email=email)
            return Response({'user_id': user.id}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)