import re
from rest_framework import serializers
from .models import CustomUser
from django.contrib.auth.password_validation import validate_password
from .validators import NumberValidator, UppercaseValidator, LowercaseValidator, SymbolValidator
from .models import Question


class UserProfileSerializer(serializers.ModelSerializer):
    user_id = serializers.UUIDField(source='pk', read_only=True)  # Use UUIDField if you changed to UUIDField in model

    class Meta:
        model = CustomUser
        fields = ['user_id', 'email', 'first_name', 'last_name', 'phone_number','state','town','school','classes','image']


class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        write_only=True,
        style={'input_type': 'password'}
    )
    user_id = serializers.UUIDField(source='pk', read_only=True)  # Use UUIDField if you changed to UUIDField in model



    class Meta:
        model = CustomUser
        fields = ['user_id','email', 'password', 'first_name', 'last_name', 'phone_number']
        extra_kwargs = {'password': {'write_only': True}}


    def validate(self, data):
        password = data.get('password')
        validators = [NumberValidator(), UppercaseValidator(), LowercaseValidator(), SymbolValidator()]

        for validator in validators:
            validator.validate(password)
        return data


    def create(self, validated_data):
        password = validated_data.pop('password')
        user = CustomUser.objects.create_user(password=password, **validated_data)
        return user



class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(style={'input_type': 'password'})


class LocationSerializer(serializers.ModelSerializer): 
    class Meta:
        model = CustomUser
        fields = ['state', 'town', 'school','classes']

class QuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Question
        fields = ['id', 'question_text_ru', 'question_text_kz', 'person_type']


class ForgotPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField()



class ResponseSerializer(serializers.Serializer):
    person_type = serializers.IntegerField()
    person_answer = serializers.CharField()

    def to_representation(self, instance):
        return {
            "person_type": instance['person_type'],
            "person_answer": instance['person_answer']
        }