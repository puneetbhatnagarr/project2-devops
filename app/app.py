# =====================================================================
# 1. IMPORT LIBRARIES
# =====================================================================
import uuid                           # Used to generate unique random IDs
from datetime import datetime         # Used to get the current date and time
from flask import Flask, request, render_template_string # The web framework
import boto3                          # The AWS SDK for Python
from werkzeug.utils import secure_filename # Sanitizes filenames for security

# Create the Flask application instance
app = Flask(__name__)

# =====================================================================
# 2. CONNECT TO AWS SERVICES
# =====================================================================
# Because we attached an IAM Role to our EC2 server, we don't need 
# to pass any passwords or access keys here. Boto3 automatically 
# grabs the temporary credentials from the EC2 environment.
s3 = boto3.client('s3', region_name='ap-south-1')
dynamodb = boto3.resource('dynamodb', region_name='ap-south-1')
table = dynamodb.Table('StudentData')

# The exact name of our S3 bucket created by Terraform
BUCKET_NAME = "student-uploads-2ca4b157" 

# =====================================================================
# 3. THE FRONTEND (HTML & CSS)
# =====================================================================
# This is a multi-line string containing the HTML code.
# I added CSS inside the <style> tags to make it look stylish.
HTML_FORM = """
<!doctype html>
<html lang="en">
<head>
    <meta charset="utf-8">
    <title>Student Registration</title>
    <style>
        /* General page styling */
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background-color: #f4f7f6;
            display: flex;
            justify-content: center;
            align-items: center;
            height: 100vh;
            margin: 0;
        }
        /* The white box containing the form */
        .form-container {
            background-color: #ffffff;
            padding: 30px 40px;
            border-radius: 10px;
            box-shadow: 0 4px 8px rgba(0,0,0,0.1);
            width: 100%;
            max-width: 400px;
        }
        /* The heading inside the box */
        h2 {
            text-align: center;
            color: #333;
            margin-bottom: 20px;
        }
        /* Styling for all input fields */
        input[type="text"], input[type="email"], input[type="file"] {
            width: 100%;
            padding: 10px;
            margin: 8px 0 15px 0;
            border: 1px solid #ccc;
            border-radius: 5px;
            box-sizing: border-box; /* Ensures padding doesn't affect width */
        }
        /* Styling for the submit button */
        input[type="submit"] {
            width: 100%;
            background-color: #4CAF50;
            color: white;
            padding: 12px;
            border: none;
            border-radius: 5px;
            cursor: pointer;
            font-size: 16px;
            font-weight: bold;
            transition: background-color 0.3s;
        }
        /* Button hover effect */
        input[type="submit"]:hover {
            background-color: #45a049;
        }
    </style>
</head>
<body>

<div class="form-container">
    <h2>Student Registration</h2>
    <form method="post" enctype="multipart/form-data">
        <label>First Name</label>
        <input type="text" name="fname" required>
        
        <label>Last Name</label>
        <input type="text" name="lname" required>
        
        <label>Email</label>
        <input type="email" name="email" required>
        
        <label>Phone Number</label>
        <input type="text" name="number" required>
        
        <label>Profile Image</label>
        <input type="file" name="file" required>
        
        <input type="submit" value="Upload Data">
    </form>
</div>

</body>
</html>
"""

# =====================================================================
# 4. THE BACKEND LOGIC (FLASK ROUTE)
# =====================================================================
# This tells Flask: "When someone visits the main page (/), run this function."
# It handles both GET (loading the page) and POST (submitting the form).
@app.route('/', methods=['GET', 'POST'])
def upload_file():
    # If the user just opened the link in a browser (GET request)
    if request.method == 'GET':
        return HTML_FORM # Show them the form

    # If the user clicked the submit button (POST request)
    if request.method == 'POST':
        # Extract the text data from the form
        fname = request.form.get('fname')
        lname = request.form.get('lname')
        email = request.form.get('email')
        number = request.form.get('number')
        
        # Extract the uploaded file
        file = request.files.get('file')

        # Make sure a file was actually uploaded
        if file and file.filename != '':
            # Clean the filename (removes potentially dangerous characters like ../)
            filename = secure_filename(file.filename)
            
            # Generate a unique ID for this student (e.g., "123e4567-e89b-12d3...")
            student_id = str(uuid.uuid4())
            
            # Create a unique timestamp (e.g., "20261025_143000")
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            
            # Combine them to make a unique S3 filename (prevents overwriting)
            s3_filename = f"{student_id}_{timestamp}_{filename}"

            try:
                # 1. UPLOAD IMAGE TO S3
                # (file, bucket_name, new_filename)
                s3.upload_fileobj(file, BUCKET_NAME, s3_filename)
                
                # 2. SAVE TEXT DATA TO DYNAMODB
                # We put a dictionary (key-value pairs) into the table
                table.put_item(
                    Item={
                        'StudentID': student_id,   # The partition key
                        'FirstName': fname,
                        'LastName': lname,
                        'Email': email,
                        'Number': number,
                        'ImageName': s3_filename,
                        'Timestamp': timestamp,
                        'Status': 'LOCKED'         # Your table lock requirement
                    }
                )

                # If everything worked, show a success message
                return """
                <div style="font-family: Arial; text-align: center; margin-top: 50px;">
                    <h2 style="color: green;">Success!</h2>
                    <p>Data saved to DynamoDB and S3.</p>
                    <a href="/">Go back</a>
                </div>
                """
                
            except Exception as e:
                # If something went wrong (e.g., AWS permissions), show the error
                return f"""
                <div style="font-family: Arial; text-align: center; margin-top: 50px;">
                    <h2 style="color: red;">Error!</h2>
                    <p>{str(e)}</p>
                    <a href="/">Go back</a>
                </div>
                """
        else:
            return "<h2>Error: No file selected.</h2>"

# =====================================================================
# 5. START THE SERVER
# =====================================================================
# This block only runs if you execute "python app.py" directly.
if __name__ == "__main__":
    # host="0.0.0.0" makes it accessible from outside the container/EC2
    # port=8000 is the port it listens on
    app.run(host="0.0.0.0", port=8000)