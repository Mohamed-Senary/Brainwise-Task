from django.db import models
from django.conf import settings

class PerformanceReview(models.Model):
    class Status(models.TextChoices):
        PENDING = "PENDING", "Pending"
        SCHEDULED = "SCHEDULED", "Scheduled"
        FEEDBACK_PROVIDED = "FEEDBACK_PROVIDED", "Feedback Provided"
        UNDER_APPROVAL = "UNDER_APPROVAL", "Under Approval"
        APPROVED = "APPROVED", "Approved"
        REJECTED = "REJECTED", "Rejected"

    employee = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="reviews",
    )

    assigner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="assigned_reviews",
    )

    approved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="approved_reviews",
    )

    scheduled_at = models.DateTimeField(null=True, blank=True)
    feedback = models.TextField(null=True, blank=True)

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Review for {self.employee.email} - {self.status}"
