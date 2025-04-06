""" Importing necessary modules and packages for routing, database interaction, user authentication,
form handling, file management, data visualization, and utilities."""
from flask import Blueprint, render_template, redirect, url_for, request, flash, current_app, make_response, session
from app import db
from app.models import Admin, Service, ServiceRequest, Customer, Professional
from flask_login import login_user, logout_user, login_required, current_user
from datetime import datetime, timedelta # timedelta is imported for converting utc time to indian standard time
from app.forms import RegistrationForm
import os # imported to interact with the operating system for the directory operations like provided direction for document in registeration
from werkzeug.utils import secure_filename # for making the filename of the document safe by removing or updating character if neccessary
from sqlalchemy import or_, and_ # these or_, and_ were imported for constructing (filtering) queries on some conditons
import matplotlib
matplotlib.use('Agg') # this was done because earlier tkinter was creating problem, now this don't require GUI like tkinter
import matplotlib.pyplot as plt
from io import BytesIO
import base64

from functools import wraps

# Creating a blueprint for the routes and other things named "main" so that later we can regsiter it in "__init__.py"
main = Blueprint('main', __name__)

""" This "nocache" was done so that the cache of protected pages which needed login is note stored
    because after logging out if earlier i clicked on back button of the browser it still
    took was to the previous page whether it was a protect page or not."""
def nocache(view):
    @wraps(view)
    def no_cache_view(*args, **kwargs):
        response = make_response(view(*args, **kwargs))
        response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, post-check=0, pre-check=0, max-age=0'
        response.headers['Pragma'] = 'no-cache'
        response.headers['Expires'] = '0'
        return response
    return no_cache_view

#-----------------------------
# Route for index (home) page
#-----------------------------
@main.route('/')
@nocache
def index():
    return render_template('index.html')
#-----------------------------------------------------------------------#

#-------------------------------------------------------
# Routes for registering of professionals and customers
#-------------------------------------------------------
@main.route('/register', methods=['GET', 'POST'])
@nocache
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        role = form.role.data
        location = form.location.data
        pin_code = form.pin_code.data
        phone_number = form.phone_number.data
        email = form.email.data
        address = form.address.data


        # Handle file upload if role is 'professional' so that admin can see the file for verification and approving purposes
        document_filename = None
        if role == 'professional':
            if 'documents' not in request.files or not request.files['documents'].filename:
                flash('Please upload the required documents.', 'danger')
                return redirect(url_for('main.register'))
                
            document = request.files['documents']
            # I have made sure that the type of documents have a broad range
            if document and (document.filename.endswith(('.pdf', '.txt', '.png', 
                                                         '.jpg', '.jpeg', '.xlsx', '.xls'))):
                document_filename = secure_filename(document.filename)
                document_path = os.path.join(current_app.config['UPLOAD_FOLDER'], document_filename)
                document.save(document_path)
            else:
                flash('Invalid file type. Please upload a PDF, text, or image file.', 'danger')
                return redirect(url_for('main.register'))

        # Checking about the unique username, email and phone number
        # I have decided to only choose those 3 criteria to be unique means address, pincode, location, etc except these 3 can be same
        existing_user = None
        if role == 'customer':
            # Check if username, email, or phone number already exists in the Customer model
            existing_user = Customer.query.filter(
                (Customer.username == username) |
                (Customer.email == form.email.data) |
                (Customer.phone_number == form.phone_number.data)
            ).first()
        else:
            # Check if username, email, or phone number already exists in the Professional model
            existing_user = Professional.query.filter(
                (Professional.username == username) |
                (Professional.email == form.email.data) |
                (Professional.phone_number == form.phone_number.data)
            ).first()

        if existing_user:
            flash('Username, email, or phone number already exists. Please choose different values.', 'danger')
            return redirect(url_for('main.register'))

        # Create the new user if the the unique criteria of username, phone number and email is fulfilled
        if role == 'professional':
            expertise = form.expertise.data
            new_user = Professional(username=username,
                                    expertise=expertise,
                                    documents=document_filename, 
                                    location=location,
                                    pin_code=pin_code,
                                    phone_number=phone_number,
                                    address=address,
                                    email=email)
        else:
            new_user = Customer(username=username,
                                location=location,
                                pin_code=pin_code,
                                phone_number=phone_number,
                                address=address,
                                email=email)

        new_user.set_password(password)
        db.session.add(new_user)
        db.session.commit()

        flash('Registration successful.', 'success')
        return redirect(url_for('main.register'))
    
    return render_template('register.html', form=form)

