from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, SelectField, ValidationError, FileField
from wtforms.validators import DataRequired, EqualTo, Length

# This form allows professionals and customers to register if they are new to this app
class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=4, max=80)])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    
    role = SelectField('Role', choices=[
        ('customer', 'Customer'), 
        ('professional', 'Service Professional')
    ], validators=[DataRequired()])

    location = StringField('Location', validators=[DataRequired()])
    pin_code = StringField('Pin Code', validators=[DataRequired(), Length(min=5, max=10)])
    phone_number = StringField('Phone Number', validators=[DataRequired(), Length(min=10, max=15)])
    email = StringField('Email', validators=[DataRequired(), Length(max=120)])
    address = StringField('Address', validators=[DataRequired(), Length(max=200)])
    
    # Expertise field for professionals only, it is exactly same as the field_of_service of service and service request
    expertise = SelectField('Field of Expertise', choices=[
        ('Plumbing', 'Plumbing'),
        ('Electrician', 'Electrician'),
        ('Cleaning', 'Cleaning'),
        ('Landscaping', 'Landscaping'),
        ('Handyman', 'Handyman'),
        ('Pest Control', 'Pest Control'),
        ('HVAC', 'HVAC'),
        ('Painting', 'Painting'),
        ('Roofing', 'Roofing'),
        ('Masonry', 'Masonry'),
        ('Glass Repair', 'Glass Repair'),
        ('Flooring', 'Flooring'),
        ('Furniture Assembly', 'Furniture Assembly'),
        ('Appliance Repair', 'Appliance Repair'),
        ('Computer Repair', 'Computer Repair'),
        ('Window Cleaning', 'Window Cleaning'),
        ('Gutter Cleaning', 'Gutter Cleaning'),
        ('Moving Services', 'Moving Services'),
        ('Security Services', 'Security Services')
    ], validators=[DataRequired()])

    documents = FileField('Upload Documents') 
    submit = SubmitField('Register')
    
    def validate(self, extra_validators=None):
        # Perform the usual validation by calling the parent class's validate method
        # This will ensure any default form validation logic is applied
        if not super().validate(extra_validators=extra_validators): # in this case extra_validators are None
            return False

        # Conditional validation based on the user's role
        if self.role.data == 'professional':
            # Check if 'expertise' field is filled for 'professional' role
            # Professionals are required to have an expertise field filled
            if not self.expertise.data:
                self.expertise.errors.append('Field of expertise is required for professionals.')
                return False

            # Check if 'documents' field is filled for 'professional' role
            # Professionals must upload relevant documents to proceed
            if not self.documents.data:
                self.documents.errors.append('Document upload is required for professionals.')
                return False 

        # If the role is 'customer', we do not validate 'expertise' or 'documents'
        # This allows customers to skip those fields
        return True