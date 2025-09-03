from django.contrib.auth.models import AbstractUser
from django.db import models

class UserAccount(AbstractUser):
    class Roles(models.TextChoices):
        ADMIN = "ADMIN", "Admin" #KEY = DB_VALUE , HUMAN_READABLE_VALUE
        MANAGER = "MANAGER", "Manager"
        HR = "HR", "HR" #HR-role: Assumed, assigns review times
        EMPLOYEE = "EMPLOYEE", "Employee"

    email = models.EmailField(unique=True)

    role = models.CharField(
        max_length=20,
        choices=Roles.choices,
        default=Roles.EMPLOYEE,
    )

    USERNAME_FIELD = "email"           # login with email
    REQUIRED_FIELDS = ["username"]     # still required for superuser creation

    def __str__(self):
        return f"{self.email} ({self.role})"

