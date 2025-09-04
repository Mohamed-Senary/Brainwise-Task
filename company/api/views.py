from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status
#from rest_framework.permissions import AllowAny #FOR TESTING PURPOSES
from accounts.api.permissions import (
    IsAdmin,
    IsEmployee,
    IsHR,
    IsManager
)
from company.models import (
    Company,
    Department,
    Employee,
    Project
)
from company.api.serializers import (
    CompanySerializer, 
    DepartmentSerializer, 
    EmployeeSerializer, 
    ProjectSerializer
)

#COMPANY ENDPOINTS
#LATER: Add Permissions
@api_view(['GET'])
@permission_classes([IsAdmin | IsManager | IsHR])
def list_companies (request):
    companies = Company.objects.all()
    serialized_companies = CompanySerializer (instance=companies , many=True)
    return Response(serialized_companies.data , status=status.HTTP_200_OK)

@api_view(['GET'])
@permission_classes([IsAdmin | IsManager | IsHR])
def company_details (request, id):
    try:
        company = Company.objects.get(pk=id)
    except Company.DoesNotExist as e:
        return Response ({"error":str(e)} , status=status.HTTP_404_NOT_FOUND)
    serialized_company = CompanySerializer (company)
    return Response(serialized_company.data , status=status.HTTP_200_OK)


#DEPARTMENT ENDPOINTS
#LATER: Add Permissions
@api_view(['GET'])
@permission_classes([IsAdmin | IsManager | IsHR])
def list_departments(request):
    # Get the company query parameter
    company_id = request.query_params.get('company') 
    if company_id:
        try:
            departments = Department.objects.filter(company_id=company_id)
        except ValueError:
            # Handle invalid company_id (non-integer)
            return Response({"error": "Invalid company ID"}, status=status.HTTP_400_BAD_REQUEST)
    else:
        departments = Department.objects.all()
    
    serializer = DepartmentSerializer(departments, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)

@api_view(['GET'])
@permission_classes([IsAdmin | IsManager | IsHR])
def department_details(request, id):
    try:
        department = Department.objects.get(pk=id)
    except Department.DoesNotExist as e:
        return Response({"error":str(e)}, status=status.HTTP_404_NOT_FOUND)
    
    serializer = DepartmentSerializer(department)
    return Response(serializer.data, status=status.HTTP_200_OK)

#EMPLOYEE ENDPOINTS
#LATER: Add Permissions 
@api_view(['GET', 'POST'])
@permission_classes([IsAdmin | IsManager | IsHR])
def list_employees (request):
    if request.method == 'GET':
        employees = Employee.objects.all()
        
        # Filter by company if provided
        company_id = request.query_params.get('company')
        if company_id:
            employees = employees.filter(company_id=company_id)
        
        # Filter by department if provided
        department_id = request.query_params.get('department')
        if department_id:
            employees = employees.filter(department_id=department_id)
        
        serializer = EmployeeSerializer(employees, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    elif request.method == 'POST':
        if not (request.user.is_hr or request.user.is_admin):
            return Response({"detail": "Only HR or Admin can create employees."}, status=status.HTTP_403_FORBIDDEN)
        employee = EmployeeSerializer (data=request.data)
        employee.is_valid(raise_exception=True)
        employee.save()
        return Response(employee.data, status=status.HTTP_201_CREATED)


@api_view(['GET', 'PUT', 'PATCH', 'DELETE'])
@permission_classes([IsAdmin | IsManager | IsHR])
def employee_by_id(request, id):
    try:
        employee = Employee.objects.get(pk=id)
    except Employee.DoesNotExist as e:
        return Response({"error": str(e)}, status=status.HTTP_404_NOT_FOUND)
    
    if request.method == 'GET':
        serializer = EmployeeSerializer(employee)
        return Response(serializer.data, status=status.HTTP_200_OK)
    elif request.method == 'DELETE':
        employee.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    elif request.method == 'PUT':
        serializer = EmployeeSerializer(employee, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)
    elif request.method == 'PATCH':
        serializer = EmployeeSerializer(employee, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)
