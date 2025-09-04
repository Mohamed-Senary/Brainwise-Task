from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
from reviews.models import PerformanceReview

User = get_user_model()


class ReviewPermissionTests(TestCase):
    def setUp(self):
        self.client = APIClient()

        # Create users with enum roles
        self.admin = User.objects.create_user(
            username="admin", email="admin@test.com", password="pass", role=User.Roles.ADMIN
        )
        self.hr = User.objects.create_user(
            username="hr", email="hr@test.com", password="pass", role=User.Roles.HR
        )
        self.manager = User.objects.create_user(
            username="manager", email="manager@test.com", password="pass", role=User.Roles.MANAGER
        )
        self.employee = User.objects.create_user(
            username="employee", email="employee@test.com", password="pass", role=User.Roles.EMPLOYEE
        )

        # A base review assigned to employee
        self.review = PerformanceReview.objects.create(
            employee=self.employee,
            status=PerformanceReview.Status.PENDING
        )

    def test_list_reviews_only_admin_hr_manager(self):
        url = reverse("review-list")

        # employee forbidden
        self.client.force_authenticate(self.employee)
        res = self.client.get(url)
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

        # hr allowed
        self.client.force_authenticate(self.hr)
        res = self.client.get(url)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

        # manager allowed
        self.client.force_authenticate(self.manager)
        res = self.client.get(url)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

        # admin allowed
        self.client.force_authenticate(self.admin)
        res = self.client.get(url)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_employee_can_list_own_reviews(self):
        self.client.force_authenticate(user=self.employee)
        response = self.client.get(reverse("emp-reviews"))  # if Option 2
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)  # the review we created
        self.assertEqual(response.data[0]["employee"], self.employee.id)

    def test_assign_review_hr_only(self):
        url = reverse("review-assign")
        data = {"employee": self.employee.id}

        # hr allowed
        self.client.force_authenticate(self.hr)
        res = self.client.post(url, data)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

        # admin forbidden
        self.client.force_authenticate(self.admin)
        res = self.client.post(url, data)
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

        # manager forbidden
        self.client.force_authenticate(self.manager)
        res = self.client.post(url, data)
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_confirm_review_employee_only(self):
        url = reverse("review-confirm" , args=[self.review.id])

        # employee allowed
        self.client.force_authenticate(self.employee)
        res = self.client.patch(url, {} , format="json")
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.review.refresh_from_db()
        self.assertEqual(self.review.status, PerformanceReview.Status.SCHEDULED)

        # hr forbidden
        self.client.force_authenticate(self.hr)
        res = self.client.patch(url, {}, format="json")
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_feedback_hr_only(self):
        self.review.status = PerformanceReview.Status.SCHEDULED
        self.review.save()
        url = reverse("review-feedback", args=[self.review.id])
        data = {"feedback": "Great job"}

        # hr allowed
        self.client.force_authenticate(self.hr)
        res = self.client.patch(url, data)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.review.refresh_from_db()
        self.assertEqual(self.review.feedback, "Great job")

        # employee forbidden
        self.client.force_authenticate(self.employee)
        res = self.client.patch(url, data)
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_push_for_approval_hr_only(self):
        self.review.status = PerformanceReview.Status.FEEDBACK_PROVIDED
        self.review.save()
        url = reverse("review-push", args=[self.review.id])

        # hr allowed
        self.client.force_authenticate(self.hr)
        res = self.client.patch(url)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.review.refresh_from_db()
        self.assertEqual(self.review.status, PerformanceReview.Status.UNDER_APPROVAL)

        # manager forbidden
        self.client.force_authenticate(self.manager)
        res = self.client.patch(url)
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_approve_review_manager_only(self):
        self.review.status = PerformanceReview.Status.UNDER_APPROVAL
        self.review.save()
        url = reverse("review-approve", args=[self.review.id])

        # manager allowed
        self.client.force_authenticate(self.manager)
        res = self.client.patch(url)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.review.refresh_from_db()
        self.assertEqual(self.review.status, PerformanceReview.Status.APPROVED)
        self.assertEqual(self.review.approved_by, self.manager)

        # hr forbidden
        self.client.force_authenticate(self.hr)
        res = self.client.patch(url)
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_reject_review_manager_only(self):
        self.review.status = PerformanceReview.Status.UNDER_APPROVAL
        self.review.save()
        url = reverse("review-reject", args=[self.review.id])

        # manager allowed
        self.client.force_authenticate(self.manager)
        res = self.client.patch(url)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.review.refresh_from_db()
        self.assertEqual(self.review.status, PerformanceReview.Status.REJECTED)

        # employee forbidden
        self.client.force_authenticate(self.employee)
        res = self.client.patch(url)
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)
