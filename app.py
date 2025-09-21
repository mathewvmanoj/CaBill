from flask import Flask, render_template, request, redirect, url_for, session, jsonify, make_response
import bcrypt
from config import Config
from pymongo import MongoClient
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import csv
from io import StringIO
from functools import wraps
from chatbot_final import *
from pathlib import Path


# Initialize Flask app
app = Flask(__name__)
app.config.from_object(Config)

base_dir = Path(__file__).resolve().parent  # Directory of the current script
file_path = base_dir / "static" / "Sample_Fall 2024.xlsx"  # Construct the file path

# Check if the file exists
if not file_path.exists():
    raise FileNotFoundError(f"Excel file not found at: {file_path}")

# Load the Excel file and clean up column names
excel_data = pd.read_excel(file_path, sheet_name='Activities - Groups') 
excel_data.columns = excel_data.columns.str.strip() 

# Initializing the client DB
client = MongoClient(Config.MONGO_URI, tlsAllowInvalidCertificates=True)
db = client['loginDB']
users = db['users']

@app.route('/')
def home():
    return redirect(url_for('login'))

# Registration Route
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        # Validating the input
        if not username or not password:
            return jsonify({"error": "Username and password are required!"}), 400

        # Checking if user already exists
        existing_user = users.find_one({'username': username})
        if existing_user:
            return jsonify({"error": "User already exists!"}), 400

        # Bicrypting the password
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

        # Inserting the user into MongoDB
        db.users.insert_one({'username': username, 'password': hashed_password})
        return jsonify({"message": "Registration successful!"}), 201

    # Rendering registration page
    return render_template('register.html')

# Login Route
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        role = request.form.get('roles')  # Correcting the form name to match 'roles'

        # Checking if both username and password are provided
        if not username or not password:
            # return jsonify({"error": "Username and password are required!"}), 400
            return render_template('login.html', error="Username and password are required!")
        if not role:
            return render_template('login.html', error="Please select a role!")

        # Finding the user in MongoDB by username
        user = users.find_one({'username': username})
        if user and bcrypt.checkpw(password.encode('utf-8'), user['password']):
            session['username'] = username  # Set session for logged-in user

            # Retrieving and checking role
            if user.get('role') == role:
                # Redirect to the respective role's dashboard
                if role == 'Faculty':
                    return redirect(url_for('faculty'))
                elif role == 'Finance':
                    return redirect(url_for('finance'))
                else:
                    render_template('login.html', error="Invalid role specified")
            else:
                return render_template('login.html', error="Role mismatch!")
        else:
             return render_template('login.html', error="Invalid username or password!")

    # Rendering login page if request is GET
    return render_template('login.html')


# A decorator for role-based access control
def role_required(required_role):

    def decorator(func):

        @wraps(func)

        def wrapped_function(*args, **kwargs):

            # Check if the user is logged in and has the correct role

            if 'username' in session:

                user = users.find_one({'username': session['username']})

                if user and user.get('role') == required_role:

                    return func(*args, **kwargs)

                else:

                    return render_template('error.html', error="Unauthorized access!"), 403

            else:

                return redirect(url_for('login'))

        return wrapped_function

    return decorator

# Finance Route
@app.route('/finance', methods=['GET', 'POST'])
@role_required('Finance')
def finance():
    if 'username' in session:  
        # Get filter parameters from query string
        from_date = request.args.get('from_date')
        to_date = request.args.get('to_date')  
        transactions, messages = finance_faculty_check(from_date, to_date)
        return render_template('finance.html', transactions=transactions, messages=messages)  # Render the timesheet if the user is logged in
    else:
        return redirect(url_for('login'))  # Redirect to login if not authenticated

