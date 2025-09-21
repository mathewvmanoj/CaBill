# TBC4

## Project Title: 
![image](https://github.com/user-attachments/assets/497604c7-d4eb-4f4f-9353-ed6fd1fd1589)

## Project Description:
In a short, we are automating the manual entries of the faculty working hours

In depth, here in this project we are creating a website where the faculty can enter their working hours in a week and we validate the faculty entries with the semester schedule. If there are any differences then we are flagging it to the finance team else we are generating a report for the entries.Adittionally,we are providing a chatbot for the finance team, allowing them to easily inquire about invoice statuses, timesheet submissions, and other relevant information, streamlining their workflow.

## Table Of Contents:
1. [Introduction](#introduction)
2. [Requirements](#requirements)
3. [LoginPage](#loginpage)
4. [FacultyPage](#facultypage)
5. [FinancePage](#financepage)
6. [Chatbot](#chatbot)

## Introduction <a name="introduction"></a>
The Invoice Automation Tool is a comprehensive software solution designed to streamline and optimize the invoicing process for businesses. This tool aims to reduce manual data entry, minimize errors, and accelerate invoice processing times through automation and intelligent data capture. By integrating with existing enterprise systems, the tool enables seamless data flow and enhances the efficiency of accounts payable operations.

## Requirements <a name="requirements"></a>
1. MongoDB
2. Python
3. Html, Css
4. Flask

## Loginpage <a name="loginpage"></a>
![Login](https://github.com/user-attachments/assets/fa082e18-07f6-4e37-a8f7-08bea2c10bd8)


## Facultypage <a name="facultypage"></a>
![Faculty](https://github.com/user-attachments/assets/b52e3b2d-8c03-4042-a0c0-f70956a0b07c)

## Financepage <a name="financepage"></a>
![Finanace](https://github.com/user-attachments/assets/09a9ca2c-f669-45a4-9114-27768613302f)

## Chatbot<a name="chatbot"></a>
![Chatbot](https://github.com/user-attachments/assets/84927e69-e439-4661-9fcb-bb9cf1abd77d)

## Steps to install this project:


### 1. Clone the Repository
```bash
git clone https://github.com/InvAutomation/CaBill.git
cd project_directory
```

### 2. Create Virtual Environment
# Create virtual environment
```bash
python3 -m venv venv

# Activate virtual environment
# On Windows
venv\Scripts\activate
# On macOS/Linux
source venv/bin/activate

```

###3. Install Required Packages
```bash
pip install -r requirements.txt
```

### 4. Update Configuration File
Create a config.py in the project root:
```bash
    # Replace with your actual MongoDB connection string
    MONGO_URI = ""
```

### 6. Run the Application
```bash 
python app.py
```

###How to Run with Docker
1. Build and Run the Application
Once you have the project files, follow these steps to build and run the backend application with Docker.

#Step 1: Build the Docker Image
Navigate to the project directory and build the Docker image:


```bash
docker-compose up --build
```

This command will:

- Build the Docker image defined in the Dockerfile.
- Create a Docker container for the backend.
- Start the container and map the ports as specified in docker-compose.yml.

#Step 2: Access the Application
Once the Docker container is running, you can access the application by visiting the following URL:
http://localhost:5000

2. If Port 5000 is Already in Use
If you encounter the error message "Ports are not available: exposing port TCP 0.0.0.0:5000 -> 0.0.0.0:0: bind: address already in use", follow these steps:

Option 1: Stop the Process Using Port 5000
Check which process is using port 5000:

```bash
lsof -i :5000
```

Kill the process using the port:

```bash
kill -9 <PID>
```

Once the port is free, run:
```bash
docker-compose up --build
```

Option 2: Change the Port Mapping in docker-compose.yml
If you don't want to stop the process using port 5000, you can change the port mapping in the docker-compose.yml file:

Open the docker-compose.yml file and look for the following line:


```bash
ports:
  - "5000:5000"
```
Change the host port (the first 5000) to another available port, such as 8080:

```bash
ports:
  - "8080:5000"
```
Save the file and run the following command to restart the container with the new port:

```bash
docker-compose up --build
```
Now, you can access the application at:

http://localhost:8080
