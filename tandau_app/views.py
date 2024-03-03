from rest_framework import generics, permissions
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate, login, logout
from .serializers import UserSerializer,LoginSerializer, QuestionSerializer
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from random import sample
from .models import Question

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
        # Query all questions grouped by person type
        questions_per_type = {}
        for question in Question.objects.all():
            questions_per_type.setdefault(question.person_type, []).append(question)

        selected_questions = []

        # Select 5 questions from each type
        for person_type, questions in questions_per_type.items():
            if len(questions) >= 5:
                selected_questions.extend(sample(questions, 5))
            else:
                selected_questions.extend(questions)  # Select all available questions if less than 5

        # Serialize the selected questions
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