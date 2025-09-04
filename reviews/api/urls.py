from django.urls import path
from .views import (
    list_reviews,
    review_by_id,
    assign_review,
    confirm_review,
    provide_feedback,
    push_for_approval,
    approve_review,
    reject_review,
    emp_reviews
)

urlpatterns = [
    path("", list_reviews, name="review-list"),              
    path("<int:pk>/", review_by_id, name="review-detail"),  
    path("emp-reviews/", emp_reviews, name="emp-reviews"), 

    # Workflow/action endpoints
    path("assign/", assign_review, name="review-assign"),                
    path("<int:pk>/confirm/", confirm_review, name="review-confirm"),      
    path("<int:pk>/feedback/", provide_feedback, name="review-feedback"),  
    path("<int:pk>/push/", push_for_approval, name="review-push"),         
    path("<int:pk>/approve/", approve_review, name="review-approve"),      
    path("<int:pk>/reject/", reject_review, name="review-reject"),         
]
