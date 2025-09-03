from django.urls import path
from .views import (
    list_companies,
    company_details,
    list_departments,
    department_details,
    list_employees,
    employee_by_id
)

urlpatterns = [
    path('' , list_companies , name='list-all-companies'),
    path('<int:id>/', company_details, name='retrieve-single-company'),
    path('departments/', list_departments, name='list-all-departments'), #could filter by company
    path('department/<int:id>/', department_details, name='retrieve-single-department'),
    path('employee/' , list_employees, name='list-all/add-employee'), #could filter by comp.,dept. or both
    path('employee/<int:id>/', employee_by_id, name='retrieve/edit/delete-single-employee')
]