# Download button functionality
@app.route('/download_finance_report', methods=['GET'])
@role_required('Finance')
def download_finance_report():
    if 'username' in session:
         # Get filter parameters from the request
        from_date = request.args.get('from_date')  # e.g., "2024-01-01"
        to_date = request.args.get('to_date')  # e.g., "2024-01-31"
        
        # Fetch filtered data
        transactions, _ = finance_faculty_check(from_date, to_date)
        if not transactions:
            return jsonify({"error": "No transactions found for the given date range."}), 404
        
        # Generate CSV content
        si = StringIO()
        csv_writer = csv.DictWriter(si, fieldnames=["Faculty Name", "Hours Worked", "Status"])
        csv_writer.writeheader()
        # Modify discrepancies symbols (if needed) before writing rows
        for transaction in transactions:
            if transaction["Status"] == "✓":
                transaction["Status"] = "Hours Matched"  
            else:
                transaction["Status"] = "Hours Unmatched"
            csv_writer.writerow(transaction)
        # Create a response to send the CSV file
        response = make_response(si.getvalue().encode('utf-8'))
        response.headers["Content-Disposition"] = "attachment; filename=report_profiles.csv"
        response.headers["Content-Type"] = "text/csv;charset=utf-8"
        return response
    else:
        return redirect(url_for('login'))  # Redirect to login if not authenticated

# Processing Faculty Details in Finance Page
def finance_faculty_check(from_date=None, to_date=None):
    # Parse dates if provided
    from_date = datetime.strptime(from_date, "%Y-%m-%d") if from_date else None
    to_date = datetime.strptime(to_date, "%Y-%m-%d") if to_date else None
    # Fetching all user data
    transactions = []
    messages = []
    faculty_hours = {}
    faculty_records = users.find({'role': 'Faculty'})

    for faculty in faculty_records:
        faculty_name =faculty['username']
        timesheets = faculty.get('timesheets', [])
        status = faculty.get('status', '✗')
        if not timesheets:
            continue

        for timesheet in timesheets:
            for week in ['week1', 'week2']:
                for entry in timesheet.get(week, []):
                    # Calculate discrepancies
                    hours_worked = int(entry['hoursWorked'])
                    course_code = entry['courseCode']
                    entry_date = datetime.strptime(entry['date'], "%Y-%m-%d")

                    # Filter by date range
                    if from_date and entry_date < from_date:
                        continue
                    if to_date and entry_date > to_date:
                        continue   

                    # Match instructor's record in the Excel schedule
                    faculty_match = excel_data[excel_data['Instructor'] == faculty_name]
                    date_match = faculty_match[faculty_match['Start Date'] == entry_date.strftime("%m/%d/%Y")] # Convert datetime object to string in 'MM/DD/YYYY' format
                    course_match = date_match[date_match['Subject'].str.contains(course_code, na=False)]

                    if len(course_match) > 1:
                        total_hours = sum(time_cal(match) for _, match in course_match.iterrows())
                    elif len(course_match) == 1:
                        total_hours = time_cal(course_match.iloc[0])
                    else:
                        total_hours = 0
                        messages.append(f"No schedule entry found for {faculty_name} on {entry['date']} for course {course_code}")


                    if faculty_name not in faculty_hours:
                        faculty_hours[faculty_name] = hours_worked
                    else:
                        faculty_hours[faculty_name] += hours_worked
                    # faculty_hours[faculty_name] = faculty_hours.get(faculty_name, 0) + hours_worked
                    timetable = extract_timetable(excel_data, faculty_name, course_code)
                    # Check for discrepancies
                    if status == '✓':
                        continue
                    if isinstance(timetable, pd.DataFrame):
                        for _, row in timetable.iterrows():
                            # Calculate the hours worked for this specific schedule entry
                            start_time = row['Start Time']
                            end_time = row['End Time']
                            hours_worked = calculate_hours_for_schedule(start_time, end_time)
                            
                            # Check for discrepancies with the database
                            status = check_discrepancies_with_database(status, faculty_name, course_code, row, hours_worked)
                    else:
                        status = '✓' if faculty_hours[faculty_name] == total_hours else '✗'
                        
        if faculty_hours.get(faculty_name, 0) > 0:
            transactions.append({
                "Faculty Name": faculty_name,
                #"Hours Worked": faculty_hours[faculty_name],
                "Hours Worked": faculty_hours.get(faculty_name, 0),
                "Status": status
            })
    return transactions, messages

