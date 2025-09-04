from rest_framework import serializers
from django.contrib.auth import get_user_model
from reviews.models import PerformanceReview

User = get_user_model()


class PerformanceReviewReadSerializer(serializers.ModelSerializer):
    # Convenience read-only fields
    employee_email = serializers.ReadOnlyField(source="employee.email")
    assigner_email = serializers.ReadOnlyField(source="assigner.email")
    approved_by_email = serializers.ReadOnlyField(source="approved_by.email")

    class Meta:
        model = PerformanceReview
        fields = [
            "id",
            "employee", "employee_email",
            "assigner", "assigner_email",
            "approved_by", "approved_by_email",
            "scheduled_at",
            "feedback",
            "status",
            "created_at",
            "updated_at",
        ]
        read_only_fields = fields  # fully read-only serializer for responses


class AssignReviewSerializer(serializers.ModelSerializer):
    """
    Used by HR to create a new review.
    Only accepts `employee` (server fills `assigner` and keeps status=PENDING).
    """
    class Meta:
        model = PerformanceReview
        fields = ["employee"]  # strictly what client can supply

    def validate_employee(self, value):
        if value.role != User.Roles.EMPLOYEE:
            raise serializers.ValidationError("employee must have role EMPLOYEE.")
        return value

    def create(self, validated_data):
        # server owns assigner; never trust client for this
        request = self.context["request"]
        validated_data["assigner"] = request.user
        # status stays default = PENDING
        return PerformanceReview.objects.create(**validated_data)


class FeedbackSerializer(serializers.Serializer):
    """
    Used by HR to submit/update feedback text.
    """
    feedback = serializers.CharField(allow_blank=False, trim_whitespace=True)

    def update(self, instance, validated_data):
        instance.feedback = validated_data["feedback"]
        instance.status = PerformanceReview.Status.FEEDBACK_PROVIDED
        instance.save(update_fields=["feedback", "status", "updated_at"])
        return instance
