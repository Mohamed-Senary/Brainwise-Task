from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status
from reviews.models import PerformanceReview
from .serializers import (
    AssignReviewSerializer,
    FeedbackSerializer,
    PerformanceReviewReadSerializer,
)
from accounts.api.permissions import (
    IsAdmin,
    IsHR,
    IsManager,
    IsEmployee
)

User = get_user_model()

@api_view(["GET"])
@permission_classes([IsAdmin | IsHR | IsManager])
def list_reviews(request):
    reviews = PerformanceReview.objects.all()

    # Optional filters
    employee_id = request.query_params.get("employee")
    if employee_id:
        reviews = reviews.filter(employee_id=employee_id)

    status_filter = request.query_params.get("status")
    if status_filter:
        reviews = reviews.filter(status=status_filter)

    serializer = PerformanceReviewReadSerializer(reviews, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)

@api_view(["GET"])
@permission_classes([IsAdmin | IsHR | IsManager])
def review_by_id(request, pk: int):
    review = get_object_or_404(PerformanceReview, pk=pk)
    serializer = PerformanceReviewReadSerializer(review)
    return Response(serializer.data, status=status.HTTP_200_OK)

@api_view(["GET"])
@permission_classes([IsEmployee])
def emp_reviews(request):
    reviews = PerformanceReview.objects.filter(employee=request.user)
    serializer = PerformanceReviewReadSerializer(reviews, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)




#INTERACTION ENDPOPINTS
#More thought out permissions
@api_view(["POST"])
@permission_classes([IsHR])
def assign_review(request):
    serializer = AssignReviewSerializer(data=request.data, context={"request": request})
    serializer.is_valid(raise_exception=True)
    review = serializer.save()
    return Response(PerformanceReviewReadSerializer(review).data, status=status.HTTP_201_CREATED)


@api_view(["PATCH"])
@permission_classes([IsEmployee])
def confirm_review(request, pk: int):
    review = get_object_or_404(PerformanceReview, pk=pk)

    # Only PENDING → SCHEDULED
    if review.status != PerformanceReview.Status.PENDING:
        return Response({"detail": "Only PENDING reviews can be confirmed."},
                        status=status.HTTP_400_BAD_REQUEST)

    review.status = PerformanceReview.Status.SCHEDULED
    review.save(update_fields=["status", "updated_at"])
    return Response(PerformanceReviewReadSerializer(review).data, status=status.HTTP_200_OK)


@api_view(["PATCH"])
@permission_classes([IsHR])
def provide_feedback(request, pk: int):
    review = get_object_or_404(PerformanceReview, pk=pk)

    # Only SCHEDULED or REJECTED → FEEDBACK_PROVIDED
    if review.status not in [PerformanceReview.Status.SCHEDULED, PerformanceReview.Status.REJECTED]:
        return Response({"detail": "Feedback allowed only when status is SCHEDULED or REJECTED."},
                        status=status.HTTP_400_BAD_REQUEST)

    serializer = FeedbackSerializer(instance=review, data=request.data)
    serializer.is_valid(raise_exception=True)
    review = serializer.save()
    return Response(PerformanceReviewReadSerializer(review).data, status=status.HTTP_200_OK)


@api_view(["PATCH"])
@permission_classes([IsHR])
def push_for_approval(request, pk: int):
    review = get_object_or_404(PerformanceReview, pk=pk)

    # Only FEEDBACK_PROVIDED → UNDER_APPROVAL
    if review.status != PerformanceReview.Status.FEEDBACK_PROVIDED:
        return Response({"detail": "Only FEEDBACK_PROVIDED reviews can be pushed for approval."},
                        status=status.HTTP_400_BAD_REQUEST)

    review.status = PerformanceReview.Status.UNDER_APPROVAL
    review.save(update_fields=["status", "updated_at"])
    return Response(PerformanceReviewReadSerializer(review).data, status=status.HTTP_200_OK)


@api_view(["PATCH"])
@permission_classes([IsManager])
def approve_review(request, pk: int):
    review = get_object_or_404(PerformanceReview, pk=pk)

    # Only UNDER_APPROVAL → APPROVED
    if review.status != PerformanceReview.Status.UNDER_APPROVAL:
        return Response({"detail": "Only UNDER_APPROVAL reviews can be approved."},
                        status=status.HTTP_400_BAD_REQUEST)

    review.status = PerformanceReview.Status.APPROVED
    review.approved_by = request.user  # server owns approver
    review.save(update_fields=["status", "approved_by", "updated_at"])
    return Response(PerformanceReviewReadSerializer(review).data, status=status.HTTP_200_OK)


@api_view(["PATCH"])
@permission_classes([IsManager])
def reject_review(request, pk: int):
    review = get_object_or_404(PerformanceReview, pk=pk)

    # Only UNDER_APPROVAL → REJECTED
    if review.status != PerformanceReview.Status.UNDER_APPROVAL:
        return Response({"detail": "Only UNDER_APPROVAL reviews can be rejected."},
                        status=status.HTTP_400_BAD_REQUEST)

    review.status = PerformanceReview.Status.REJECTED
    # (optionally clear approved_by if previously set; not needed here)
    review.save(update_fields=["status", "updated_at"])
    return Response(PerformanceReviewReadSerializer(review).data, status=status.HTTP_200_OK)