#-----------------------------------------------------------------------------------------------------------------------------#

#-------------- 
# Admin routes 
#-------------- 
@main.route('/admin/login', methods=['GET', 'POST']) 
@nocache
def admin_login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        # Find the admin in the admin table of the database
        admin = Admin.query.filter_by(username=username).first()

        if admin and admin.check_password(password):
            login_user(admin)
            flash('Login successful!', 'success')
            return redirect(url_for('main.admin_dashboard'))
        else:
            flash('Login Unsuccessful. Please check username and password.', 'danger')

    return render_template('admin/login.html')

@main.route('/admin/dashboard') 
@login_required
@nocache
def admin_dashboard(): 
    if not isinstance(current_user, Admin):
        flash('Unauthorized access.','danger')
        return redirect(url_for('main.index')) 

    # Fetching customer, professional and services data for the purpose of constucting graph
    customers = Customer.query.all()
    professionals = Professional.query.all()
    services = Service.query.all()

    # Calculate the number of active and blocked customers
    active_customers = sum(1 for c in customers if not c.is_blocked)
    blocked_customers = sum(1 for c in customers if c.is_blocked)

    # Calculate the number of active and inactive professionals
    active_professionals = sum(1 for p in professionals if p.is_approved)
    inactive_professionals = sum(1 for p in professionals if not p.is_approved)

    # Total services
    total_services = len(services)

    # Creating the bar chart with Matplotlib
    fig, ax = plt.subplots(figsize=(8, 6))
    categories = ['Active Customers', 'Blocked Customers', 'Active Professionals', 'Inactive Professionals', 'Total Services']
    values = [active_customers, blocked_customers, active_professionals, inactive_professionals, total_services]

    # Giving different colour to different categories 
    ax.bar(categories, values, color=['green', 'red', 'blue', 'orange', 'purple'])

    # Adding labels for the x-axis, y-axis, and a title to make the graph informative and visually appealing
    ax.set_xlabel('Categories')
    ax.set_ylabel('Count')
    ax.set_title('Admin Dashboard Analysis')

    # Rotate the x-axis labels as earlier the names were overlapping because they are long 
    plt.xticks(rotation=45, ha="right")

    # Automatically adjusts spacing between plot elements to avoid overlap
    plt.tight_layout()

    # Save the plot to a BytesIO object with format as png
    img = BytesIO()
    plt.savefig(img, format='png')
    
    # Reset stream position to the beginning after plt.savefig() to enable reading the image data
    img.seek(0)

    # converting BytesIO image to base64 string so that it can be embedded in html
    img_base64 = base64.b64encode(img.getvalue()).decode('utf-8')

    # Close the figure to free memory
    plt.close(fig)

    return render_template('admin/dashboard.html', customers=customers, professionals=professionals, services=services, img_base64=img_base64)

@main.route('/admin/customer_info', methods=['GET', 'POST'])
@login_required
@nocache
def customer_info():
    if not isinstance(current_user, Admin):
        flash('Unauthorized access.','danger')
        return redirect(url_for('main.index'))
    
    # Get the search query from the form if it's POST
    search_query = request.form.get('search_query', '')
    
    if search_query:
        # Fetch customers filtered by the username, ilike was used because it makes search case-insensitive
        customers = Customer.query.filter(Customer.username.ilike(f'%{search_query}%')).all()
    else:
        # Fetch all customers if no search query
        customers = Customer.query.all()

    return render_template('admin/customer_info.html', customers=customers, search_query=search_query)

