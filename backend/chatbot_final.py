from pymongo import MongoClient
from app.config import Config
import re

def connect_db():
    """
    Connect to MongoDB.
    """
    try:
        client = MongoClient(Config.MONGO_URI, tlsAllowInvalidCertificates=True)
        db = client["loginDB"]
        print("Connected to MongoDB successfully.")
        return db
    except Exception as e:
        print("Error connecting to MongoDB:", str(e))
        return None

def parse_user_question(question):
    """
    Analyze the user question and determine the kind of query to generate.
    Returns the corresponding MongoDB aggregation query or a predefined response.
    """
    question = question.lower()
    
    if question in ["list faculty", "list all faculty members", "show faculty"]:
        return "list_faculty"
    
    if "login" in question or "register" in question:
        return "Refer to the documentation for instructions."
    
    # Extract usernames
    match = re.search(r"(?:for|by) ([\w, ]+)", question)
    usernames = [name.strip() for name in match.group(1).split(",")] if match else None
    
    # Matching case-insensitive username 
    regex_usernames = [{"username" : {"$regex": f"^{re.escape(name)}$", "$options": "i"}} for name in usernames]

    # Specific day extraction
    day_match = re.search(r"on (\w+day)", question)
    specific_day = day_match.group(1).lower() if day_match else None
    

    # Query for total working hours
    if "total hours" in question or "working hours" in question:
        return [
            {"$match": {"$or": regex_usernames}},
            {"$unwind": "$timesheets"},
            {"$unwind": "$timesheets.week1"},
            {
                "$group": {
                    "_id": "$username",
                    "totalHours": {"$sum": {"$toDouble": "$timesheets.week1.hoursWorked"}}
                }
            },
            {"$project": {"_id": 0, "username": "$_id", "totalHours": 1}}
        ]
    
    # Query for start date and end date
    elif "start date" in question or "end date" in question:
        return [
            {"$match": {"$or": regex_usernames}},
            {"$unwind": "$timesheets"},
            {
                "$project": {
                    "_id": 0,
                    "username": 1,
                    "start_date": "$timesheets.startDate",
                    "end_date": "$timesheets.endDate"
                }
            }
        ]
    
    # Query for course codes
    elif "course code" in question or "course" in question:
        query = [
            {"$match": {"$or": regex_usernames}},
            {"$unwind": "$timesheets"},
            {"$unwind": "$timesheets.week1"},
        ]
        
        # Handle specific day query if provided
        if specific_day:
            query.append({"$match": {"timesheets.week1.day": {"$regex": f"^{specific_day}$", "$options": "i"}}})
        
        query.append({
            "$project": {
                "_id": 0,
                "username": 1,
                "courseCode": "$timesheets.week1.courseCode",
                "day": "$timesheets.week1.day"
            }
        })
        
        return query
    else:
        return "Error: Invalid question type."

def list_all_faculty_members(db):
    """
    Fetch and display all unique faculty member names from the database.
    """
    try:
        # Query to get distinct usernames
        faculty_names = db.users.distinct("username")
        if not faculty_names:
            return "No faculty members found."
        
        formatted_names = "\n".join(faculty_names)
        return f"List of Faculty Members:\n{formatted_names}"
    except Exception as e:
        print("Error fetching faculty names:", str(e))
        return "Error: Could not fetch faculty member names."
    
def execute_query(db, query):
    """
    Execute the MongoDB query and return the results.
    """
    try:
        if isinstance(query, str) and query.startswith("Error"):
            return query 
        results = db.users.aggregate(query)
        return list(results)
    except Exception as e:
        print("Error in executing query:", str(e))
        return None

def format_results(results, question):
    """
    Format query results into plain text.
    """
    if not results:
        return "No records found."

    formatted_results = []
    for result in results:
        if "total hours" in question or "working hours" in question:
            if len(results) == 1:
                formatted_results.append(f"Total Hours: {result.get('totalHours', 'N/A')}")
            else:
                formatted_results.append(f"Username: {result.get('username', 'N/A')}\nTotal Hours: {result.get('totalHours', 'N/A')}")
        elif "course code" in question or "course" in question:
            course_code = result.get("courseCode", "N/A")
            day = result.get("day", "N/A")
            if course_code != "N/A":
                formatted_results.append(f"Username: {result.get('username', 'N/A')}, Course Code: {course_code}, Day: {day}")
            else:
                formatted_results.append(f"Username: {result.get('username', 'N/A')}, Course Code: Not Found")
        elif "start date" in question or "end date" in question:
            formatted_results.append(f"Start Date: {result.get('start_date', 'N/A')}, End Date: {result.get('end_date', 'N/A')}")
        else:
            formatted_result = "\n".join([f"{key}: {value}" for key, value in result.items()])
            formatted_results.append(formatted_result)
    
    return "\n\n".join(formatted_results)

def chatbot():
    """
    Main chatbot function to interact with the user, generate a query, and fetch results.
    """
    db = connect_db()
    if db is None:
        return

    print("Chatbot is ready! Ask your questions.")

    while True:
        user_question = input("\nYOU: ").strip()

        if user_question.lower() in ["exit", "quit"]:
            print("Goodbye!")
            break

        print("Chatbot is analyzing your question...")
        query = parse_user_question(user_question)
        
        if query == "list_faculty":
            print("CHATBOT: Fetching faculty member names...")
            faculty_list = list_all_faculty_members(db)
            print(f"CHATBOT:\n{faculty_list}")
            continue

        if isinstance(query, str):
            if query.startswith("Error"):
                print(f"CHATBOT: {query}")
            else:
                print(f"CHATBOT: {query}")  
            continue

        results = execute_query(db, query)
        if results:
            print("\nCHATBOT: Here are the results:")
            print(format_results(results, user_question))
        else:
            print("CHATBOT: No data found.")

if __name__ == "__main__":
    chatbot()