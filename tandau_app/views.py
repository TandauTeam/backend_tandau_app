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
import requests
from random import sample
from .models import *
from .models import CustomUser
from rest_framework.authentication import TokenAuthentication
from django.http import JsonResponse
from django.utils import timezone
from datetime import timedelta
from django.conf import settings
import os
from dotenv import load_dotenv
from datetime import datetime, timedelta
import json
from random import sample
from django.db.models import IntegerField
from django.db.models.functions import Cast
from .utils import *

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
        selected_question_ids = set()  # Keep track of selected question IDs

        # Sort by person_type integer
        for person_type, questions in sorted(questions_per_type.items(), key=lambda x: int(x[0])):
            if len(questions) >= 5:
                selected = sample(questions, min(5, len(questions)))  # Get a sample of 5 or all questions if less than 5
            else:
                selected = questions

            for q in selected:
                if q.id not in selected_question_ids:  # Check if question ID is not already selected
                    selected_questions.append(q)
                    selected_question_ids.add(q.id)  # Add the question ID to the set

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

    def post(self, request, *args, **kwargs):
        user_id = request.headers.get('user-id')
        if not user_id:
            return Response({'error': 'User ID missing in headers'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = CustomUser.objects.get(pk=user_id)
        except CustomUser.DoesNotExist:
            return Response({'error': 'User does not exist'}, status=status.HTTP_404_NOT_FOUND)

        # Update the user with the uploaded image
        user.image = request.data.get('image')
        user.save()

        serializer = self.get_serializer(user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

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
            
            else:
                # If authentication fails, return error message
                return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

class CalculatePercentageView(APIView):
    def post(self, request):
        user_id = request.headers['user_id']
        responses = request.data.get('responses', [])

        max_person_type = calculate_max_percentage(responses)

        if not user_id:
            return JsonResponse({"error": "User ID not provided in headers"}, status=400)

        success, user = update_user_person_type(user_id, max_person_type)
        if not success:
            return JsonResponse({"error": "User does not exist"}, status=404)

        person_info = load_person_info(max_person_type)
        if not person_info:
            return JsonResponse({"error": "Person type not found in JSON data"}, status=404)

        response_data = generate_response_data(person_info)
        return JsonResponse(response_data)
        


class MainAPIView(APIView):
    def get(self, request, format=None):
        user_id = request.headers['user_id']  # Get user_id from query parameters
        if not user_id:
            return Response({'error': 'user_id is required in query parameters'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = CustomUser.objects.get(id=user_id)  # Retrieve user object using user_id
        except CustomUser.DoesNotExist:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

        # Check if the user already has a quote generated within the last 24 hours
        last_quote = UserQuote.objects.filter(user=user, timestamp__gte=timezone.now()-timedelta(days=7)).first()
        if last_quote:
            # If a quote exists, return it
            serializer = UserQuoteSerializer(last_quote)
            collection_video = get_youtube_video(request)
            response_data = {
                        'username': f'{user.first_name} {user.last_name}',
                        'kz_quotes': serializer.data['quote'],
                        'author': serializer.data['author'],
                        'videos':collection_video}
            
            return Response(response_data)
        else:
            # Load quotes from JSON file
            with open('tandau_app/location/quotes.json', 'r') as file:
                all_quotes = json.load(file)
            
            if not all_quotes:
                return Response({}, status=status.HTTP_204_NO_CONTENT)
            else:
                # Get quotes that the user has already used
                used_quotes = UserQuote.objects.filter(user=user).values_list('quote', flat=True)
                # Filter out used quotes
                available_quotes = [quote for quote in all_quotes if quote['kz_quotes'] not in used_quotes]
                if not available_quotes:
                    return Response({}, status=status.HTTP_204_NO_CONTENT)
                else:
                    # Select a random quote from the available quotes
                    random_quote = random.choice(available_quotes)
                    # Save the selected quote for the user
                    user_quote = UserQuote.objects.create(user=user, quote=random_quote['kz_quotes'], author=random_quote['author'])
                    serializer = UserQuoteSerializer(user_quote)
                    # Return the quote along with the author
                    collection_video = get_youtube_video(request)
                    response_data = {
                        'kz_quotes': serializer.data['quote'],
                        'author': serializer.data['author'],
                        'videos':collection_video
                    }
        return Response(response_data)



class VideoView(APIView):

    def get(self,request):
        collection_videos = get_youtube_video_total(request)
        return Response(collection_videos, status=status.HTTP_200_OK)
    
    def post(self, request, format=None):
        serializer = VideoSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

class GetPersonView(APIView):
    def get(self, request):
        user_id = request.headers["user_id"]
        print(user_id)

        if not user_id:
            return JsonResponse({"error": "User ID not provided in headers"}, status=400)

        try:
            user = CustomUser.objects.get(id=user_id)
        except CustomUser.DoesNotExist:
            return JsonResponse({"error": "User does not exist"}, status=404)

        person_info = load_person_info(user.person_type)
        if not person_info:
            return JsonResponse({"error": "Person type not found in JSON data"}, status=404)

        response_data = generate_response_data(person_info)
        return JsonResponse(response_data)