@main.route('/admin/professional_info', methods=['GET', 'POST'])
@login_required
@nocache
def professional_info():
    # Ensure only admins can access this route
    if not isinstance(current_user, Admin):
        flash('Unauthorized access.','danger')
        return redirect(url_for('main.index'))
    
    # Get the search query from the form if it's POST
    search_query = request.form.get('search_query', '')
    
    if search_query:
        # Fetch professionals filtered by the username (case-insensitive)
        professionals = Professional.query.filter(Professional.username.ilike(f'%{search_query}%')).all()
    else:
        # Fetch all professionals if no search query
        professionals = Professional.query.all()

    return render_template('admin/professional_info.html', professionals=professionals, search_query=search_query)

@main.route('/admin/services')
@login_required
@nocache
def services():
    if not isinstance(current_user, Admin):
        flash('Unauthorized access.','danger')
        return redirect(url_for('main.index'))
    
    # Fetch all services
    services = Service.query.all()

    return render_template('admin/services.html',  services=services)

# Route for approving the professional who registered new
@main.route('/admin/approve/<int:id>', methods=['POST'])
@login_required
@nocache
def approve_user(id):
    if not isinstance(current_user, Admin):
        flash('Unauthorized access.','danger')
        return redirect(url_for('main.index'))
    
    # fetching the professional to approve
    professional = Professional.query.get_or_404(id)

    # is_approved is False by default for professional
    professional.is_approved = True
    db.session.commit()
    flash(f'{professional.username} has been approved!', 'success')
    return redirect(url_for('main.professional_info'))

# Route for unapproving or we can say blocking a professional
@main.route('/admin/unapprove/<int:id>', methods=['POST'])
@login_required
@nocache
def unapprove_user(id):
    if not isinstance(current_user, Admin):
        flash('Unauthorized access.','danger')
        return redirect(url_for('main.index'))

    
    # fetching the professional to block
    professional = Professional.query.get_or_404(id)

    professional.is_approved = False
    db.session.commit()
    flash(f'{professional.username} has been blocked!', 'success')
    return redirect(url_for('main.professional_info'))

# Route for blocking the customer
@main.route('/admin/block_user/<int:id>', methods=['POST'])
@login_required
@nocache
def block_user(id):
    if not isinstance(current_user, Admin):
        flash('Unauthorized access.','danger')
        return redirect(url_for('main.index'))
    
    # fetching the customer to block
    customer = Customer.query.get_or_404(id)

    # is_blocked is True by default for customer
    customer.is_blocked = True
    db.session.commit()
    flash(f'{customer.username} has been blocked.', 'success')
    return redirect(url_for('main.customer_info'))

# Route for unblocking the customer
@main.route('/admin/unblock_user/<int:id>', methods=['POST'])
@login_required
@nocache
def unblock_user(id):
    if not isinstance(current_user, Admin):
        flash('Unauthorized access.','danger')
        return redirect(url_for('main.index'))
    
    # fetching the customer to unblock
    customer = Customer.query.get_or_404(id)

    customer.is_blocked = False
    db.session.commit()
    flash(f'{customer.username} has been unblocked.', 'success')
    return redirect(url_for('main.customer_info'))

# Route for creating a new service
@main.route('/admin/create_service', methods=['GET', 'POST'])
@login_required
@nocache
def create_service():
    if not isinstance(current_user, Admin):
        flash('Unauthorized access.','danger')
        return redirect(url_for('main.index'))

    if request.method == 'POST':
        name = request.form.get('name')
        price = request.form.get('price')
        time_required = request.form.get('time_required')
        description = request.form.get('description')
        field_of_service = request.form.get('field_of_service')
        
        service = Service(
            name=name, 
            price=price, 
            time_required=time_required, 
            description=description, 
            field_of_service=field_of_service
        )
        db.session.add(service)
        db.session.commit()
        flash('Service created successfully.', 'success')
        return redirect(url_for('main.services'))
    
    # Defining possible "field_of_service" options these are exactly same as the options of "expertise" in the "RegistrationForm" to avoid problems
    fields_of_service = [
        'Plumbing', 'Electrician', 'Cleaning', 'Landscaping', 'Handyman', 'Carpentry', 
        'Pest Control', 'HVAC', 'Painting', 'Roofing', 'Masonry', 'Glass Repair',
        'Flooring', 'Furniture Assembly', 'Appliance Repair', 'Computer Repair', 
        'Window Cleaning', 'Gutter Cleaning', 'Moving Services', 'Security Services'
    ]
    return render_template('admin/create_service.html', fields_of_service=fields_of_service)

