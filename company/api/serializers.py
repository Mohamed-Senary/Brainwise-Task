from rest_framework import serializers
from ..models import Company, Department, Employee, Project

class CompanySerializer(serializers.ModelSerializer):
    # Include computed fields as read-only
    number_of_departments = serializers.ReadOnlyField()
    number_of_employees = serializers.ReadOnlyField()
    number_of_projects = serializers.ReadOnlyField()

    class Meta:
        model = Company
        fields = [
            'id',
            'name',
            'number_of_departments',
            'number_of_employees',
            'number_of_projects'
        ]


class DepartmentSerializer(serializers.ModelSerializer):
    # Include computed fields as read-only
    number_of_employees = serializers.ReadOnlyField()
    number_of_projects = serializers.ReadOnlyField()

    class Meta:
        model = Department
        fields = [
            'id',
            'company',
            'name',
            'number_of_employees',
            'number_of_projects'
        ]
        
    def to_representation(self, instance):
        """
        Override to include company name in response
        """
        data = super().to_representation(instance)
        
        # Add company name
        if instance.company:
            data['company_name'] = instance.company.name
            
        return data

class EmployeeSerializer(serializers.ModelSerializer):
    # Include computed field as read-only
    days_employed = serializers.ReadOnlyField()
    
    class Meta:
        model = Employee
        fields = [
            'id',
            'company',
            'department',
            'name',
            'email',
            'mobile_number',
            'address',
            'designation',
            'hired_on',
            'days_employed'
        ]
    
    def to_representation(self, instance):
        """
        Override to include company and department names in response
        """
        data = super().to_representation(instance)
        
        # Add company name
        if instance.company:
            data['company_name'] = instance.company.name
        
        # Add department name
        if instance.department:
            data['department_name'] = instance.department.name
        else:
            data['department_name'] = None
            
        return data


class ProjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        fields = [
            'id',
            'company',
            'department',
            'name',
            'description',
            'start_date',
            'end_date',
            'assigned_employees'
        ]
    
    def to_representation(self, instance):
        """
        Override to include company name, department name, and assigned employees list
        """
        data = super().to_representation(instance)
        
        # Add company name
        if instance.company:
            data['company_name'] = instance.company.name
        
        # Add department name
        if instance.department:
            data['department_name'] = instance.department.name
        else:
            data['department_name'] = None
        
        # Add assigned employees list with names
        assigned_employees = []
        for employee in instance.assigned_employees.all():
            assigned_employees.append({
                'id': employee.id,
                'name': employee.name,
                'email': employee.email
            })
        data['assigned_employees_list'] = assigned_employees
        
        return data