def extract_timetable(excel_data, instructor_name, course_code):
    """
    Extracts the timetable for the given instructor and course code.
    Ensures strict matching for the instructor and partial matching for the course code.
    """
    # Clean the data by stripping spaces and converting to lowercase for consistency
    excel_data['Instructor'] = excel_data['Instructor'].str.strip().str.lower()
    excel_data['Subject'] = excel_data['Subject'].str.strip().str.lower()

    # Clean the inputs
    instructor_name = instructor_name.strip().lower()
    course_code = course_code.strip().lower()

    # Filter data: strict match for instructor, partial match for course code
    filtered_data = excel_data[
        (excel_data['Instructor'] == instructor_name) &  # Exact match for instructor
        (excel_data['Subject'].str.startswith(course_code))  # Partial match at the start of the subject
    ]
    
    if filtered_data.empty:
        return f"No timetable found for Instructor: {instructor_name}, Course: {course_code}"
    
    # Convert 'Start Date' and 'End Date' columns to datetime objects
    filtered_data = filtered_data.copy()
    filtered_data.loc[:, 'Start Date'] = pd.to_datetime(filtered_data['Start Date'], format='%m/%d/%Y')
    filtered_data.loc[:, 'End Date'] = pd.to_datetime(filtered_data['End Date'], format='%m/%d/%Y')



    #filtered_data['Start Date'] = pd.to_datetime(filtered_data['Start Date'], format='%m/%d/%Y')
    filtered_data['End Date'] = pd.to_datetime(filtered_data['End Date'], format='%m/%d/%Y')
    
    # Extract relevant timetable details
    timetable_details = filtered_data[['Start Date', 'End Date', 'Start Time', 'End Time', 'Days of the Week']]
    return timetable_details

def get_dates_for_weekday(start_date, end_date, weekdays):
    """
    Returns all dates within the given range that fall on the specified weekdays.
    """
    day_mapping = {
        "M": 0,  # Monday
        "T": 1,  # Tuesday
        "W": 2,  # Wednesday
        "Th": 3,  # Thursday
        "F": 4,  # Friday
        "Sa": 5,  # Saturday
        "Su": 6   # Sunday
    }

    start_date = datetime.strptime(start_date, "%m/%d/%Y")
    end_date = datetime.strptime(end_date, "%m/%d/%Y")
    target_days = [day_mapping.get(day.upper()) for day in weekdays]

    if None in target_days:
        raise ValueError("Invalid weekday abbreviation.")

    dates = []
    current_date = start_date
    while current_date <= end_date:
        if current_date.weekday() in target_days:
            dates.append(current_date.strftime("%m/%d/%Y"))
        current_date += timedelta(days=1)

    return dates

def calculate_hours_for_schedule(start_time, end_time):
    """
    Calculate the hours worked for a specific schedule entry.
    """
    if isinstance(start_time, datetime):
        start_time = start_time.time()
    if isinstance(end_time, datetime):
        end_time = end_time.time()

    today = datetime.today().date()
    
    start_datetime = datetime.combine(today, start_time)
    end_datetime = datetime.combine(today, end_time)
    
    time_diff = end_datetime - start_datetime
    total_hours_per_class = time_diff.total_seconds() / 3600  # Convert seconds to hours
    
    return total_hours_per_class


