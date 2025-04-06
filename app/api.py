from flask_restful import Resource, reqparse, Api
from app.models import Admin, Customer, Professional, ServiceRequest,Service , db

# Initialize the API object
api = Api()

#-------------------------------------------------------------------------------------------------------------------#
# Resource for handling authentication
class AuthResource(Resource):
    def post(self):
        # Parse the required fields for login
        parser = reqparse.RequestParser()
        parser.add_argument('username', type=str, required=True, help='Username cannot be blank')
        parser.add_argument('password', type=str, required=True, help='Password cannot be blank')
        parser.add_argument('role', type=str, required=True, choices=('admin', 'customer', 'professional'), 
                            help="Role must be 'admin', 'customer', or 'professional'")
        args = parser.parse_args()

        # Extract fields
        username = args['username']
        password = args['password']
        role = args['role']
        
        # Check user credentials based on role
        user = None
        if role == 'admin':
            user = Admin.query.filter_by(username=username).first()
        elif role == 'customer':
            user = Customer.query.filter_by(username=username).first()
        elif role == 'professional':
            user = Professional.query.filter_by(username=username).first()

        # Authenticate and respond
        if user and user.check_password(password):
            return {
                'message': 'Login successful',
                'role': role,
                'user_id': user.id
            }, 200
        return {'message': 'Invalid credentials'}, 401
#-----------------------------------------------------------------------------------------------------------------#
    
#-----------------------------------------------------------------------------------------------------------------#
"""
All resource classes (AdminResource, CustomerResource, ProfessionalResource, 
ServiceResource, and ServiceRequestResource) follow a similar structure for 
handling HTTP methods (GET, POST, PUT, DELETE):

- 'GET': Retrieves data by ID.
- 'POST': Creates new entries, using `reqparse.RequestParser` to validate and 
  parse input data.
- 'PUT': Updates existing entries by ID, with `reqparse` ensuring proper data 
  validation.
- 'DELETE': Removes entries by ID.

`reqparse` is used in 'POST' and 'PUT' methods to validate required fields and 
ensure correct data formats before database operations.
"""    
# Admin Resource for CRUD operations on admin
class AdminResource(Resource):
    def get(self, admin_id):
        admin = Admin.query.get(admin_id)
        if admin:
            return {'id': admin.id, 'username': admin.username}, 200
        return {'message': 'Admin not found'}, 404

    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('username', type=str, required=True, help='Username cannot be blank')
        parser.add_argument('password', type=str, required=True, help='Password cannot be blank')
        args = parser.parse_args()

        new_admin = Admin(username=args['username'])
        new_admin.set_password(args['password'])
        db.session.add(new_admin)
        db.session.commit()
        return {'message': 'Admin created successfully'}, 201

    def put(self, admin_id):
        admin = Admin.query.get(admin_id)
        if admin:
            parser = reqparse.RequestParser()
            parser.add_argument('username', type=str, required=True, help='Username cannot be blank')
            parser.add_argument('password', type=str, required=True, help='Password cannot be blank')
            args = parser.parse_args()

            admin.username = args['username']
            admin.set_password(args['password'])
            db.session.commit()
            return {'message': 'Admin updated successfully'}, 200
        return {'message': 'Admin not found'}, 404

    def delete(self, admin_id):
        admin = Admin.query.get(admin_id)
        if admin:
            db.session.delete(admin)
            db.session.commit()
            return {'message': 'Admin deleted successfully'}, 200
        return {'message': 'Admin not found'}, 404

