from django.shortcuts import render
from random import randint
import string 
import random 
import boto3,base64
from datetime import datetime

from django.shortcuts import render
from django.db.models import Q,Count
from django.contrib.auth import authenticate, login
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import generics, status, permissions, filters
from django.core.mail import send_mail
from .viewsets import DetailsAPI,CreateAttribute,PaginationList
from .models import *
from .serializers import *
def responsedata(status, message, data=None):
    if status:
        return {"status":status,"message":message,"data":data}
    else:
        return {"status":status,"message":message,}
class RegisterUser(APIView):

    token_obtain_pair = TokenObtainPairView.as_view()

    def post(self, request):
        if request.data.get('mobile'):
            if User.objects.filter(mobile=request.data.get('mobile')).exists():
                return Response(responsedata(False, "User already present"), status=status.HTTP_400_BAD_REQUEST)
        if User.objects.filter(email=request.data.get('email')).exists():
            return Response(responsedata(False, "User Email already present"), status=status.HTTP_400_BAD_REQUEST)
        if request.data.get("confirm_password") != request.data.get("password"):
            return Response(responsedata(False, "Password Does Not Match!!"), status=status.HTTP_400_BAD_REQUEST)
        if request.data:
            data = request.data
            serializer = UserSerializer(data=data)        
            if serializer.is_valid(raise_exception=True):
                serializer.save()  
            user_data = serializer.data
            number = str(randint(10000,99999))
            data = {"user":serializer.data['uuid'],'otp_type':'mobile', 'otp_code':int(number) }
            serializer = OtpSerializer(data=data,partial=True)
            if serializer.is_valid(raise_exception=True):
                serializer.save()    
                msg = 'Your OTP is ' + number
                data = serializer.data
                user_data['verification_data']=self.__populate_data(user_data['uuid'],request)
                return Response(responsedata(True, "Data Inserted",user_data), status=status.HTTP_200_OK)
        return Response(responsedata(False, "No Data provided"), status=status.HTTP_400_BAD_REQUEST)

    def __populate_data(self,user,request) -> None:
    # get user data for notification type
        request.data['user'] = user
        #take user notification ojects if already exists
        serializer = VerificationSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
        data = serializer.data
        return data

            
class LoginUser(TokenObtainPairView):
    """To login club user using email/mobile and password"""

    token_obtain_pair = TokenObtainPairView.as_view()

    def post(self, request, *args, **kwargs):
        
        if not request.data.get("password"):
            return Response(responsedata(False, "Password is required"), status=status.HTTP_400_BAD_REQUEST)

        if not User.objects.filter(email=request.data.get('email')).exists():
            return Response(responsedata(False, "No user found"), status=status.HTTP_400_BAD_REQUEST)
        
        if not User.objects.get(email=request.data.get('email')).check_password(request.data.get("password")):
            return Response(responsedata(False, "Incorrect Password"), status=status.HTTP_400_BAD_REQUEST)
        
        if request.data.get('email'):
            user = User.objects.get(email=request.data.get('email'))
            request.data['uuid'] = user.uuid
            user = authenticate(email=request.data.get('email'), password=request.data.get('password'))
            login(request,user)
        serializer = TokenObtainPairSerializer(data=request.data)

        if serializer.is_valid(raise_exception=True):
            data = serializer.validate(request.data)
            data['user'] = User.objects.filter(uuid=request.data.get('uuid')).values()
            return Response(responsedata(True, "Sign in Successful", data), status=status.HTTP_200_OK)
        return Response(responsedata(False, "Something went wrong"), status=status.HTTP_400_BAD_REQUEST)