def check_discrepancies_with_database(status, instructor_name, course_code, timetable, hours_worked):
    """
    Check if the extracted timetable matches the database records for day, date, and hours worked.
    """
    # Query MongoDB for instructor and course code
    db_data = users.find({"username": instructor_name, "timesheets.week1.courseCode": course_code})

    # Loop through each record in the database
    for record in db_data:
        print(f"Checking record for instructor {instructor_name}, course code {course_code}...")

        for timesheet in record['timesheets']:
            for week_entry in timesheet.get('week1', []):
                # Compare course codes
                if week_entry['courseCode'] == course_code:
                    db_days = week_entry['day']  # Days stored in MongoDB (e.g., "Tuesday")

                    # Check for day discrepancy
                    timetable_days = timetable['Days of the Week']
                    day_mapping = {"M":"Monday","T": "Tuesday", "W": "Wednesday", "Th": "Thursday", "F": "Friday","Sa":"Saturday"}
                    timetable_day = day_mapping.get(timetable_days, timetable_days)  # Apply this on Excel data
                    

                    # Check for date discrepancy
                    timetable_start_date = timetable['Start Date'].strftime('%m/%d/%Y')  # Directly use the Timestamp object
                    timetable_end_date = timetable['End Date'].strftime('%m/%d/%Y')  # Directly use the Timestamp object

                    calculated_dates = get_dates_for_weekday(timetable_start_date,
                                                             timetable_end_date,
                                                             timetable_days)

                    calculated_dates = [datetime.strptime(date_str, "%m/%d/%Y").date() for date_str in calculated_dates]
        

                    # Get the corresponding database date and days
                    db_date_str = week_entry['date']  # Database date as a string
                    db_date = datetime.strptime(db_date_str, "%Y-%m-%d").date() # Convert to datetime

                    # Calculate hours from Excel timetable and compare with database
                    db_hours_worked = float(week_entry['hoursWorked'])

                    if (db_days != timetable_day) :
                        status = '✗'
                    elif not db_date in calculated_dates:
                        status = '✗'
                    elif hours_worked != db_hours_worked:
                        status = '✗'
                    else:
                        status = '✓'
    
    return status
 


# Finance comparision code
def time_cal(course_match):
    time_format = "%H:%M:%S"
    start_time = datetime.strptime(str(course_match.get('Start Time')), time_format)
    end_time = datetime.strptime(str(course_match['End Time']), time_format)
    
    # Calculate the difference (which will be a timedelta object)
    time_diff = end_time - start_time
    
    # Get the total hours spent
    total_hours = time_diff.total_seconds() / 3600  # Convert seconds to hours
    total_hours = np.ceil(total_hours).astype(int)
    return total_hours

# Updating the Status based on the changes in the UI
@app.route('/update_status', methods=['POST'])
def update_status():
    data = request.json
    faculty_name = data.get('faculty_name')
    status = data.get('status')

    if not faculty_name or status not in ['✓', '✗']:
        return jsonify({"error": "Invalid data"}), 400

    # Update the record in the database
    result = users.update_one(
        {"username": faculty_name},
        {"$set": {"status": status}}
    )

    if result.modified_count > 0:
        return jsonify({"message": "Status updated successfully"}), 200
    else:
        return jsonify({"error": "No changes made"}), 400

@app.route('/faculty_details/<faculty_name>', methods=['GET'])
@role_required('Finance')
def faculty_details(faculty_name):
    if 'username' in session:  # Ensure the user is authenticated
        faculty = users.find_one({'role': 'Faculty', 'username': faculty_name})
        if not faculty:
            return f"Faculty '{faculty_name}' not found.", 404

        # Extract relevant details
        details = []
        timesheets = faculty.get('timesheets', [])
        for timesheet in timesheets:
            for week in ['week1', 'week2']:
                for entry in timesheet.get(week, []):
                    details.append({
                        "Date": entry.get('date'),
                        "Day": entry.get('day'),
                        "Course_Code": entry.get('courseCode'),
                        "Hours_Worked": entry.get('hoursWorked'),
                        "Comments": entry.get('comments', "N/A")
                    })

        return render_template('faculty_view.html', faculty_name=faculty_name, details=details)
    else:
        return redirect(url_for('faculty'))  # Redirect to login if not authenticated

