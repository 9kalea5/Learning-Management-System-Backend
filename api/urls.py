from api import views as api_views
from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView

urlpatterns = [
    path("user/token/", api_views.MyTokenObtainPairView.as_view),
    path("user/token/refresh/", TokenRefreshView.as_view()),
    path("user/register/", api_views.RegisterView.as_view()),
    path("user/password-reset-email/<email>/", api_views.PasswordResetEmailVerifyApiView.as_view()),
    path("user/password-change/", api_views.PasswordChangeAPIView.as_view()),
    path("user/profile/<user_id>/", api_views.PasswordChangeAPIView.as_view()),
    path("user/change-password/", api_views.ChangePasswordAPIView.as_view()),


    path("course/category/", api_views.CategoryListAPIView.as_view()),
    path("course/course-list/", api_views.CourseListAPIView.as_view()),
    path("course/course-detail/<slug>/", api_views.CourseDetailAPIView.as_view()),
    path("course/cart/", api_views.CartAPIView.as_view()),
    path("course/cart-list/<cart_id>/", api_views.CartListAPIView.as_view()),
    path("course/cart-item-delete/<cart_id>/<item_id>/", api_views.CartItemDeleteAPIView.as_view()),
    path("cart/stats/<cart_id>/", api_views.CartStatsAPIView.as_view()),
    path("order/create-order/", api_views.CreateOrderAPIView.as_view()),
    path("order/check_out/<oid>/", api_views.CheckoutAPIView.as_view()),
    path("order/coupon/", api_views.CouponApplyAPIView.as_view()),
    
    path("student/summary/<user_Id/", api_views.StudentSummaryAPIView.as_view()),
    path("student/course-list/<user-id>/", api_views.StudentCourseListAPIView.as_view()),
    path("student/course-list/<user-id>/<enrolment_id>/", api_views.StudentCourseDetailAPIView.as_view()),
    path("student/course-completed/", api_views.StudentCourseCompletedCreateAPIView.as_view()),
    path("student/course-note/<user_id>/<enrollment_id>/", api_views.StudentNoteCreateAPIView.as_view()), 
    path("student/course-note/", api_views.StudentNoteCreateAPIView.as_view()),
    path("student/course-note-detail/<user_id>/<enrollment_id>/<note_id>/", api_views.StudentNoteDetailAPIView.as_view()),
    path("student/rate-course/", api_views.StudentRateCourseAPIView.as_view()),
    path("student/rate-detail/<user_id>/<review_id>/", api_views.StudentRateDetailAPIView.as_view()),
    path("student/wishlist/<user_id>/", api_views.StudentWishListListCreateAPIView.as_view()),
    path("student/question-answer-list-create/<course_id>/", api_views.QuestionListCreateAPIView.as_view()),
    path("student/question-answer-message-create/<course_id>/", api_views.QuestionAnserMessageSendAPIView.as_view()),
    
    path("teacher/summary/<teacher_id>/", api_views.TeacherSummaryAPIView.as_view()),
]