# Customer Resource for CRUD operations on customers
class CustomerResource(Resource):
    def get(self, customer_id):
        customer = Customer.query.get(customer_id)
        if customer:
            return {
                'id': customer.id,
                'username': customer.username,
                'location': customer.location,
                'pin_code': customer.pin_code,
                'phone_number': customer.phone_number,
                'email': customer.email,
                'address': customer.address
            }, 200
        return {'message': 'Customer not found'}, 404

    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('username', type=str, required=True, help='Username cannot be blank')
        parser.add_argument('password', type=str, required=True, help='Password cannot be blank')
        parser.add_argument('location', type=str, required=True, help='Location cannot be blank')
        parser.add_argument('pin_code', type=str, required=True, help='Pin code cannot be blank')
        parser.add_argument('phone_number', type=str, required=True, help='Phone number cannot be blank')
        parser.add_argument('email', type=str, required=True, help='Email cannot be blank')
        parser.add_argument('address', type=str, required=True, help='Address cannot be blank')
        
        args = parser.parse_args()
        
        new_customer = Customer(
            username=args['username'],
            location=args['location'],
            pin_code=args['pin_code'],
            phone_number=args['phone_number'],
            email=args['email'],
            address=args['address']
        )
        new_customer.set_password(args['password'])
        db.session.add(new_customer)
        db.session.commit()
        return {'message': 'Customer created successfully'}, 201

    def put(self, customer_id):
        customer = Customer.query.get(customer_id)
        if customer:
            parser = reqparse.RequestParser()
            parser.add_argument('username', type=str, required=False)
            parser.add_argument('password', type=str, required=False)
            parser.add_argument('location', type=str, required=False)
            parser.add_argument('pin_code', type=str, required=False)
            parser.add_argument('phone_number', type=str, required=False)
            parser.add_argument('email', type=str, required=False)
            parser.add_argument('address', type=str, required=False)
            
            args = parser.parse_args()

            if args['username']:
                customer.username = args['username']
            if args['password']:
                customer.set_password(args['password'])
            if args['location']:
                customer.location = args['location']
            if args['pin_code']:
                customer.pin_code = args['pin_code']
            if args['phone_number']:
                customer.phone_number = args['phone_number']
            if args['email']:
                customer.email = args['email']
            if args['address']:
                customer.address = args['address']

            db.session.commit()
            return {'message': 'Customer updated successfully'}, 200

        return {'message': 'Customer not found'}, 404

    def delete(self, customer_id):
        customer = Customer.query.get(customer_id)
        if customer:
            db.session.delete(customer)
            db.session.commit()
            return {'message': 'Customer deleted successfully'}, 200
        return {'message': 'Customer not found'}, 404

# Professional Resource for CRUD operations on professionals
class ProfessionalResource(Resource):
    def get(self, professional_id):
        professional = Professional.query.get(professional_id)
        if professional:
            return {
                'id': professional.id,
                'username': professional.username,
                'expertise': professional.expertise,
                'location': professional.location,
                'pin_code': professional.pin_code,
                'phone_number': professional.phone_number,
                'email': professional.email,
                'address': professional.address
            }, 200
        return {'message': 'Professional not found'}, 404

    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('username', type=str, required=True, help='Username cannot be blank')
        parser.add_argument('password', type=str, required=True, help='Password cannot be blank')
        parser.add_argument('expertise', type=str, required=True, help='Expertise cannot be blank')
        parser.add_argument('location', type=str, required=True, help='Location cannot be blank')
        parser.add_argument('pin_code', type=str, required=True, help='Pin code cannot be blank')
        parser.add_argument('phone_number', type=str, required=True, help='Phone number cannot be blank')
        parser.add_argument('email', type=str, required=True, help='Email cannot be blank')
        parser.add_argument('address', type=str, required=True, help='Address cannot be blank')
        
        args = parser.parse_args()
        
        new_professional = Professional(
            username=args['username'],
            expertise=args['expertise'],
            location=args['location'],
            pin_code=args['pin_code'],
            phone_number=args['phone_number'],
            email=args['email'],
            address=args['address']
        )
        new_professional.set_password(args['password'])
        db.session.add(new_professional)
        db.session.commit()
        return {'message': 'Professional created successfully'}, 201

    def put(self, professional_id):
        professional = Professional.query.get(professional_id)
        if professional:
            parser = reqparse.RequestParser()
            parser.add_argument('username', type=str, required=False)
            parser.add_argument('password', type=str, required=False)
            parser.add_argument('expertise', type=str, required=False)
            parser.add_argument('location', type=str, required=False)
            parser.add_argument('pin_code', type=str, required=False)
            parser.add_argument('phone_number', type=str, required=False)
            parser.add_argument('email', type=str, required=False)
            parser.add_argument('address', type=str, required=False)
            
            args = parser.parse_args()

            if args['username']:
                professional.username = args['username']
            if args['password']:
                professional.set_password(args['password'])
            if args['expertise']:
                professional.expertise = args['expertise']
            if args['location']:
                professional.location = args['location']
            if args['pin_code']:
                professional.pin_code = args['pin_code']
            if args['phone_number']:
                professional.phone_number = args['phone_number']
            if args['email']:
                professional.email = args['email']
            if args['address']:
                professional.address = args['address']

            db.session.commit()
            return {'message': 'Professional updated successfully'}, 200

        return {'message': 'Professional not found'}, 404

    def delete(self, professional_id):
        professional = Professional.query.get(professional_id)
        if professional:
            db.session.delete(professional)
            db.session.commit()
            return {'message': 'Professional deleted successfully'}, 200
        return {'message': 'Professional not found'}, 404