@app.route('/submit_timesheet', methods=['POST'])
@role_required('Faculty')
def submit_timesheet():
    if 'username' not in session:
        # Redirect to login if not authenticated
        return jsonify({'status': 'error', 'message': 'User not authenticated'}), 401

    # Retrieve JSON  data from the request body
    data = request.get_json()

    start_date = data.get('start_date')
    end_date = data.get('end_date')
    timesheet_data = data.get('timesheet_data')
    confirm_override = data.get('confirm_override', False)

    # Log received data
    print(f"Received: start_date={start_date}, end_date={end_date}, timesheet_data={timesheet_data}")

    # Process each timesheet entry
    for entry in timesheet_data:
        date = entry['date']
        day = entry['day']
        course_code = entry['course_code']
        hours_worked = entry['hours_worked']
        comments = entry['comments']

        # Validate hours worked
        if not hours_worked or not hours_worked.strip().replace('.', '', 1).isdigit():
            return jsonify({'status': 'error', 'message': 'Please provide a valid number for hours worked!'}), 400
        
        hours_worked = float(hours_worked)

        # Check for existing entry
        existing_entry = users.find_one({
            'username': session['username'],
            'timesheets.week1.date': date,
            'timesheets.week1.day': day,
            'timesheets.week1.courseCode': course_code
        })

        if existing_entry:
            # If entry exists, check if hours worked differ
            for week in existing_entry['timesheets']:
                for entry in week['week1']:
                    if entry['date'] == date and entry['day'] == day and entry['courseCode'] == course_code:
                        if float(entry['hoursWorked']) != hours_worked:
                            if not confirm_override:
                                return jsonify({
                                    'status': 'warning',
                                    'message': f"Timesheet for {course_code} on {date} already exists with {entry['hoursWorked']} hours. Do you want to override?"
                                }), 409  # Conflict
                            else:
                                # Proceed with overriding the entry
                                users.update_one(
                                    {'username': session['username']},
                                    {'$pull': {'timesheets': {'week1.date': date, 'week1.day': day, 'week1.courseCode': course_code}}}
                                )

        # Insert or update the timesheet entry in the database
        new_entry = {
            'week1': [{
                'date': date,
                'day': day,
                'courseCode': course_code,
                'hoursWorked': hours_worked,
                'comments': comments
            }]
        }

        users.update_one(
            {'username': session['username']},
            {'$addToSet': {'timesheets': new_entry}}, upsert=True
        )

    return jsonify({'status': 'success', 'message': 'Timesheet submitted successfully'}),200 

# Faculty Route
@app.route('/faculty', methods=['GET','POST'])
@role_required('Faculty')
def faculty():
    if 'username' in session:
        return render_template('faculty.html')  # Render the timesheet if the user is logged in
    else:
        return redirect(url_for('login'))  # Redirect to login if not authenticated

#Route to fetch the timesheet data for the logged-in user
@app.route('/view_timesheet', methods=['GET'])
@role_required('Faculty')
def view_timesheet():

    # Ensure the user is logged in

    if 'username' not in session:

        return jsonify({"error": "User not logged in!"}), 403



    # Get the current logged-in user's username from session

    username = session['username']



    try:

        # Fetch the user document from the database

        user_data = users.find_one({'username': username})



        if not user_data:

            return jsonify({"error": "User not found"}), 404



        # Retrieve the timesheets field from the user's document

        timesheets = user_data.get('timesheets', [])



        return jsonify({"timesheets": timesheets}), 200

    except Exception as e:

        return jsonify({"error": str(e)}), 500

@app.route('/chatbot', methods=['POST'])
def chatbot():
    data = request.json
    question = data.get('question')
    # Process the question with your chatbot model
    response = process_question(question)  # Replace with your chatbot logic
    return jsonify({"response": response})

def process_question(question):
    if question.lower() in ("hello","hi") :
        results = "Hi there! How can I help you?"
        return results
    elif question.lower() in ("how are you","how do you do", "how's everthing going") :
        results = "I'm just a bot, but I'm doing great! How about you?"
        return results
    else:
        question = question.lower()
        """
        Chatbot endpoint to process questions and return responses.
        """
        if not question:
            return jsonify({"response": "Please provide a valid question."})

        db = connect_db()
        if db is None:
            return jsonify({"response": "Error connecting to the database."})

        print("Chatbot is analyzing your question...")
        query = parse_user_question(question)
        if query == "list_faculty":
            print("CHATBOT: Fetching faculty member names...")
            faculty_list = list_all_faculty_members(db)
            return faculty_list
            
        if isinstance(query, str) and query.startswith("Error"):
            return jsonify({"response": query})

        results = execute_query(db, query)
        print("Results==================================================================")
        print(results)
        if results:
            print("\nCHATBOT: Here are the results:")
            return format_results(results, question)
        else:
            return "CHATBOT: No data found."

# Logout Route
@app.route('/logout')
def logout():
    # session.pop('username', None)
    return redirect(url_for('login'))

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)