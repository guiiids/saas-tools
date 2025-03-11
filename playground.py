import os

# Check if the SENDGRID_API_KEY environment variable is set
api_key = os.getenv('SENDGRID_API_KEY')

if api_key:
    print("SENDGRID_API_KEY is set correctly.")
   
else:
    print("SENDGRID_API_KEY is not set. Please set it in your system environment variables.")