# Route for updating the created services
@main.route('/admin/update_service/<int:id>', methods=['GET', 'POST'])
@login_required
@nocache
def update_service(id):
    if not isinstance(current_user, Admin):
        flash('Unauthorized access.','danger')
        return redirect(url_for('main.index'))

    # fetching the service to update
    service = Service.query.get_or_404(id)

    if request.method == 'POST':
        service.name = request.form.get('name')
        service.price = request.form.get('price')
        service.time_required = request.form.get('time_required')
        service.description = request.form.get('description')
        db.session.commit()
        flash('Service updated','success')
        return redirect(url_for('main.services'))
    return render_template('admin/update_service.html', service=service)

# Route for deleting the created services
@main.route('/admin/delete_service/<int:id>', methods=['POST'])
@login_required
@nocache
def delete_service(id):
    if not isinstance(current_user, Admin):
        flash('Unauthorized access.','danger')
        return redirect(url_for('main.index'))
    
    # fetching the service to delete
    service = Service.query.get_or_404(id)
    db.session.delete(service)
    db.session.commit()
    
    flash('Service deleted successfully', 'success')
    return redirect(url_for('main.services'))

#----------------------------------------------------------------------------------------------------------------------#

#-----------------
# Customer routes
#-----------------
@main.route('/customer/login', methods=['GET', 'POST'])
@nocache
def customer_login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        customer = Customer.query.filter_by(username=username).first()
        if customer and customer.check_password(password):
            if customer.is_blocked == False:
                login_user(customer)
                return redirect(url_for('main.customer_dashboard'))
            else:
                flash('You are blocked. Please contact the admin.', 'danger')
        else:
            flash('Login Unsuccessful. Please check username and password.', 'danger')
    return render_template('customer/login.html')

@main.route('/customer/dashboard')
@login_required
@nocache
def customer_dashboard():
    if not isinstance(current_user, Customer):
        flash('Unauthorized access.','danger')
        return redirect(url_for('main.index'))

    # Fetching all service requests made by the customer
    service_requests = ServiceRequest.query.filter_by(customer_id=current_user.id).all()
    services = Service.query.all()
    
    # Calculate counts for each status
    pending_count = sum(1 for request in service_requests if request.service_status == 'pending')
    accepted_count = sum(1 for request in service_requests if request.service_status == 'accepted')
    completed_count = sum(1 for request in service_requests if request.service_status == 'completed')
    closed_count = sum(1 for request in service_requests if request.service_status == 'closed')
    in_progress_count = sum(1 for request in service_requests if request.service_status == 'in_progress')
    
    # Creating the bar chart similiar to admin bar chart
    fig, ax = plt.subplots(figsize=(8, 6))
    categories = ['Pending', 'Accepted', 'In Progress', 'Completed', 'Closed']
    counts = [pending_count, accepted_count, in_progress_count, completed_count, closed_count]

    ax.bar(categories, counts, color=['red', 'green', 'blue', 'yellow', 'orange'])

    ax.set_xlabel('Request Status')
    ax.set_ylabel('Number of Requests')
    ax.set_title('Service Request Status Analysis')

    plt.xticks(rotation=45, ha="right")

    plt.tight_layout()

    img = BytesIO()
    plt.savefig(img, format='png')
    img.seek(0)
    img_base64 = base64.b64encode(img.getvalue()).decode('utf-8')
    plt.close(fig)

    return render_template('customer/dashboard.html', service_requests=service_requests, services=services, img_base64=img_base64)