class ForgetPasswordOTP(APIView):

    def post(self, request):
        if request.data.get('mobile'):
            if not User.objects.filter(mobile=request.data.get("mobile")).exists():
                return Response(responsedata(False, "No user  found"), status=status.HTTP_400_BAD_REQUEST)
            user =User.objects.filter(mobile=request.data.get("mobile")).values().first()
            number = str(randint(1000, 9999))

            data = {"user":user['uuid'],"code":int(number), "mobile":request.data.get("mobile")}
            serializer = ForgotPasswordSerializer(data=data)
            if serializer.is_valid(raise_exception=True):
                try:
                    serializer.save()
                    contact = request.data.get('mobile')
                    msg = 'Your OTP is ' + number
                    return Response(responsedata(True, "OTP Sent Successfully", {"fr":msg}), status=status.HTTP_200_OK)
                except:
                    return Response(responsedata(False, "Cant send sms"), status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response(responsedata(False, "Please provide mobile number "), status=status.HTTP_400_BAD_REQUEST)

class ForgetPasswordOTPValidation(APIView):
    """To check if OTP is correct or not"""

    def post(self, request):

        if request.data.get('code'):
            data = request.data
            setup = ForgotPassword.objects.filter(mobile=data.get('mobile'),code=data.get('code'),is_used=False).first()
            if not setup:
                return Response(responsedata(False, "otp provided is incorrect"), status=status.HTTP_400_BAD_REQUEST)
            else:
                try:
                    val = {"is_used": True}
                    serializer = ForgotPasswordSerializer(setup,data=val,partial=True)
                    if serializer.is_valid(raise_exception=True):
                        serializer.save()
                    return Response(responsedata(True, "Correct OTP"), status=status.HTTP_200_OK)
                except:
                    return Response(responsedata(False, "Something Went Wrong"), status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response(responsedata(False, "Otp not provided"), status=status.HTTP_400_BAD_REQUEST)

class ForgetPasswordChange(APIView):

    "To reset passsword if don't recall the present one"

    def put(self, request):
        if not request.data.get('new_password') or not request.data.get('confirm_password'):
            return Response(responsedata(False, "Enter all the fields"), status=status.HTTP_400_BAD_REQUEST)

        if (request.data.get('new_password') !=  request.data.get('confirm_password')):
            return Response(responsedata(False, "Password doesn't match"), status=status.HTTP_400_BAD_REQUEST)
        user = User.objects.get(mobile=request.data.get('mobile'))
        if request.data.get('mobile'):
            data = {"password":request.data['new_password'],'mobile_verified':True}

        serializer = UserSerializer(user, data=data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(responsedata(True, "Password Updated",200), status=status.HTTP_200_OK)
        else:
            return Response(responsedata(False, "Something went wrong",500), status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class SendOtp(APIView):
    """To send otp to  mobile"""

    def post(self, request, pk):
        
        if request.data.get('mobile'):
            number = str(randint(10000,99999))
            data = {"user":request.user.uuid,'otp_type':'mobile', 'otp_code':int(number) }
            serializer = OtpSerializer(data=data,partial=True)
            if serializer.is_valid(raise_exception=True):
                try:
                    serializer.save()
                    contact = request.data.get('mobile')
                    msg = 'Your OTP is ' + number
                    return Response(responsedata(True, "OTP Sent Successfully",{"msg":msg}), status=status.HTTP_200_OK)
                except:
                    return Response(responsedata(False, "Cant send message"), status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class ValidateOtp(APIView):
    """To check if OTP is correct or not"""

    def post(self, request, pk):

        if request.data.get('otp_code'):
            data = request.data
            setup = Otp.objects.get(user = request.user.uuid,otp_code=data.get('otp_code'),is_used=False)
            if not setup:
                return Response(responsedata(False, "otp provided is incorrect"), status=status.HTTP_400_BAD_REQUEST)
            else:
                try:
                    val = {"is_used": True}
                    serializer = OtpSerializer(setup,data=val,partial=True)
                    if serializer.is_valid(raise_exception=True):
                        serializer.save()
                    return Response(responsedata(True, "Correct OTP"), status=status.HTTP_200_OK)
                except:
                    return Response(responsedata(False, "Something Went Wrong"), status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response(responsedata(False, "OTP not provided"), status=status.HTTP_400_BAD_REQUEST)


class UserProfile(DetailsAPI):
    model_class = User
    serializer_class = UserSerializer
    permission_classes = [permissions.AllowAny]
    instance_name = 'User'

class AgencyDetialsCrud(DetailsAPI):
    model_class = AgencyDetials
    serializer_class = AgencyDetialsSerializer
    permission_classes = [permissions.AllowAny]
    instance_name = 'AgencyDetials'

class CreateAgencyDetials(CreateAttribute):
    model_class = AgencyDetials
    serializer_class = AgencyDetialsSerializer
    permission_classes = [permissions.AllowAny]
    instance_name = 'AgencyDetials'

class AgencyDetialsList(PaginationList):
    model_class = AgencyDetials
    serializer_class = AgencyDetialsSerializer
    permission_classes = [permissions.AllowAny]
    instance_name = 'AgencyDetials'

class DealerDetialsCrud(DetailsAPI):
    model_class = DealerDetials
    serializer_class = DealerDetialsSerializer
    permission_classes = [permissions.AllowAny]
    instance_name = 'DealerDetials'

class CreateDealerDetials(CreateAttribute):
    model_class = DealerDetials
    serializer_class = DealerDetialsSerializer
    permission_classes = [permissions.AllowAny]
    instance_name = 'DealerDetials'

class DealerDetialsList(PaginationList):
    model_class = DealerDetials
    serializer_class = DealerDetialsSerializer
    permission_classes = [permissions.AllowAny]
    instance_name = 'DealerDetials'


class DriverDetailsCrud(DetailsAPI):
    model_class = DriverDetails
    serializer_class = DriverDetailsSerializer
    permission_classes = [permissions.AllowAny]
    instance_name = 'DriverDetails'

class CreateDriverDetails(CreateAttribute):
    model_class = DriverDetails
    serializer_class = DriverDetailsSerializer
    permission_classes = [permissions.AllowAny]
    instance_name = 'DriverDetails'

class DriverDetailsList(PaginationList):
    model_class = DriverDetails
    serializer_class = DriverDetailsSerializer
    permission_classes = [permissions.AllowAny]
    instance_name = 'DriverDetails'

class DriversCrud(DetailsAPI):
    model_class = Drivers
    serializer_class = DriversSerializer
    permission_classes = [permissions.AllowAny]
    instance_name = 'Drivers'

class CreateDrivers(CreateAttribute):
    model_class = Drivers
    serializer_class = DriversSerializer
    permission_classes = [permissions.AllowAny]
    instance_name = 'Drivers'

class DriversList(PaginationList):
    model_class = Drivers
    serializer_class = DriversSerializer
    permission_classes = [permissions.AllowAny]
    instance_name = 'Drivers'


class OrderCrud(DetailsAPI):
    model_class = Order
    serializer_class = OrderSerializer
    permission_classes = [permissions.AllowAny]
    instance_name = 'Order'

class CreateOrder(CreateAttribute):
    model_class = Order
    serializer_class = OrderSerializer
    permission_classes = [permissions.AllowAny]
    instance_name = 'Order'

class OrderList(PaginationList):
    model_class = Order
    serializer_class = OrderSerializer
    permission_classes = [permissions.AllowAny]
    instance_name = 'Order'


class DeliveryCrud(DetailsAPI):
    model_class = Delivery
    serializer_class = DeliverySerializer
    permission_classes = [permissions.AllowAny]
    instance_name = 'Delivery'

class CreateDelivery(CreateAttribute):
    model_class = Delivery
    serializer_class = DeliverySerializer
    permission_classes = [permissions.AllowAny]
    instance_name = 'Delivery'

class DeliveryList(PaginationList):
    model_class = Delivery
    serializer_class = DeliverySerializer
    permission_classes = [permissions.AllowAny]
    instance_name = 'Delivery'

class VehiclesCrud(DetailsAPI):
    model_class = Vehicles
    serializer_class = VehiclesSerializer
    permission_classes = [permissions.AllowAny]
    instance_name = 'Vehicles'

class CreateVehicles(CreateAttribute):
    model_class = Vehicles
    serializer_class = VehiclesSerializer
    permission_classes = [permissions.AllowAny]
    instance_name = 'Vehicles'

class VehiclesList(PaginationList):
    model_class = Vehicles
    serializer_class = VehiclesSerializer
    permission_classes = [permissions.AllowAny]
    instance_name = 'Vehicles'
