# Importing the intialize function to initialize the Flask app
from app import initialize_app

# Create an instance of the Flask app named "app"
app = initialize_app()

# So that code only run when script is being run directly not when it is imported
if __name__ == "__main__":
    app.run(debug=True) # Starts the web server and extra features like telling us errors