# Route for the page for creating service requests
@main.route('/customer/create_request', methods=['GET'])
@login_required
@nocache
def create_request():
    if not isinstance(current_user, Customer):
        flash('Unauthorized access.','danger')
        return redirect(url_for('main.index'))

    # Fetch all available services for the dropdown menu
    services = Service.query.all()

    # distinct locations from the Customer model
    customer_locations = Customer.query.with_entities(Customer.location).distinct()

    # distinct locations from the Professional model
    professional_locations = Professional.query.with_entities(Professional.location).distinct()

    # Combining the unique locations from both Customer and Professional models
    locations = customer_locations.union(professional_locations).all()

    # Extract location values from the query result (tuples) using list comprehension
    locations = [location[0] for location in locations]
    
    # distinct pincodes from the Customer model
    customer_pincodes = Customer.query.with_entities(Customer.pin_code).distinct()

    # distinct pincodes from the Professional model
    professional_pincodes = Professional.query.with_entities(Professional.pin_code).distinct()

    # Combining the unique pincodes from both Customer and Professional models
    pincodes = customer_pincodes.union(professional_pincodes).all()

    # Extract pincodes values from the query result (tuples) using list comprehension
    pincodes = [pincode[0] for pincode in pincodes]

    return render_template('customer/create_request.html', services=services, locations=locations, pincodes=pincodes)

# Route for searching the services and see the result
@main.route('/customer/search_services', methods=['GET'])
def search_services():
    query = request.args.get('search_query', '')
    if query:
        results = Service.query.filter(Service.name.ilike(f'%{query}%')).all()
    else:
        results = []

    customer_locations = Customer.query.with_entities(Customer.location).distinct()
    professional_locations = Professional.query.with_entities(Professional.location).distinct()
    locations = customer_locations.union(professional_locations).all()
    locations = [location[0] for location in locations]

    customer_pincodes = Customer.query.with_entities(Customer.pin_code).distinct()
    professional_pincodes = Professional.query.with_entities(Professional.pin_code).distinct()
    pincodes = customer_pincodes.union(professional_pincodes).all()
    pincodes = [pincode[0] for pincode in pincodes]

    return render_template('customer/search_results.html', results=results,locations=locations,pincodes=pincodes)

# Route for requesting a service
@main.route('/customer/request_service', methods=['POST'])
@login_required
@nocache
def request_service():
    if not isinstance(current_user, Customer):
        flash('Unauthorized access.','danger')
        return redirect(url_for('main.index'))
    
    """Get the selected service ID (but actually the name of service is shown to and selected by the customer),
    location, and pin code from the form in the html.
    """
    service_id = request.form.get('service_id')
    location = request.form.get('location')
    pin_code = request.form.get('pin_code')

    # Retrieve the service to get the field of expertise
    service = Service.query.get(service_id)

    # new service request is created and added to the database
    new_request = ServiceRequest(
        customer_id=current_user.id,
        service_id=service_id,
        date_of_request=datetime.utcnow() + timedelta(hours=5, minutes=30),
        location=location,
        pin_code=pin_code,
        field_of_service=service.field_of_service)
    
    db.session.add(new_request)
    db.session.commit()
    
    flash('Service request submitted successfully!','success')
    return redirect(url_for('main.create_request'))

# Route for the page for viewing created service requests
@main.route('/customer/service_requests')
@login_required
@nocache
def service_requests():
    if not isinstance(current_user, Customer):
        flash('Unauthorized access.','danger')
        return redirect(url_for('main.index'))

    """all service requests will be shown except the ones that are closed even the completed ones will be shown for the rating the
    professional purpose, note this point that closed and completed are two different statuses,
    completed is done by professional whereas closed is done the customer.""" 
    service_requests = ServiceRequest.query.filter(ServiceRequest.customer_id == current_user.id,ServiceRequest.service_status != 'closed').all()

    return render_template('customer/service_requests.html', service_requests=service_requests)

