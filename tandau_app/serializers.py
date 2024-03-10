from rest_framework import serializers
from .models import CustomUser
from django.contrib.auth.password_validation import validate_password
from .validators import NumberValidator, UppercaseValidator, LowercaseValidator, SymbolValidator
from .models import Question

class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        max_length=20,
        min_length=8,
        write_only=True,
        style={'input_type': 'password'}
    )

    class Meta:
        model = CustomUser
        fields = ['email', 'password', 'first_name', 'last_name', 'phone_number']
        extra_kwargs = {'password': {'write_only': True}}

    def validate_password(self, value):
        validators = [
            NumberValidator(),
            UppercaseValidator(),
            LowercaseValidator(),
            SymbolValidator(),
        ]

        for validator in validators:
            validator.validate(value)

        return value

    def create(self, validated_data):
        password = validated_data.pop('password')
        user = CustomUser.objects.create_user(password=password, **validated_data)
        return user


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(style={'input_type': 'password'})



class QuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Question
        fields = ['id', 'question_text_ru', 'question_text_kz', 'person_type']


class ForgotPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField()



class UserLocationSerializer(serializers.Serializer):
    school_id = serializers.IntegerField()
    state_id = serializers.IntegerField()