from app import db
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

class Admin(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), nullable=False, unique=True)
    password = db.Column(db.String(128), nullable=False)

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)
    
    @property
    def is_active(self):
        return True

    @property
    def is_authenticated(self):
        return True

    @property
    def is_anonymous(self):
        return False

    def get_id(self):
        return str(self.id)
    
class Customer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), nullable=False, unique=True)
    password = db.Column(db.String(128), nullable=False)
    is_blocked = db.Column(db.Boolean, default=False) 
    location = db.Column(db.String(100), nullable=False)
    pin_code = db.Column(db.String(10), nullable=False)
    phone_number = db.Column(db.String(15), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    address = db.Column(db.String(200), nullable=False)

    # Relationship to ServiceRequests
    service_requests = db.relationship('ServiceRequest', back_populates='requesting_customer')

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)

    @property
    def is_active(self):
        return True

    @property
    def is_authenticated(self):
        return True

    @property
    def is_anonymous(self):
        return False

    def get_id(self):
        return str(self.id)
    
class Professional(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), nullable=False, unique=True)
    password = db.Column(db.String(128), nullable=False)
    expertise = db.Column(db.String(100), nullable=False)
    rating = db.Column(db.Float, default=0)
    num_reviews = db.Column(db.Integer, default=0)
    location = db.Column(db.String(100), nullable=False)
    pin_code = db.Column(db.String(10), nullable=False)
    documents = db.Column(db.String(200))
    is_approved = db.Column(db.Boolean, default=False)
    phone_number = db.Column(db.String(15), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    address = db.Column(db.String(200), nullable=False)

    rejected_requests = db.Column(db.String, default='')
    accepted_requests = db.Column(db.String, default='')
    completed_requests = db.Column(db.String, default='')

    # Relationship to ServiceRequests
    service_requests = db.relationship('ServiceRequest', back_populates='assigned_professional')

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)

    @property
    def is_active(self):
        return True

    @property
    def is_authenticated(self):
        return True

    @property
    def is_anonymous(self):
        return False

    def get_id(self):
        return str(self.id)

class Service(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    price = db.Column(db.Float, nullable=False)
    time_required = db.Column(db.Float)
    description = db.Column(db.String(100), nullable=False)
    field_of_service = db.Column(db.String(100), nullable=False)

    # Relationship to ServiceRequests
    requests = db.relationship('ServiceRequest', back_populates='associated_service', lazy=True)

class ServiceRequest(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    
    # Foreign keys
    service_id = db.Column(db.Integer, db.ForeignKey('service.id'), nullable=False)
    customer_id = db.Column(db.Integer, db.ForeignKey('customer.id'), nullable=False)
    professional_id = db.Column(db.Integer, db.ForeignKey('professional.id'), nullable=True)
    
    # Dates and status
    date_of_request = db.Column(db.DateTime, default=datetime.utcnow)
    date_of_acceptance = db.Column(db.DateTime, nullable=True)
    date_of_completion = db.Column(db.DateTime, nullable=True)
    service_status = db.Column(db.String(20), default='pending')
    remarks = db.Column(db.String(100), nullable=True)
    location = db.Column(db.String(100), nullable=True)
    pin_code = db.Column(db.String(10), nullable=True)
    field_of_service = db.Column(db.String(100), nullable=True)

    # Relationships
    associated_service = db.relationship('Service', back_populates='requests')
    requesting_customer = db.relationship('Customer', back_populates='service_requests')
    assigned_professional = db.relationship('Professional', back_populates='service_requests')