@main.route('/customer/update_request/<int:id>', methods=['POST'])
@login_required
@nocache
def update_request(id):
    if not isinstance(current_user, Customer):
        flash('Unauthorized access.','danger')
        return redirect(url_for('main.index'))
    
    # Fetch the service request based on the ID
    request_service = ServiceRequest.query.get_or_404(id)

    request_service.remarks = request.form.get('remarks')

    db.session.commit()
    flash('Service request updated', 'success')
    return redirect(url_for('main.service_requests'))

@main.route('/customer/close_request/<int:id>', methods=['POST'])
@login_required
@nocache
def close_request(id):
    if not isinstance(current_user, Customer):
        flash('Unauthorized access.','danger')
        return redirect(url_for('main.index'))

    service_request = ServiceRequest.query.get_or_404(id)

    # changing the service status
    service_request.service_status = 'closed'

    # Get the professional assigned to the request
    professional = service_request.assigned_professional

    # Update rating and number of reviews if the customer rated the professional before closing the request
    try:
        rating = int(request.form.get("rating"))
        if 1 <= rating <= 5 and professional:
            # Calculate new average rating
            new_total_rating = (professional.rating * professional.num_reviews + rating) / (professional.num_reviews + 1)
            professional.rating = round(new_total_rating, 2)  # Round to 2 decimal places for display
            professional.num_reviews += 1
    except ValueError:
        pass

    db.session.commit()
    flash('Service request closed.', 'success')
    return redirect(url_for('main.service_requests'))

#--------------------------------------------------------------------------------------------------#

#----------------------------- 
# Service Professional routes 
#----------------------------- 
@main.route('/professional/login', methods=['GET', 'POST'])
@nocache
def professional_login():

    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        # Find the professional in the professional table in the database
        professional = Professional.query.filter_by(username=username).first()

        if professional and professional.check_password(password):
            if not professional.is_approved:
                flash('Your account is awaiting admin approval.', 'warning')
                return redirect(url_for('main.professional_login'))
            login_user(professional)
            flash('Login successful!', 'success')
            return redirect(url_for('main.professional_dashboard'))
        else:
            flash('Invalid username or password. Please try again.', 'danger')

    return render_template('professional/login.html')

