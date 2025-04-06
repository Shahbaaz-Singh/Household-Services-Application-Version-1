# Household-Services-Application-Version-1
It is a multi-user app (requires one admin and other service professionals/ customers) which acts as platform for providing comprehensive home servicing and solutions.

## Frameworks Used

These are the mandatory frameworks on which the project is built:

- **Flask** for application code
- **Jinja2 templates + Bootstrap** for HTML generation and styling
- **SQLite** for data storage

## Project Statement

The project statement for this project can be found at:

[Project Statement](https://docs.google.com/document/d/1waf_CKBLk25fkwF-R4KS7wLq4KTIPhUcAtj6if5N-zo/pub)

## Project Report

A detailed project report, including a comprehensive overview, technical implementation, and future enhancements, can be found at:

[Project Report](https://github.com/Shahbaaz-Singh/Household-Services-Application-Version-1/blob/main/Project%20Report.pdf)

The report contains:
- **Project Overview**: Goals, scope, and purpose of the application
- **Technical Implementation**: Frameworks used, system architecture, and database design
- **API Endpoints Documentation**: How different users interact with the system
- **Demo Video Links**: Showcasing the features in action

## Running the Project

To run the project, navigate to the `household-services-application-version-1` directory and execute:

```sh
python run.py
```

## Database Setup

Initialize and migrate the database using Flask-Migrate:

```sh
set FLASK_APP=app:initialize_app
flask db init
flask db migrate -m "Initial migration."
flask db upgrade
```

## Creating an Admin User

To create a new admin user, use the following Python commands:

```python
from app import db
from app.models import Admin

new_admin = Admin(username="username")
new_admin.set_password("password")
db.session.add(new_admin)
db.session.commit()

Admin.query.all()
```

## API Endpoints

### Admin Endpoints

- **Create Admin**:
  ```sh
  curl -X POST http://localhost:5000/api/admins -H "Content-Type: application/json" -d "{\"username\": \"admin1\", \"password\": \"securepassword\"}"
  ```
- **Update Admin**:
  ```sh
  curl -X PUT http://localhost:5000/api/admins/1 -H "Content-Type: application/json" -d "{\"username\": \"updated_admin\", \"password\": \"newpassword\"}"
  ```
- **Delete Admin**:
  ```sh
  curl -X DELETE http://localhost:5000/api/admins/1
  ```
- **Get Admin Details**:
  ```sh
  curl -X GET http://localhost:5000/api/admins/1
  ```

### Customer Endpoints

- **Create Customer**:
  ```sh
  curl -X POST http://localhost:5000/api/customers -H "Content-Type: application/json" -d "{\"username\": \"customer1\", \"password\": \"securepassword\", \"location\": \"NY\", \"pin_code\": \"10001\", \"phone_number\": \"1234567890\", \"email\": \"customer1@example.com\", \"address\": \"123 Main St\"}"
  ```
- **Update Customer**:
  ```sh
  curl -X PUT http://localhost:5000/api/customers/1 -H "Content-Type: application/json" -d "{\"username\": \"updated_customer\", \"password\": \"newpassword\"}"
  ```
- **Delete Customer**:
  ```sh
  curl -X DELETE http://localhost:5000/api/customers/1
  ```
- **Get Customer Details**:
  ```sh
  curl -X GET http://localhost:5000/api/customers/1
  ```

### Professional Endpoints

- **Create Professional**:
  ```sh
  curl -X POST http://localhost:5000/api/professionals -H "Content-Type: application/json" -d "{\"username\": \"pro1\", \"password\": \"securepassword\", \"expertise\": \"plumbing\", \"location\": \"LA\", \"pin_code\": \"90001\", \"phone_number\": \"9876543210\", \"email\": \"pro1@example.com\", \"address\": \"456 Elm St\"}"
  ```
- **Update Professional**:
  ```sh
  curl -X PUT http://localhost:5000/api/professionals/1 -H "Content-Type: application/json" -d "{\"username\": \"updated_pro\", \"password\": \"newpassword\"}"
  ```
- **Delete Professional**:
  ```sh
  curl -X DELETE http://localhost:5000/api/professionals/1
  ```
- **Get Professional Details**:
  ```sh
  curl -X GET http://localhost:5000/api/professionals/1
  ```

### Service Endpoints

- **Create Service**:
  ```sh
  curl -X POST http://localhost:5000/api/services -H "Content-Type: application/json" -d "{\"name\": \"cleaning\", \"description\": \"Cleaning service\", \"price\": 100, \"time_required\":2, \"field_of_service\":\"Cleaning\"}"
  ```
- **Update Service**:
  ```sh
  curl -X PUT http://localhost:5000/api/services/3 -H "Content-Type: application/json" -d "{\"name\": \"cleaning\", \"description\": \"Cleaning service\", \"price\": 1000000, \"time_required\":2, \"field_of_service\":\"Cleaning\"}"
  ```
- **Delete Service**:
  ```sh
  curl -X DELETE http://localhost:5000/api/services/1
  ```
- **Get Service Details**:
  ```sh
  curl -X GET http://localhost:5000/api/services/1

### Service Request Endpoints

- **Create Service Request**:
  ```sh
  curl -X POST http://localhost:5000/api/requests -H "Content-Type: application/json" -d "{\"service_id\": 1, \"customer_id\": 1, \"remarks\": \"Urgent cleaning needed\", \"service_status\": \"pending\", \"field_of_service\":\"Cleaning\", \"location\": \"LA\", \"pin_code\": \"90001\"}"
  ```
- **Update Service Request**:
  ```sh
  curl -X PUT http://localhost:5000/api/requests/1 -H "Content-Type: application/json" -d "{\"service_id\": 1, \"customer_id\": 1, \"remarks\": \"Urgent cleaning needed\", \"service_status\": \"pending\", \"field_of_service\":\"Cleaning\", \"location\": \"LA\", \"pin_code\": \"90001\"}"
  ```
- **Delete Service Request**:
  ```sh
  curl -X DELETE http://localhost:5000/api/requests/1
  ```
- **Get Service Request Details**:
  ```sh
  curl -X GET http://localhost:5000/api/requests/1
  ```

### Authentication Endpoints

- **Login as Admin**:
  ```sh
  curl -X POST http://localhost:5000/api/login -H "Content-Type: application/json" -d "{\"username\": \"admin1\", \"password\": \"securepassword\", \"role\": \"admin\"}"
  ```
- **Login as Customer**:
  ```sh
  curl -X POST http://localhost:5000/api/login -H "Content-Type: application/json" -d "{\"username\": \"customer1\", \"password\": \"mypassword\", \"role\": \"customer\"}"
  ```
- **Login as Professional**:
  ```sh
  curl -X POST http://localhost:5000/api/login -H "Content-Type: application/json" -d "{\"username\": \"professional1\", \"password\": \"propassword\", \"role\": \"professional\"}"
  ```
