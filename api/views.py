import random
from decimal import Decimal
from django.shortcuts import render
from core.models import CustomUser, Profile
from api import models as api_models
from api import serializer as api_serializer
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny

class MyTokenObtainPairView(TokenObtainPairView):
    serializer_class = api_serializer.MyTokenPairSerializer
    
class RegisterView(generics.CreateAPIView):
    serializer_class = api_serializer.RegisterSrializer
    queryset = CustomUser.objects.all()
    permission_classes = [AllowAny]
    
def generate_otp(length=7):
    otp = ''.join([str(random.randint(0,9)) for _ in range(length)])
    return otp

class PasswordResetEmailVerifyApiView(generics.RetrieveAPIView):
    permission_classes = [AllowAny]
    serializer_class = api_serializer.UserSerializer
    
    def get_object(self):
        email = self.kwargs['email']
        
        user = CustomUser.objects.filter(email=email).first()
        
        if user:
            uuidb64 = user.pk
            refresh = RefreshToken.for_user(user)
            refresh_token = str(refresh.access_token)
            user.otp = generate_otp()
            user.save()
            
            
            link = f"http://localhost:5173/create-new-password/?otp={user.otp}&uuidb64={uuidb64}"
            print("link=", link)
            
        return user
    
class PasswordChangeAPIView(generics.CreateAPIView):
    permission_classes = [AllowAny]
    serializer_class = api_serializer.UserSerializer
    
    def create(self, request, *args, **kwargs):
        otp = request.data['otp']
        uuidb64 = request.data['uuidb64']
        password = request.data['password']
        
        user = CustomUser.objects.get(id=uuidb64, otp=otp)
        if user:
            user.set_password(password)
            user.otp = ""
            user.save()
            
            return Response({"message": "Password Changed Successfully"}, status=status.HTTP_201_CREATED)
        else:
            return Response({"message": "User Not Found"}, status=status.HTTP_404_NOT_FOUND)
        
class CategoryListAPIView(generics.ListAPIView):
    queryset = api_models.Category.objects.filter(active=True)
    serializer_class = api_serializer.CategorySerializer
    permission_classes = [AllowAny]
    
class CourseListAPIView(generics.ListAPIView):
    queryset = api_models.Course.objects.filter(
        platform_status="Published",
        teacher_status="Published"
    )
    serializer_class = api_serializer.CourseSerializer
    permission_classes = [AllowAny]
    
class CourseDetailAPIView(generics.RetrieveAPIView):
    serializer_class = api_serializer.CourseSerializer
    permission_classes = [AllowAny]
    queryset = api_models.Course
    
    def get_object(self):
        slug = self.kwargs['slug']
        course = api_models.Course.objects.get(slug=slug, platform_status="Published", teacher_status="Published")
        return course
    
class CartAPIView(generics.CreateAPIView):
    queryset = api_models.Cart.objects.filter().all()
    serializer_class = api_serializer.CartSerializer
    permission_classes = [AllowAny]
    
    def create(self, request, *args, **kwargs):
        course_id = request.data['course_id']
        user_id = request.data['user_id']
        price = request.data['price']
        country_name = request.data['country_name']
        cart_id = request.data['cart_id']
        
        course = api_models.Course.filter(id=course_id).first()
        
        if user_id != "undefined":
            user = CustomUser.filter(id=course_id).first()
        else:
            user = None
            
        try:
            country_object = api_models.Country.objects.filter(name="country_name").first()
            country = country_object.name
        except:
            country_object = None
            country = "United States"
            
        if country_object:
            tax_rate = country_object.tax_rate / 100
        else:
            tax_rate = 0
            
        cart = api_models.Cart.objects.filter(cart_id=cart_id, course=course).first()
        
        if cart:
            cart.course = course
            cart.user = user
            cart.price = price
            cart.tax_fee = Decimal(price) * Decimal(tax_rate)
            cart.country = country
            cart.cart_id = cart_id
            cart.total = Decimal(cart.price) + Decimal(cart.tax_fee)
            cart.save()
            
            return Response({"message": "Cart Successfully Updated"}, status=status.HTTP_200_OK)
        
        else:
            cart = api_models.Cart()
            
            cart.course = course
            cart.user = user
            cart.price = price
            cart.tax_fee = Decimal(price) * Decimal(tax_rate)
            cart.country = country
            cart.cart_id = cart_id
            cart.total = Decimal(cart.price) + Decimal(cart.tax_fee)
            cart.save()
            
            return Response({"message": "Cart Successfully Created"}, status=status.HTTP_201_CREATED)
        
        
class CartListAPIView(generics.ListAPIView):
    serializer_class = api_serializer.CartSerializer
    permission_classes = [AllowAny]
    
    def get_queryset(self):
        cart_id = self.kwargs['cart_id']
        queryset = api_models.Cart.objects.filter(cart_id=cart_id)
        return queryset
    
class CartItemDeleteAPIView(generics.DestroyAPIView):
    serializer_class = api_serializer.CartSerializer
    permission_classes = [AllowAny]
    
    def get_object(self):
        cart_id = self.kwargs['cart_id']
        item_id = self.kwargs['item_id']
        
        return api_models.Cart.objects.filter(cart_id=cart_id, item_id=item_id).first()