# Service Resource for CRUD operations on services
class ServiceResource(Resource):
    def get(self, service_id):
        service = Service.query.get(service_id)
        if service:
            return {
                'id': service.id,
                'name': service.name,
                'price': service.price,
                'time_required': service.time_required,
                'description': service.description,
                'field_of_service': service.field_of_service
            }, 200
        return {'message': 'Service not found'}, 404

    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('name', type=str, required=True, help='Name of the service cannot be blank')
        parser.add_argument('price', type=float, required=True, help='Price of the service cannot be blank')
        parser.add_argument('time_required', type=int, required=True, help='Time required for the service cannot be blank')
        parser.add_argument('description', type=str, required=False, help='Description of the service')
        parser.add_argument('field_of_service', type=str, required=True, help='Field of service cannot be blank')

        args = parser.parse_args()

        new_service = Service(
            name=args['name'],
            price=args['price'],
            time_required=args['time_required'],
            description=args.get('description'),
            field_of_service=args['field_of_service']
        )
        db.session.add(new_service)
        db.session.commit()

        return {'message': 'Service created successfully'}, 201

    def put(self, service_id):
        service = Service.query.get(service_id)
        if service:
            parser = reqparse.RequestParser()
            parser.add_argument('name', type=str, required=False, help='Name of the service')
            parser.add_argument('price', type=float, required=False, help='Price of the service')
            parser.add_argument('time_required', type=int, required=False, help='Time required for the service')
            parser.add_argument('description', type=str, required=False, help='Description of the service')
            parser.add_argument('field_of_service', type=str, required=False, help='Field of service')

            args = parser.parse_args()

            if args['name']:
                service.name = args['name']
            if args['price']:
                service.price = args['price']
            if args['time_required']:
                service.time_required = args['time_required']
            if args['description']:
                service.description = args['description']
            if args['field_of_service']:
                service.field_of_service = args['field_of_service']

            db.session.commit()

            return {'message': 'Service updated successfully'}, 200

        return {'message': 'Service not found'}, 404

    def delete(self, service_id):
        service = Service.query.get(service_id)
        if service:
            db.session.delete(service)
            db.session.commit()
            return {'message': 'Service deleted successfully'}, 200
        return {'message': 'Service not found'}, 404

