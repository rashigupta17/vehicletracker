from django.db import models
import uuid  # for generating uuid
import datetime

from django.contrib.postgres.fields import ArrayField
from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.auth.models import PermissionsMixin
from .managers import UserManager

# base model
class BaseModel(models.Model):
    """Base ORM model"""
    # create uuid field
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # created and updated at date
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # meta class
    class Meta:
        abstract = True

    # Time elapsed since creation
    def get_seconds_since_creation(self):
        """
        Find how much time has been elapsed since creation, in seconds.
        This function is timezone agnostic, meaning this will work even if
        you have specified a timezone.
        """
        return (datetime.datetime.utcnow() -
                self.created_at.replace(tzinfo=None)).seconds


# User model table
class User(BaseModel, AbstractBaseUser, PermissionsMixin):
    """A ORM model for Managing User and Authentication"""

    # mobile field
    mobile = models.BigIntegerField(unique=True,null =True)
    email =  models.EmailField(max_length = 254,unique=True,null = True,blank=True) 
    full_name = models.CharField(unique=True,max_length=100,null=True,blank=True)
    city = models.CharField(max_length=100,null=True,blank=True)
    dob = models.DateField(null=True,blank=True)
    password = models.CharField(max_length=100)
    gender =models.CharField(max_length=100,null=True,blank=True)
    profile_pictures =models.URLField(null=True,blank=True)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_superuser = models.BooleanField(default=False)
    is_admin = models.BooleanField(default=False)
    reset_password = models.BooleanField(default=False)
    is_dealer =models.BooleanField(default=False)
    is_agency = models.BooleanField(default=False)
    is_driver = models.BooleanField(default=False)
    
    # create objs for management
    objects = UserManager()

    # SET email field as username
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    # create a meta class
    class Meta:
        db_table= 'user'

class Verification(BaseModel):
    user = models.ForeignKey(User,on_delete=models.CASCADE)
    aadhaar = models.TextField(null=True,blank=True)
    aadhaar_verified =models.BooleanField(default=False)
    dl = models.TextField(null=True,blank=True)
    dl_verified = models.BooleanField(default=False)
    gst_no =models.TextField(null=True,blank=True)
    gst_verified = models.BooleanField(default=False)

class AgencyDetials(BaseModel):
    user =models.ForeignKey(User,on_delete=models.CASCADE)
    verification = models.ForeignKey(Verification,on_delete=models.CASCADE)
    city = models.CharField(max_length=200,null=True,blank=True)
    name = models.CharField(max_length=200,null=True,blank=True)

class DealerDetials(BaseModel):
    user =models.ForeignKey(User,on_delete=models.CASCADE)
    verification = models.ForeignKey(Verification,on_delete=models.CASCADE)
    city = models.CharField(max_length=200,null=True,blank=True)
    name = models.CharField(max_length=200,null=True,blank=True)


class DriverDetails(BaseModel):
    user = models.ForeignKey(User,on_delete=models.CASCADE)
    verification = models.ForeignKey(Verification,on_delete=models.CASCADE)
    belongs_to = models.ForeignKey(AgencyDetials,on_delete=models.CASCADE)

class Drivers(BaseModel):
    agency = models.ForeignKey(AgencyDetials,on_delete=models.CASCADE)
    drivers = models.ManyToManyField(User)

class Vehicles(BaseModel):
    agency = models.ForeignKey(AgencyDetials,on_delete=models.CASCADE)
    vehicle_type = models.TextField(null=True,blank=True)
    vehicle_number = models.TextField(null=True,blank=True)
    vehicle_rc = models.TextField(null=True,blank=True)

class Order(BaseModel):
    agency = models.ForeignKey(AgencyDetials,on_delete=models.CASCADE)
    dealer = models.ForeignKey(DealerDetials,on_delete=models.CASCADE)
    vehicles = models.ManyToManyField(Vehicles)
    drivers = models.ManyToManyField(User)
    start_date = models.DateField()
    end_date = models.DateField()
    source = models.TextField()
    destination = models.TextField()
    total_price = models.BigIntegerField()
    paid_status = models.BooleanField(default=False)
    goods_type = models.TextField()
    goods_quantity = models.TextField()

class Delivery(BaseModel):
    order = models.ForeignKey(Order,on_delete=models.CASCADE)
    order_date = models.DateField()
    order_time = models.TimeField()
    verification = models.BooleanField(default=False)
    status = models.CharField(max_length=200)

class Otp(BaseModel):
    user = models.ForeignKey(User, related_name="otp_set_user", on_delete = models.CASCADE)
    otp_type = models.CharField(max_length = 50)
    otp_code = models.IntegerField()
    is_used = models.BooleanField(default=False)

    def __str__(self):
        return str(self.otp_code)

    class Meta:
        db_table = 'OTP'

class ForgotPassword(BaseModel):
    user = models.ForeignKey(User,on_delete=models.CASCADE,default= None)
    email = models.EmailField(max_length=150,null=True, blank=True)
    mobile = models.BigIntegerField(null=True, blank=True)
    code = models.IntegerField()
    is_used = models.BooleanField(default=False)


