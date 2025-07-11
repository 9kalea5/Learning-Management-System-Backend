import random
from decimal import Decimal
from django.shortcuts import render
from django.contrib.auth.hashers import check_password
from django.db import models
from core.models import CustomUser, Profile
from api import models as api_models
from api import serializer as api_serializer
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from datetime import datetime, timedelta

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
        
class ChangePasswordAPIView(generics.CreateAPIView):
    serializer_class = api_serializer.UserSerializer
    permission_classes = [AllowAny]
    
    def create(self, request, *args, **kwargs):
        user_id = request.data['user_id']
        old_password = request.data['old_password']
        new_password = request.data['new_password']
        
        user = CustomUser.objects.get(id=user_id)
        if user is not None:
            if check_password(old_password, user.password):
                user.set_password(new_password)
                user.save()
                return Response({"message": "Password changed successfully", "icon": "success"})
            else:
                return Response({"message": "Old password is incorrect", "icon": "warning"})
        else:
            return Response({"message": "User does not exists", "icon": "error"})
        
class ProfileAPIView(generics.RetrieveUpdateAPIView):
    serializer_class = api_serializer.ProfileSerializer
    permission_classes = [AllowAny]

    def get_object(self):
        try:
            user_id = self.kwargs['user_id']
            user = CustomUser.objects.get(id=user_id)
            return Profile.objects.get(user=user)
        except:
            return None
        
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
        
        return api_models.Cart.objects.filter(cart_id=cart_id, id=item_id).first()
    
