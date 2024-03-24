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
import math
import requests
from random import sample
from .models import Question
from collections import defaultdict
from .models import CustomUser
from rest_framework.authentication import TokenAuthentication

from django.conf import settings
import os
import json
from random import sample
from django.db.models import IntegerField
from django.db.models.functions import Cast


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

        # Convert person_type to integer for sorting
        questions = Question.objects.annotate(person_type_int=Cast('person_type', IntegerField())).filter(person_type__range=(1, 9))

        for question in questions:
            questions_per_type.setdefault(question.person_type, []).append(question)

        selected_questions = []

        # Sort by person_type integer
        for person_type, questions in sorted(questions_per_type.items(), key=lambda x: int(x[0])):
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
        
class LocationUpdateAPIView(generics.CreateAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = LocationSerializer
    def post(self, request, *args, **kwargs):
        # Get user_id from URL parameters
        user_id = self.kwargs.get('pk')

        # Check if the user exists
        try:
            user = CustomUser.objects.get(id=user_id)
            # Update the user's location
            serializer = self.get_serializer(user, data=request.data)
        except CustomUser.DoesNotExist:
            # Create a new user with the specified location
            serializer = self.get_serializer(data={'id': user_id, **request.data})

        # Validate the serializer
        serializer.is_valid(raise_exception=True)

        # Save the location data for the user
        serializer.save()

        return Response(serializer.data, status=status.HTTP_201_CREATED)

class UserProfileView(generics.RetrieveAPIView):
    serializer_class = UserProfileSerializer

    def retrieve(self, request, *args, **kwargs):
        user_id = kwargs.get('user_id')  # Get the user_id from URL parameters
        if user_id is not None:
            try:
                user = CustomUser.objects.get(pk=user_id)  # Retrieve the user based on user_id
            except CustomUser.DoesNotExist:
                return Response({'error': 'User does not exist'}, status=status.HTTP_404_NOT_FOUND)

            serializer = self.get_serializer(user)
            return Response(serializer.data)
        else:
            return Response({'error': 'Please provide a user_id in the URL parameters'}, status=status.HTTP_400_BAD_REQUEST)





class UserLoginAPIView(APIView):
    def post(self, request, format=None):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():

            email = serializer.validated_data['email']
            password = serializer.validated_data['password']
            user = authenticate(request, email=email, password=password)
            if user:
                token, _ = Token.objects.get_or_create(user=user)
                return Response({'user_id': user.id, 'token': token.key}, status=status.HTTP_200_OK)
            
                # return Response({'user_id': user.id, 'access_token':token }, status=status.HTTP_200_OK)
            else:
                # If authentication fails, return error message
                return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

class CalculatePercentageView(APIView):

    def post(self, request):
        responses = request.data.get('responses', [])

        # Dictionary to store the sum of person_answer for each person_type
        answer_sum_per_type = defaultdict(int)

        # Iterate through responses and accumulate person_answer values
        for response in responses:
            person_type = response.get('person_type')
            person_answer = response.get('person_answer')
            answer_sum_per_type[person_type] += person_answer

        # Calculate percentage for each person type
        results = {}
        list_results = []
        max_percentage = -1  # Initialize max_percentage to a value lower than any possible percentage
        max_person_type = None  # Variable to store the person_type with the highest percentage
        for person_type, answer_sum in answer_sum_per_type.items():
            percentage = (answer_sum / (len(responses) * 9)) * 100  # Assuming each person type has 9 questions
            result = {"person_type": person_type, "result": math.ceil(percentage)}
            list_results.append(result)

            # Update max_person_type if the current percentage is higher than max_percentage
            if percentage > max_percentage:
                max_percentage = percentage
                max_person_type = person_type

        # Mark the result with the highest percentage as primary
        for result in list_results:
            if result['person_type'] == max_person_type:
                result['primary'] = True
            else:
                result['primary'] = False

        results["list_result"] = list_results
        return Response(results)