@main.route('/professional/dashboard')
@login_required
@nocache
def professional_dashboard():
    if not (isinstance(current_user, Professional) and current_user.is_approved):
        flash('Unauthorized access.','danger')
        return redirect(url_for('main.index'))

    # fetching the professional data by using the current user id
    professional = Professional.query.get(current_user.id)

    """ I had to add 3 more fields in the professional table to tackle some problems, the problem was that if a professional reject a service
        it status is changed globaly to 'rejected' because of which other professional were also not able to see the requests so i added 3 new 
        fields which is of type string in which ids of services that professional rejected, accepted and completed
        are stored and are separated by commas.
        """
    # Split the stored comma-separated string of request IDs into a list of strings
    rejected_requests_list = current_user.rejected_requests.split(',')  if current_user.rejected_requests else []
    accepted_requests_list = current_user.accepted_requests.split(',')  if current_user.accepted_requests else []
    accepted_requests_list = [int(id) for id in accepted_requests_list]
    accepted_requests = ServiceRequest.query.filter(ServiceRequest.service_status.in_(['accepted']))
    accepted_requests = [req for req in accepted_requests if req.id  in accepted_requests_list]
    completed_requests_list = current_user.completed_requests.split(',')  if current_user.completed_requests else []
    
    # Get the total number of requests in each category
    num_rejected = len(rejected_requests_list)
    num_accepted = len(accepted_requests)
    num_completed = len(completed_requests_list)

    rejected_requests = current_user.rejected_requests.split(',')  if current_user.rejected_requests else []

    # Converts the id which is in string type to integer type so now it is a list of ids of type integer
    rejected_requests = [int(id) for id in rejected_requests] 

    """ As any other professional rejected a service it status will change so to find pending requests for a professional
    we only have to consider those whose pending and those who status is rejected but are not in the rejected list of the
    professional in question. The another logic for pending request is that location is if the location and pincode filter
    is used then the pending_requests get filter according to that so that if location or pincode match with the location
    or pincode of the professional if mentioned as filter then that requests will be considered only.
    """
    pending_requests = ServiceRequest.query.filter(ServiceRequest.service_status.in_(['pending', 'rejected']),
                                                   ServiceRequest.field_of_service == current_user.expertise,
                                                   or_(
                                                        and_
                                                            (ServiceRequest.location.in_([None, ""]),
                                                            ServiceRequest.pin_code.in_([None, ""])),
                                                        or_
                                                            (ServiceRequest.location == current_user.location,
                                                            ServiceRequest.pin_code == current_user.pin_code))).all()
    
    # Fetch all requests that are in the pending_requests, but exclude the ones rejected by the current professional
    pending_requests = [req for req in pending_requests if req.id not in rejected_requests]
    num_pending = len(pending_requests)

    # Calculating in-progress requests by usign the formula "in progress = accepted - completed"
    in_progess_requests = ServiceRequest.query.filter(ServiceRequest.service_status.in_(['in_progress']))
    in_progess_requests = [req for req in in_progess_requests if req.id  in accepted_requests_list]
    num_in_progress = len(in_progess_requests)

    # Creating the bar chart similiar to admin bar chart
    fig, ax = plt.subplots(figsize=(8, 6))
    categories = ['Rejected', 'Accepted', 'Completed', 'Pending', 'In Progress']
    values = [num_rejected, num_accepted, num_completed, num_pending, num_in_progress]

    ax.bar(categories, values, color=['red', 'green', 'blue', 'yellow', 'orange'])

    ax.set_xlabel('Request Status')
    ax.set_ylabel('Count')
    ax.set_title('Service Request Statistics')

    plt.xticks(rotation=45, ha="right")

    plt.tight_layout()

    img = BytesIO()
    plt.savefig(img, format='png')
    img.seek(0)
    img_base64 = base64.b64encode(img.getvalue()).decode('utf-8')
    plt.close(fig)

    # Render the dashboard page with the plot
    return render_template('professional/dashboard.html', img_base64=img_base64,professional=professional)

@main.route('/professional/pending_requests')
@login_required
@nocache
def pending_requests():
    
    # fetching the pending requests for a professional in the same way done in dashboard
    rejected_requests = current_user.rejected_requests.split(',') if current_user.rejected_requests else []
    rejected_requests = [int(id) for id in rejected_requests]
    
    """ If the expertise match and location or pincode are not mentioned then will be no problem for the professional to
    accept the request but if expertise is not matched then no matter if the location or pincode match, and if expertise match
    but anyone of the pincode or location match it can accept else not. So on this logic I filter every case and only show the
    service request that match these conditions on the pending requests page.
    """
    pending_requests = ServiceRequest.query.filter(ServiceRequest.service_status.in_(['pending', 'rejected']),
                                                   ServiceRequest.field_of_service == current_user.expertise,
                                                   or_(
                                                        and_
                                                            (ServiceRequest.location.in_([None, ""]),
                                                            ServiceRequest.pin_code.in_([None, ""])),
                                                        or_
                                                            (ServiceRequest.location == current_user.location,
                                                            ServiceRequest.pin_code == current_user.pin_code))).all()
    
    pending_requests = [req for req in pending_requests if req.id not in rejected_requests]

    return render_template('professional/pending_requests.html', pending_requests=pending_requests)

@main.route('/professional/accepted_requests')
@login_required
@nocache
def accepted_requests():

    # fetching accepted service requests for professionals
    accepted_requests = ServiceRequest.query.filter(
        ServiceRequest.service_status.in_(['accepted', 'in_progress']),
        ServiceRequest.professional_id == current_user.id).all()

    """ Fetching customer data associated with each service request so that professional can see the information of customer
    who have requested the services to actually do the service
    """
    customer_data = []
    for request in accepted_requests:
        customer = Customer.query.get(request.customer_id)
        customer_data.append((request, customer))

    return render_template('professional/accepted_requests.html', customer_data=customer_data)