class CartStatsAPIView(generics.RetrieveAPIView):
    serializer_class = api_serializer.CartSerializer
    permission_classes = [AllowAny]
    lookup_field = 'cart_id'
    
    def get_queryset(self):
        cart_id = self.kwargs['cart_id']
        queryset = api_models.Cart.objects.filter(cart_id=cart_id)
        return queryset
    
    def get(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        
        total_price = 0.00
        total_tax = 0.00
        total_total = 0.00
        
        for cart_item in queryset:
            total_price += float(self.calculate_price(cart_item))
            total_tax += float(self.calculate_tax(cart_item))
            total_total += round(float(self.calculate_total(cart_item)), 2)
            
        data = {
            "price": total_price,
            "tax": total_tax,
            "total": total_total
        }
            
        return Response(data)
        
    def calculate_price(self, cart_item):
        return cart_item.price
    
    def calculate_tax(self, cart_item):
        return cart_item.tax_fee
    
    def calculate_total(self, cart_item):
        return cart_item.total

class CreateOrderAPIView(generics.CreateAPIView):
    serializer_class = api_serializer.CartOrderSerializer
    permission_class = [AllowAny]
    queryset = api_models.CartOrder.objects.all()
    
    def create(self, request, *args, **kwargs):
        full_name = request.data['full_name']
        email = request.data['email']
        country = request.data['country']
        cart_id = request.data['cart_id']
        user_id = request.data['user_id']
        
        if user_id != 0:
            user = CustomUser.objects.get(id=user_id)
        else:
            user = None
            
        cart_items = api_models.Cart.objects.filter(cart_id=cart_id)
        
        total_price = Decimal(0.00)
        total_tax = Decimal(0.00)
        total_initial_total = Decimal(0.00)
        total_total = Decimal(0.00)
        
        order = api_models.CartOrder.objects.create(
            full_name=full_name,
            email=email,
            country=country,
            student=user
        )
        
        for c in cart_items:
            api_models.CartOrderItem.objects.create(
                order=order,
                course=c.course,
                price=c.price,
                tax_fee=c.tax_fee,
                total=c.total,
                initial_total=c.total,
                teacher=c.course.teacher
            )
            
            total_price += Decimal(c.price)
            total_tax += Decimal(c.tax_fee)
            total_initial_total += Decimal(c.total)
            total_total += Decimal(c.total)
            
            order.teachers.add(c.course.teacher)
            
        order.sub_total = total_price
        order.tax_fee = total_tax
        order.initial_total = total_initial_total
        order.total = total_total
        order.save()
        
        return Response({"message": "Order Created Succcessfully"}, status=status.HTTP_201_CREATED)
    
class CheckoutAPIView(generics.RetrieveAPIView):
    serializer_class = api_serializer.CartOrderSerializer
    permission_classes = [AllowAny]
    queryset = api_models.CartOrder.objects.all()
    lookup_field = 'oid'
    
class CouponApplyAPIView(generics.CreateAPIView):
    serializer_class = api_serializer.CouponSerializer
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        order_oid = request.data['order_oid']
        coupon_code = request.data['coupon_code']

        order = api_models.CartOrder.objects.get(oid=order_oid)
        coupon = api_models.Coupon.objects.filter(code=coupon_code).first()

        if coupon:
            order_items = api_models.CartOrderItem.objects.filter(order=order, teacher=coupon.teacher)
            for i in order_items:
                if not coupon in i.coupons.all():
                    discount = i.total * coupon.discount / 100

                    i.total -= discount
                    i.price -= discount
                    i.saved += discount
                    i.applied_coupon = True
                    i.coupons.add(coupon)

                    order.coupons.add(coupon)
                    order.total -= discount
                    order.sub_total -= discount
                    order.saved += discount

                    i.save()
                    order.save()
                    coupon.used_by.add(order.student)
                    return Response({"message": "Coupon Found and Activated", "icon": "success"}, status=status.HTTP_201_CREATED)
                else:
                    return Response({"message": "Coupon Already Applied", "icon": "warning"}, status=status.HTTP_200_OK)
        else:
            return Response({"message": "Coupon Not Found", "icon": "error"}, status=status.HTTP_404_NOT_FOUND)
        
class StudentSummaryAPIView(generics.ListAPIView):
        serializer_class = api_serializer.StudentSummarySerializer
        permission_classes = [AllowAny]
        
        def get_queryset(self):
            user_id = self.kwargs['user_id']
            user = CustomUser.objects.get(id=user)        
            
            total_courses = api_models.EnrolledCourse.objects.filter(user=user).count()
            completed_lessons = api_models.CompletedLesson.objects.filter(user=user).count()
            achieved_certificates = api_models.Certificate.objects.filter(user=user).count()
            
            return [{
                "total_courses": total_courses,
                "completed_lessons": completed_lessons,
                "achieved_certificates": achieved_certificates,
            }]
            
        def list(self, request, *args, **kwargs):
            queryset = self.get_queryset()
            serializer = self.get_serializer(queryset, many=True)
            return Response(serializer.data)
        
class StudentCourseListAPIView(generics.ListAPIView):
    serializer_class = api_serializer.EnrolledCourseSerializer
    permission_classes = [AllowAny]
    
    def get_queryset(self):
        user_id = self.kwargs['user_id']
        user = CustomUser.objects.get(id=user_id)
        
        return api_models.EnrolledCourse.objects.filter(user=user)
    
class StudentCourseDetailAPIView(generics.RetrieveAPIView):
    serializer_class = api_serializer.EnrolledCourseSerializer
    permission_classes = [AllowAny]
    lookup_field = 'enrollment_field'
    
    def get_object(self):
        user_id = self.kwargs['user_id']
        enrollment_id = self.kwargs['enrollment_id']
        
        user = CustomUser.objects.get(id=user_id)
        return api_models.EnrolledCourse.objects.get(user=user, enrollment_id=enrollment_id)
    
class StudentCourseCompletedCreateAPIView(generics.CreateAPIView):
    serializer_class = api_serializer.CompletedLessonSerializer
    permission_classes = [AllowAny]
    
    def create(self, request, *args, **kwargs):
        user_id = request.data['user_id']
        course_id = request.data['course_id']
        variant_item_id = request.data['variant_item_id']
        
        user = CustomUser.objects.get(id=user_id)
        course = api_models.Course.objects.get(id=course_id)
        variant_item = api_models.VariantItem,object.get(variant_item_id=variant_item_id)
        
        completed_lessons = api_models.CompletedLesson.objects.filter(user=user, course=course, variant_item=variant_item)
        
        if completed_lessons:
            completed_lessons.delete()
            return Response({"message": "Course marked as not completed"})
        
        else:
            api_models.CompletedLesson.objects.create(user=user, course=course, variant_item=variant_item)
            return Response({"message": "Course marked as completed"})
        
class StudentNoteCreateAPIView(generics.CreateAPIView):
    serializer_class =api_serializer.NoteSerializer
    permission_classes = [AllowAny]
    
    def create(self, request, *args, **kwargs):
        user_id =request.data['user_id']
        enrollment_id = request.data['enrollment_id']
        title = request.data['title']
        note = request.data['note']
        
        user = CustomUser.objects.get(id=user_id)
        enrolled = api_models.EnrolledCourse.objects.get(enrollment_id=enrollment_id)
        
        api_models.Note.objects.create(user=user, course=enrolled.course, note=note, title=title)
        
        return Response({"message": "Note created successfully"}, status=status.HTTP_201_CREATED)
    
class StudentNoteDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = api_serializer.NoteSerializer
    permission_classes = [AllowAny]
    
    def get_queryset(self):
        user_id = self.kwargs['user_id']
        enrollment_id = self.kwargs['enrollment_id']
        
        user = CustomUser.objects.get(id=user_id)
        enrolled = api_models.EnrolledCourse.objects.get(enrollment_id=enrollment_id)
        
        return api_models.Note.objects.filter(user=user, course=enrolled.course)
        
    def get_object(self):
        user_id = self.kwargs['user_id']
        enrollment_id = self.kwargs['enrollment_id']
        note_id = self.kwargs['note_id']
        
        user = CustomUser.objects.get(id=user_id)
        enrolled = api_models.EnrolledCourse.objects.get(enrollment_id=enrollment_id)
        note = api_models.Note.objects.get(user=user, course=enrolled.course, id=note_id)
        return note
    
class StudentRateCourseAPIView(generics.CreateAPIView):
    serializer_class = api_serializer.ReviewSerializer
    permission_classes = [AllowAny]
    
    def create(self, request, *args, **kwargs):
        user_id = request.data['user_id']
        course_id = request.data['course_id']
        rating = request.data['rating']
        review = request.data['review']
        
        user = CustomUser.objects.get.get(id=user_id)
        course = api_models.Course.objects.get(id=course_id)
        
        api_models.Review.objects.create(
            user=user,
            course=course,
            review=review,
            rating=rating
        )
        
        return Response({"message": "Review created successfully"}, status=status.HTTP_201_CREATED)

class StudentRateDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = api_serializer.ReviewSerializer
    permission_classes = [AllowAny]
    
    def get_object(self):
        user_id = self.kwargs['user_id']
        review_id = self.kwargs['review_id']
        
        user = CustomUser.objects.get(id=user_id)
        return api_models.Review.objects.get(id=review_id, user=user)
    
class StudentWishListListCreateAPIView(generics.ListCreateAPIView):
    serializer_class = api_serializer.WishlistSerializer
    permission_classes = [AllowAny]
    
    def get_queryset(self):
        user_id = self.kwargs['user_id']
        user = CustomUser.objects.get(id=user_id)
        return api_models.Wishlist.objects.filter(user=user)
    
    def create(self, request, *args, **kwargs):
        user_id = request.data['user_id']
        course_id = request.data['course_id']
        
        user = CustomUser.objects.get(id=user_id)
        course = api_models.Course.objects.get(id=course_id)
        
        wishlist = api_models.Wishlist.objects.filter(user=user, course=course).first()
        if wishlist:
            wishlist.delete()
            return Response({"message": "Wishlist deleted"}, status=status.HTTP_200_OK)
        
        else:
            api_models.Wishlist.objects.create(
                user=user, course=course, 
            )
            
            return Response({"message": "Wishlist created"}, status=status.HTTP_201_CREATED)
        
class QuestionListCreateAPIView(generics.ListCreateAPIView):
    serializer_class = api_serializer.Question_AnswerSerializer
    permission_classes = [AllowAny]
    
    def get_queryset(self):
        course_id = self.kwargs['course_id']
        course = CustomUser.objects.get(id=course_id)
        return api_models.Wishlist.objects.filter(course=course)
    
    def create(self, request, *args, **kwargs):
        user_id = request.data['user_id']
        course_id = request.data['course_id']
        title = request.data['title']
        message = request.data['message']
        
        user = CustomUser.objects.get(id=user_id)
        course = api_models.Course.objects.get(id=course_id)
        
        question = api_models.Question_Answer.objects.create(user=user, course=course, title=title)
        
        api_models.Question_Answer_Message.objects.create(user=user, course=course, message=message, question=question)
        
        return Response({"message": "Group conversation started"}, status=status.HTTP_201_CREATED)
        
        
class QuestionAnserMessageSendAPIView(generics.CreateAPIView):
    serializer_class = api_serializer.Question_Answer_MessageSerializer
    permission_classes = [AllowAny]
    
    def create(self, request, *args, **kwargs):
        course_id = request.data['course_id']
        qa_id = request['qa-id']
        user_id = request.data['user_id']
        message = request.data['message']
        
        user = CustomUser.objects.get(id=user_id)
        course = api_models.Course.objects.get(id=course_id)
        
        question = api_models.Question_Answer.objects.get(qa_id=qa_id)
        
        api_models.Question_Answer_Message.objects.create(user=user, course=course, message=message, question=question)
        
        question_serializer = api_serializer.Question_AnswerSerializer(question)
        return Response({"message": "Message Sent","question": question_serializer})
    
class TeacherSummaryAPIView(generics.ListAPIView):
    serializer_class = api_serializer.TeacherSummarySerializer
    permission_classes = [AllowAny]
    
    def get_queryset(self):
        teacher_id = self.kwargs['teacher_id']
        teacher = api_models.Teacher.objects.get(id=teacher_id)

        one_month_ago = datetime.today() - timedelta(days=28)

        total_courses = api_models.Course.objects.filter(teacher=teacher).count()

        total_revenue = api_models.CartOrderItem.objects.filter(
            teacher=teacher,
            order__payment_status="Paid"
        ).aggregate(total=models.Sum("Price"))['total'] or 0

        monthly_revenue = api_models.CartOrderItem.objects.filter(
            teacher=teacher,
            order__payment_status="Paid",
            date__gte=one_month_ago
        ).aggregate(total=models.Sum("Price"))['total'] or 0

        enrolled_courses = api_models.EnrolledCourse.objects.filter(teacher=teacher)
        unique_student_ids = set()
        students = []

        for course in enrolled_courses:
            if course.user_id not in unique_student_ids:
                user = CustomUser.objects.get(id=course.user_id)
                students.append({
                    "full_name": user.profile.full_name,
                    "image": user.profile.image.url if user.profile.image else None,
                    "country": user.profile.country,
                    "date": user.profile.date,
                })
                unique_student_ids.add(course.user_id)

        return [{
            "total_courses": total_courses,
            "total_revenue": total_revenue,
            "monthly_revenue": monthly_revenue,
            "total_students": len(students),
        }]

        
    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)