from django.contrib import admin
from django.urls import path
from main import views
urlpatterns = [
    path('registeruser', views.RegisterUser.as_view()),
    path('loginuser', views.LoginUser.as_view()),
    path('forgetpasswordotp', views.ForgetPasswordOTP.as_view()),
    path('forgetpasswordotpvalidation', views.ForgetPasswordOTPValidation.as_view()),
    path('forgetpasswordchange', views.ForgetPasswordChange.as_view()),
    path('sendotp/<pk>', views.SendOtp.as_view()),
    path('validateotp/<pk>', views.ValidateOtp.as_view()),

    path('createagencydetails',views.CreateAgencyDetials.as_view()),
    path('createdealerdetails',views.CreateDealerDetials.as_view()),
    path('createdriverdetails',views.CreateDriverDetails.as_view()),
    path('adddrivers',views.CreateDrivers.as_view()),
    path('addvehicles',views.CreateVehicles.as_view()),
    path('createorder',views.CreateOrder.as_view()),
    path('createdelivery',views.CreateDelivery.as_view()),

    path('rudagencydetails/<pk>',views.AgencyDetialsCrud.as_view()),
    path('ruddealerdetails/<pk>',views.DealerDetialsCrud.as_view()),
    path('ruddriverdetails/<pk>',views.DriverDetailsCrud.as_view()),
    path('ruddrivers/<pk>',views.DriversCrud.as_view()),
    path('rudvehicles/<pk>',views.VehiclesCrud.as_view()),
    path('rudorder/<pk>',views.OrderCrud.as_view()),
    path('ruddelivery/<pk>',views.DeliveryCrud.as_view()),

]