from rest_framework import serializers
from django.contrib.auth import authenticate
from .models import CustomUser

class UserSerializer(serializers.ModelSerializer):
    can_predict = serializers.SerializerMethodField()
    quota_status = serializers.SerializerMethodField()

    class Meta:
        model = CustomUser
        fields = [
            'id', 'email', 'full_name', 'phone_number',
            'preferred_market', 'preferred_currency', 'preferred_gold_unit',
            'subscription_tier', 'is_pro_or_higher', 'credits_remaining',
            'predictions_used_today', 'can_predict', 'quota_status',
            'telegram_chat_id', 'whatsapp_number', 'created_at'
        ]
        read_only_fields = ['id', 'subscription_tier', 'is_pro_or_higher', 'credits_remaining', 'predictions_used_today', 'created_at']

    def get_can_predict(self, obj):
        can, _ = obj.can_make_prediction()
        return can

    def get_quota_status(self, obj):
        _, msg = obj.can_make_prediction()
        return msg


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)

    class Meta:
        model = CustomUser
        fields = ['email', 'password', 'full_name', 'phone_number', 'preferred_market', 'preferred_currency', 'preferred_gold_unit']

    def create(self, validated_data):
        password = validated_data.pop('password')
        user = CustomUser.objects.create_user(password=password, **validated_data)
        return user


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        email = data.get('email')
        password = data.get('password')
        user = authenticate(email=email, password=password)
        if not user:
            raise serializers.ValidationError("Invalid email or password.")
        if not user.is_active:
            raise serializers.ValidationError("Account is disabled.")
        data['user'] = user
        return data
