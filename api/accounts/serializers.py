from django.contrib.auth import get_user_model, password_validation
from django.db import transaction
from rest_framework import serializers
from study_preference.models import StudyPreference
from study_preference.serializers import StudyPreferenceSerializer

User = get_user_model()


class SignUpSerializer(
    serializers.Serializer
):  # nested serializer to handle the creation of a new user and their study preference
    username = serializers.CharField(max_length=150)
    email = serializers.EmailField()
    password = serializers.CharField(
        write_only=True,
        trim_whitespace=False,
    )  # fields to be expected
    study_preferences = StudyPreferenceSerializer()

    def validate_username(self, value):  # field validation for username
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError("Username already exists.")
        return value

    def validate_password(
        self, value
    ):  # password validation using Django's built-in validators
        password_validation.validate_password(value)
        return value

    @transaction.atomic  # Ensures that the user and study preference creation is atomic
    def create(
        self, validated_data
    ):  # called at .save() method of the serializer to create a new user and their study preference
        user = User.objects.create_user(  # creaete_user method is used to create a new user instance with the provided validated data
            username=validated_data["username"],
            email=validated_data["email"],
            password=validated_data["password"],
        )
        study_preference_data = validated_data.pop(
            "study_preferences"
        )  # remove the study preference
        StudyPreference.objects.create(user=user, **study_preference_data)  # create it
        return user
