import pandas as pd
import random
from faker import Faker

# Initialize Faker for generating random data
fake = Faker()

# Function to generate random values based on type
def generate_random_value(value_type):
    if value_type == "int":
        return random.randint(1, 100)
    elif value_type == "float":
        return round(random.uniform(1.0, 100.0), 2)
    elif value_type == "name":
        return fake.name()
    elif value_type == "email":
        return fake.email()
    elif value_type == "date":
        return fake.date()
    elif value_type == "city":
        return fake.city()
    elif value_type == "text":
        return fake.sentence()
    else:
        return None

# Function to create the random Excel file
def generate_excel(file_name, num_rows, columns):
    data = {col: [generate_random_value(value_type) for _ in range(num_rows)] for col, value_type in columns.items()}
    df = pd.DataFrame(data)
    df.to_excel(file_name, index=False)
    print(f"Excel file '{file_name}' created successfully!")

# Example usage
if __name__ == "__main__":
    num_rows = 50  # Set number of rows globally
    columns = {
        "ID": "int",
        "Name": "name",
        "Email": "email",
        "Age": "int",
        "Salary": "float",
        "Joining Date": "date",
        "City": "city",
        "Remarks": "text"
    }
    
    generate_excel("random_data.xlsx", num_rows, columns)