# ServiceRequest Resource for CRUD operations on service requests
class ServiceRequestResource(Resource):
    def get(self, request_id):
        request = ServiceRequest.query.get(request_id)
    
        if request:
            response_data = {
                'id': request.id,
                'service_id': request.service_id,
                'customer_id': request.customer_id,
                'professional_id': request.professional_id,
                # Convert datetime fields to ISO format strings if they are not None as JSON can't read them direct
                'date_of_request': request.date_of_request.isoformat() if request.date_of_request else None,
                'date_of_acceptance': request.date_of_acceptance.isoformat() if request.date_of_acceptance else None,
                'date_of_completion': request.date_of_completion.isoformat() if request.date_of_completion else None,
                'service_status': request.service_status,
                'remarks': request.remarks,
                'field_of_service': request.field_of_service,
                'location': request.location,
                'pin_code': request.pin_code
            }
            return response_data, 200

        return {'message': 'Service request not found'}, 404


    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('service_id', type=int, required=True, help='Service ID cannot be blank')
        parser.add_argument('customer_id', type=int, required=True, help='Customer ID cannot be blank')
        parser.add_argument('service_status', type=str, required=False)
        parser.add_argument('remarks', type=str, required=False)
        parser.add_argument('field_of_service', type=str, required=False)
        parser.add_argument('location', type=str, required=False)
        parser.add_argument('pin_code', type=str, required=False)
        
        args = parser.parse_args()

        new_request = ServiceRequest(
            service_id=args['service_id'],
            customer_id=args['customer_id'],
            service_status=args.get('service_status'),
            remarks=args.get('remarks'),
            field_of_service=args.get('field_of_service'),
            location=args.get('location'),
            pin_code=args.get('pin_code')
        )
        db.session.add(new_request)
        db.session.commit()
        return {'message': 'Service request created successfully'}, 201

    def put(self, request_id):
        request = ServiceRequest.query.get(request_id)
        if request:
            parser = reqparse.RequestParser()
            parser.add_argument('service_status', type=str, required=False, help='Service status cannot be blank')
            parser.add_argument('remarks', type=str, required=False, help='Remarks about the service')
            parser.add_argument('field_of_service', type=str, required=False, help='Field of service')
            parser.add_argument('location', type=str, required=False, help='Location of the service request')
            parser.add_argument('pin_code', type=str, required=False, help='Pin code of the location')

            args = parser.parse_args()

            if args['service_status']:
                request.service_status = args['service_status']
            if args['remarks']:
                request.remarks = args['remarks']
            if args['field_of_service']:
                request.field_of_service = args['field_of_service']
            if args['location']:
                request.location = args['location']
            if args['pin_code']:
                request.pin_code = args['pin_code']

            db.session.commit()
            return {'message': 'Service request updated successfully'}, 200

        return {'message': 'Service request not found'}, 404

    def delete(self, request_id):
        request = ServiceRequest.query.get(request_id)
        if request:
            db.session.delete(request)
            db.session.commit()
            return {'message': 'Service request deleted successfully'}, 200
        return {'message': 'Service request not found'}, 404
#--------------------------------------------------------------------------------------------------------------------------------------#

#--------------------------------------------------------------------------------------------------------------------------------------#
# Adding resources to the API and defining/setting their endpoints

api.add_resource(AuthResource, '/api/login', endpoint='login')  # Authentication

api.add_resource(AdminResource, '/api/admins', endpoint='admins')  # For POST
api.add_resource(AdminResource, '/api/admins/<int:admin_id>', endpoint='admin')  # For GET, PUT, DELETE

api.add_resource(CustomerResource, '/api/customers', endpoint='customers')  # For POST
api.add_resource(CustomerResource, '/api/customers/<int:customer_id>', endpoint='customer')  # For GET, PUT, DELETE

api.add_resource(ProfessionalResource, '/api/professionals', endpoint='professionals')  # For POST
api.add_resource(ProfessionalResource, '/api/professionals/<int:professional_id>', endpoint='professional')  # For GET, PUT, DELETE

api.add_resource(ServiceResource, '/api/services', endpoint='services')  # For POST (create)
api.add_resource(ServiceResource, '/api/services/<int:service_id>', endpoint='service')  # For GET, PUT, DELETE

api.add_resource(ServiceRequestResource, '/api/requests', endpoint='service_requests')  # For POST
api.add_resource(ServiceRequestResource, '/api/requests/<int:request_id>', endpoint='service_request')  # For GET, PUT, DELETE
#--------------------------------------------------------------------------------------------------------------------------------------#