# Route for accepting service request for professional
@main.route('/professional/accept_service/<int:id>', methods=['POST'])
@login_required
@nocache
def accept_service_request(id):
    if not (isinstance(current_user, Professional) and current_user.is_approved):
        flash('Unauthorized access.','danger')
        return redirect(url_for('main.index'))
    
    # fetching the service request to accept
    request_service = ServiceRequest.query.get_or_404(id)

    request_service.service_status = 'accepted'
    request_service.date_of_acceptance = datetime.utcnow() + timedelta(hours=5, minutes=30) # adding timedelta convert the time to IST
    request_service.professional_id = current_user.id  # Assign the professional to the request

    """ Check if the current user has any accepted requests stored and Split the stored comma-separated string of accepted request IDs
    into a list of strings but ff no accepted requests exist, initialize an empty list.
    """
    accepted_requests_list = current_user.accepted_requests.split(',') if current_user.accepted_requests else []

    # Check if the given `id` is not already in the list of accepted requests
    if str(id) not in accepted_requests_list:
        # If not present, append the `id` (converted to a string) to the list
        accepted_requests_list.append(str(id))

    # Join the list of accepted request IDs back into a comma-separated string for storage
    current_user.accepted_requests = ','.join(accepted_requests_list)

    db.session.commit()

    flash('You have accepted the service request.','success')
        
    return redirect(url_for('main.pending_requests'))

# Route for rejecting service request for professional
@main.route('/professional/reject_service/<int:id>', methods=['POST'])
@login_required
@nocache
def reject_service_request(id):
    if not (isinstance(current_user, Professional) and current_user.is_approved):
        flash('Unauthorized access.','danger')
        return redirect(url_for('main.index'))

    # fetching the service request to accept
    request_service = ServiceRequest.query.get_or_404(id)

    request_service.service_status = 'rejected'

    # Same process like accepted_requests list
    rejected_requests = current_user.rejected_requests.split(',') if current_user.rejected_requests else []
    
    if str(id) not in rejected_requests:
        rejected_requests.append(str(id))
    
    current_user.rejected_requests = ','.join(rejected_requests)
    
    db.session.commit()

    flash('You have rejected the service request.','success')
    return redirect(url_for('main.pending_requests'))

# Route for updating accepted service request for professional
@main.route('/professional/update_service_status/<int:id>', methods=['POST'])
@login_required
@nocache
def update_service_status(id):
    if not (isinstance(current_user, Professional) and current_user.is_approved):
        flash('Unauthorized access.','danger')
        return redirect(url_for('main.index'))
    
    request_service = ServiceRequest.query.get_or_404(id)
    
    # get the service status from the dropdown options, form was used in html to get the service_status
    new_status = request.form.get('service_status')
    request_service.service_status = new_status

    if new_status == 'in_progress':
        db.session.commit()

    # If the status is updated to 'completed', append the request ID to completed_requests
    if new_status == 'completed':
        request_service.date_of_completion = datetime.utcnow() + timedelta(hours=5, minutes=30)

        # Same process for adding the completed requests like the rejected and accepted
        completed_requests_list = current_user.completed_requests.split(',') if current_user.completed_requests else []

        if str(id) not in completed_requests_list:
            completed_requests_list.append(str(id))
        
        current_user.completed_requests = ','.join(completed_requests_list)
        
        db.session.commit()

    flash('Service status updated successfully.','success')
    return redirect(url_for('main.accepted_requests'))

#---------------------------------------------------------------------------------------------------------------------------#

#-----------------
# Logout routes
#-----------------

# Logout for Admin
@main.route('/admin/logout')
@login_required
@nocache
def admin_logout():
    logout_user()
    session.clear()
    return redirect(url_for('main.index'))

# Logout for Customer
@main.route('/customer/logout')
@login_required
@nocache
def customer_logout():
    logout_user()
    session.clear()
    return redirect(url_for('main.index'))

# Logout for Professional
@main.route('/professional/logout')
@login_required
@nocache
def professional_logout():
    logout_user()
    session.clear()
    return redirect(url_for('main.index'))
#-----------------------------------------------------------------------------------------#