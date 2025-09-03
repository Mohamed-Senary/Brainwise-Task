from django.db import models
from django.utils import timezone
#from django.core.exceptions import ValidationError

class Company(models.Model):
    name = models.CharField(max_length=255, help_text="Company name")

    class Meta:
        verbose_name = "Company"
        verbose_name_plural = "Companies"
        ordering = ['name']

    def __str__(self):
        return self.name

    @property
    def number_of_departments(self):
        """
        Returns the total number of departments in this company.
        """
        return self.departments.count()

    @property
    def number_of_employees(self):
        """
        Returns the total number of employees in this company.
        """
        return self.employees.count()

    @property
    def number_of_projects(self):
        """
        Returns the total number of projects in this company.
        """
        return self.projects.count()
    
class Department(models.Model):
    company = models.ForeignKey(
        Company, 
        on_delete=models.CASCADE, 
        related_name='departments'
    )
    name = models.CharField(
        max_length=255
    )

    class Meta:
        verbose_name = "Department"
        verbose_name_plural = "Departments"
        # Ensure department names are unique within each company
        #ie: a single company can't have the same dept more than once
        unique_together = [['company', 'name']]

    def __str__(self):
        return f"{self.company.name} - {self.name}"

    @property
    def number_of_employees(self):
        """
        Returns the total number of employees in this department.
        """
        return self.employees.count()

    @property
    def number_of_projects(self):
        """
        Returns the total number of projects assigned to this department.
        """
        return self.projects.count()
    
class Employee(models.Model):
    company = models.ForeignKey(
        Company,
        on_delete=models.PROTECT,  # Prevent accidental company deletion
        related_name='employees'
    )
    department = models.ForeignKey(
        Department,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='employees',
    )
    name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    mobile_number = models.CharField(
        max_length=20, 
        blank=True
    )
    address = models.CharField(max_length=500, blank=True)
    designation = models.CharField(
        max_length=100, 
        blank=True
    )
    hired_on = models.DateField(
        null=True, 
        blank=True
    )
    
    class Meta:
        verbose_name = "Employee"
        verbose_name_plural = "Employees"
        ordering = ['name']

    def __str__(self):
        return f"{self.name} ({self.company.name})"

    @property
    def days_employed(self):
        """
        Returns the number of days the employee has been employed.
        Returns None if the employee hasn't been hired yet.
        """
        if not self.hired_on:
            return None
        return (timezone.now().date() - self.hired_on).days

    # def clean(self):
    #     """
    #     Custom validation for Employee model.
    #     """
    #     super().clean()
        
    #     # Ensure employee's department belongs to the same company
    #     if self.department and self.company and self.department.company != self.company:
    #         raise ValidationError({
    #             'department': 'Employee department must belong to the same company.'
    #         })

class Project(models.Model):
    company = models.ForeignKey(
        Company,
        on_delete=models.CASCADE,
        related_name='projects'
    )
    department = models.ForeignKey(
        Department,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='projects'
    )
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    start_date = models.DateField()
    end_date = models.DateField(
        null=True, 
        blank=True, 
    )
    # Many-to-Many relationship with employees
    assigned_employees = models.ManyToManyField(
        Employee,
        blank=True,
        related_name='assigned_projects'
    )

    class Meta:
        verbose_name = "Project"
        verbose_name_plural = "Projects"
        ordering = ['company__name', 'name']

    def __str__(self):
        return f"{self.company.name} - {self.name}"

    # def clean(self):
    #     """
    #     Custom validation for Project model.
    #     """
    #     super().clean()
        
    #     # Validate date range
    #     if self.end_date and self.start_date and self.end_date < self.start_date:
    #         raise ValidationError({
    #             'end_date': 'End date cannot be before start date.'
    #         })
        
    #     # Ensure project's department belongs to the same company
    #     if self.department and self.company and self.department.company != self.company:
    #         raise ValidationError({
    #             'department': 'Project department must belong to the same company.'
    #         })

    # def save(self, *args, **kwargs):
    #     """
    #     Override save to include validation.
    #     """
    #     self.full_clean()
    #     super().save(*args, **kwargs)