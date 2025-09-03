from django.test import TestCase
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from django.urls import reverse
from .models import Company, Department, Employee, Project
from accounts.models import UserAccount

class CompanyAPITestCase(APITestCase):
    def setUp(self):
        """Set up test data - companies, departments, employees, projects"""
        self.client = APIClient()
        
        # Create test companies
        self.company1 = Company.objects.create(name="Tech Corp")
        self.company2 = Company.objects.create(name="Design Studio") 
        self.company3 = Company.objects.create(name="Marketing Agency")
        
        # Create departments for company1
        self.dept1_eng = Department.objects.create(
            company=self.company1,
            name="Engineering"
        )
        self.dept1_hr = Department.objects.create(
            company=self.company1,
            name="HR"
        )
        
        # Create departments for company2
        self.dept2_creative = Department.objects.create(
            company=self.company2,
            name="Creative"
        )
        self.dept2_dev = Department.objects.create(
            company=self.company2,
            name="Development"
        )
        
        # Create test employees
        self.employee1 = Employee.objects.create(
            company=self.company1,
            department=self.dept1_eng,
            name="John Doe",
            email="john@techcorp.com",
            designation="Software Engineer",
            hired_on="2023-01-15"
        )
        self.employee2 = Employee.objects.create(
            company=self.company1,
            department=self.dept1_hr,
            name="Jane Smith",
            email="jane@techcorp.com", 
            designation="HR Manager",
            hired_on="2022-06-10"
        )
        self.employee3 = Employee.objects.create(
            company=self.company2,
            department=self.dept2_creative,
            name="Bob Wilson",
            email="bob@design.com",
            designation="Designer"
        )
        
        # Create test projects
        self.project1 = Project.objects.create(
            company=self.company1,
            department=self.dept1_eng,
            name="Website Redesign",
            description="Redesign company website",
            start_date="2024-01-01",
            end_date="2024-06-01"
        )
        self.project2 = Project.objects.create(
            company=self.company2,
            department=self.dept2_creative,
            name="Brand Identity",
            description="Create new brand identity",
            start_date="2024-02-01"
        )
        
        # Add employees to projects
        self.project1.assigned_employees.add(self.employee1)
        self.project2.assigned_employees.add(self.employee3)

    # ============= COMPANY TESTS =============
    def test_list_companies_success(self):
        """Test GET /api/company/ returns all companies"""
        url = reverse('list-all-companies')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 3)
        
        # Check computed fields are included
        company_data = response.data[0]  # Assuming ordered by name
        self.assertIn('number_of_departments', company_data)
        self.assertIn('number_of_employees', company_data)
        self.assertIn('number_of_projects', company_data)

    def test_company_details_success(self):
        """Test GET /api/company/{id}/ returns specific company"""
        url = reverse('retrieve-single-company', args=[self.company1.id])
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], "Tech Corp")
        self.assertEqual(response.data['number_of_departments'], 2)
        self.assertEqual(response.data['number_of_employees'], 2)
        self.assertEqual(response.data['number_of_projects'], 1)

    def test_company_details_not_found(self):
        """Test GET /api/company/{id}/ with non-existent ID returns 404"""
        url = reverse('retrieve-single-company', args=[9999])
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertIn('error', response.data)

    # ============= DEPARTMENT TESTS =============
    def test_list_departments_success(self):
        """Test GET /api/company/departments/ returns all departments"""
        url = reverse('list-all-departments')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 4)  # 2 + 2 departments
        
        # Check computed fields and company name are included
        dept_data = response.data[0]
        self.assertIn('number_of_employees', dept_data)
        self.assertIn('number_of_projects', dept_data)
        self.assertIn('company_name', dept_data)

    def test_list_departments_filtered_by_company(self):
        """Test GET /api/company/departments/?company=1 filters by company"""
        url = reverse('list-all-departments')
        response = self.client.get(url, {'company': self.company1.id})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)  # Only company1 departments
        
        for dept in response.data:
            self.assertEqual(dept['company'], self.company1.id)
            self.assertEqual(dept['company_name'], "Tech Corp")

    def test_list_departments_filtered_by_nonexistent_company(self):
        """Test GET /api/company/departments/?company=9999 returns empty list"""
        url = reverse('list-all-departments')
        response = self.client.get(url, {'company': 9999})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 0)

    def test_list_departments_invalid_company_id(self):
        """Test GET /api/company/departments/?company=invalid returns 400"""
        url = reverse('list-all-departments')
        response = self.client.get(url, {'company': 'invalid'})
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_department_details_success(self):
        """Test GET /api/company/department/{id}/ returns specific department"""
        url = reverse('retrieve-single-department', args=[self.dept1_eng.id])
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], "Engineering")
        self.assertEqual(response.data['company_name'], "Tech Corp")
        self.assertEqual(response.data['number_of_employees'], 1)

    def test_department_details_not_found(self):
        """Test GET /api/company/department/{id}/ with non-existent ID returns 404"""
        url = reverse('retrieve-single-department', args=[9999])
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    # ============= EMPLOYEE TESTS =============
    def test_list_employees_success(self):
        """Test GET /api/company/employee/ returns all employees"""
        url = reverse('list-all/add-employee')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 3)
        
        # Check computed fields and nested names are included
        emp_data = response.data[0]
        self.assertIn('days_employed', emp_data)
        self.assertIn('company_name', emp_data)
        self.assertIn('department_name', emp_data)

    def test_list_employees_filtered_by_company(self):
        """Test GET /api/company/employee/?company=1 filters by company"""
        url = reverse('list-all/add-employee')
        response = self.client.get(url, {'company': self.company1.id})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)  # Only company1 employees

    def test_list_employees_filtered_by_department(self):
        """Test GET /api/company/employee/?department=1 filters by department"""
        url = reverse('list-all/add-employee')
        response = self.client.get(url, {'department': self.dept1_eng.id})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['name'], "John Doe")

    def test_list_employees_filtered_by_company_and_department(self):
        """Test GET /api/company/employee/?company=1&department=1 filters by both"""
        url = reverse('list-all/add-employee')
        response = self.client.get(url, {
            'company': self.company1.id,
            'department': self.dept1_eng.id
        })
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_create_employee_success(self):
        """Test POST /api/company/employee/ creates new employee"""
        url = reverse('list-all/add-employee')
        data = {
            'company': self.company1.id,
            'department': self.dept1_eng.id,
            'name': 'New Employee',
            'email': 'new@techcorp.com',
            'designation': 'Junior Developer'
        }
        response = self.client.post(url, data)
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['name'], 'New Employee')
        self.assertEqual(response.data['company_name'], 'Tech Corp')
        self.assertEqual(response.data['department_name'], 'Engineering')

    def test_create_employee_invalid_data(self):
        """Test POST /api/company/employee/ with invalid data returns 400"""
        url = reverse('list-all/add-employee')
        data = {
            'name': 'Invalid Employee'
            # Missing required fields
        }
        response = self.client.post(url, data)
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_employee_duplicate_email(self):
        """Test POST /api/company/employee/ with duplicate email returns 400"""
        url = reverse('list-all/add-employee')
        data = {
            'company': self.company1.id,
            'name': 'Duplicate Email',
            'email': 'john@techcorp.com'  # Already exists
        }
        response = self.client.post(url, data)
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_employee_details_success(self):
        """Test GET /api/company/employee/{id}/ returns specific employee"""
        url = reverse('retrieve/edit/delete-single-employee', args=[self.employee1.id])
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'John Doe')
        self.assertEqual(response.data['company_name'], 'Tech Corp')
        self.assertIsNotNone(response.data['days_employed'])

    def test_employee_details_not_found(self):
        """Test GET /api/company/employee/{id}/ with non-existent ID returns 404"""
        url = reverse('retrieve/edit/delete-single-employee', args=[9999])
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_update_employee_success(self):
        """Test PUT /api/company/employee/{id}/ updates employee"""
        url = reverse('retrieve/edit/delete-single-employee', args=[self.employee1.id])
        data = {
            'company': self.employee1.company.id,
            'department': self.employee1.department.id,
            'name': 'John Updated',
            'email': self.employee1.email,
            'designation': 'Senior Developer'
        }
        response = self.client.put(url, data)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'John Updated')
        self.assertEqual(response.data['designation'], 'Senior Developer')

    def test_partial_update_employee_success(self):
        """Test PATCH /api/company/employee/{id}/ partially updates employee"""
        url = reverse('retrieve/edit/delete-single-employee', args=[self.employee1.id])
        data = {'designation': 'Lead Developer'}
        response = self.client.patch(url, data)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['designation'], 'Lead Developer')
        self.assertEqual(response.data['name'], 'John Doe')  # Unchanged

    def test_delete_employee_success(self):
        """Test DELETE /api/company/employee/{id}/ deletes employee"""
        url = reverse('retrieve/edit/delete-single-employee', args=[self.employee3.id])
        response = self.client.delete(url)
        
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        
        # Verify employee was deleted
        self.assertFalse(Employee.objects.filter(id=self.employee3.id).exists())
