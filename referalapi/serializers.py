from decouple import config
from rest_framework import serializers

from .constants import CODE_VALIDATION_ERROR, SELF_REFERRAL_CODE_ERROR, INVALID_REFERRAL_CODE_ERROR, \
    PHONE_NUMBER_IS_NOT_VALID
from .models import User
from .rediscli import redis_client


class UserCreationSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'phone_number']
        extra_kwargs = {'phone_number': {'validators': []}}

    def validate_phone_number(self, phone_number):
        if not phone_number.isdigit():
            raise serializers.ValidationError(PHONE_NUMBER_IS_NOT_VALID)
        return phone_number


class UserProfileSerializer(serializers.ModelSerializer):
    other_user_invite_code = serializers.CharField(min_length=config('INVITE_CODE_LENGTH', cast=int, default=6),
                                                   max_length=config('INVITE_CODE_LENGTH', cast=int, default=6),
                                                   allow_blank=True, source='other_user_invite_code.my_invite_code')
    referrals = serializers.SerializerMethodField()

    def get_referrals(self, obj):
        return obj.referrals.all().values_list('phone_number', flat=True)

    def validate_other_user_invite_code(self, value):
        referrer = User.objects.filter(my_invite_code=value)
        if len(value) > 0 and not referrer.exists():
            raise serializers.ValidationError(INVALID_REFERRAL_CODE_ERROR)
        return value

    def update(self, instance, validated_data):
        referrer = User.objects.filter(my_invite_code=validated_data['other_user_invite_code']).first()
        if instance == referrer:
            raise serializers.ValidationError(SELF_REFERRAL_CODE_ERROR)
        instance.other_user_invite_code = referrer
        if validated_data.get('phone_number') is not None:
            instance.phone_number = validated_data['phone_number']
        instance.save()
        return instance

    class Meta:
        model = User
        fields = ['id', 'phone_number', 'my_invite_code', 'other_user_invite_code', 'referrals']
        read_only_fields = ['id', 'my_invite_code', 'referrals']
        extra_kwargs = {'phone_number': {'required': False}}


class EnterCodeSerializer(serializers.Serializer):
    code = serializers.CharField(required=True,
                                 min_length=config('VERIFICATION_CODE_LEN', cast=int, default=6),
                                 max_length=config('VERIFICATION_CODE_LEN', cast=int, default=6))

    def validate(self, data):
        code_from_user: str = data['code']
        phone_number: str = redis_client.get(code_from_user)
        if not phone_number:
            raise serializers.ValidationError(CODE_VALIDATION_ERROR)
        return data
