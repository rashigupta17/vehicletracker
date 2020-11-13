from rest_framework import serializers
from django.contrib.auth.hashers import make_password
import re
from .models import *

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'

    def validate_password(self, str) -> str:
        """ A function to save the password for storing the values """
        return make_password(str)

class VerificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Verification
        fields = '__all__'
class AgencyDetialsSerializer(serializers.ModelSerializer):
    class Meta:
        model = AgencyDetials
        fields = '__all__'
class DealerDetialsSerializer(serializers.ModelSerializer):
    class Meta:
        model = DealerDetials
        fields = '__all__'
class DriverDetailsSerializer(serializers.ModelSerializer):
    class Meta:
        model = DriverDetails
        fields = '__all__'
class DriversSerializer(serializers.ModelSerializer):
    class Meta:
        model = Drivers
        fields = '__all__'
class VehiclesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Vehicles
        fields = '__all__'
class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = '__all__'

class DeliverySerializer(serializers.ModelSerializer):
    class Meta:
        model = Delivery
        fields = '__all__'
class ForgotPasswordSerializer(serializers.ModelSerializer):
    class Meta:
        model = ForgotPassword
        fields= '__all__'

class OtpSerializer(serializers.ModelSerializer):
    class Meta:
        model = Otp
        fields = '__all__'
