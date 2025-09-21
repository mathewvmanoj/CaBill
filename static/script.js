document.addEventListener("DOMContentLoaded", function () {
    const registerForm = document.getElementById("registerForm");
    const loginForm = document.getElementById("loginForm");
    const toggles = document.querySelectorAll(".toggle-switch");
    const urlParams = new URLSearchParams(window.location.search);
    const fromDate = urlParams.get('from_date');
    const toDate = urlParams.get('to_date');
    // Global Variables
    let currentPage = 1;
    let totalPages = 1;
    let recordsPerPage = 10;
    let timesheets = []; // Global variable to store fetched timesheets
    let isTableVisible = false; // Track visibility of the table

    // Elements
    const viewTimesheetBtn = document.getElementById('view-timesheet-btn');
    const timesheetContainer = document.getElementById('timesheet-container');
    const tableContainer = document.getElementById('timesheet-table-container');
    // const prevButton = document.getElementById('prev-button');
    // const nextButton = document.getElementById('next-button');

    // Handle the "View Timesheet" button click
    if (viewTimesheetBtn) {
        viewTimesheetBtn.addEventListener('click', function () {
            if (isTableVisible) {
                // Hide the table if it is currently visible
                timesheetContainer.setAttribute('hidden', true);
                isTableVisible = false;
            } else {
                // Reset page to 1 and fetch data
                currentPage = 1; // Reset to first page
                fetch('/view_timesheet')
                    .then(response => response.json())
                    .then(data => {
                        if (data.error) {
                            alert(data.error);
                        } else {
                            // Sort the timesheets by date (latest to oldest)
                            timesheets = data.timesheets.sort((a, b) => {
                                const latestA = new Date(a.week1[a.week1.length - 1].date);
                                const latestB = new Date(b.week1[b.week1.length - 1].date);
                                return latestB - latestA; // Descending order
                            });
                            totalPages = Math.ceil(timesheets.length / recordsPerPage); // Calculate total pages
                            displayTimesheets(); // Display first page
                            isTableVisible = true; // Mark table as visible
                        }
                    })
                    .catch(error => {
                        console.error('Error fetching timesheet data:', error);
                        alert('There was an error fetching the timesheet data.');
                    });
            }
        });
    }

    // Function to Display Timesheets
    function displayTimesheets() {
        if (timesheetContainer) {
            timesheetContainer.removeAttribute('hidden'); // Show the container

            // Clear previous content
            tableContainer.innerHTML = '';

            if (timesheets.length === 0) {
                tableContainer.innerHTML = '<p>No timesheets available.</p>';
                return;
            }

            // Calculate indices for current page
            const startIndex = (currentPage - 1) * recordsPerPage;
            const endIndex = Math.min(startIndex + recordsPerPage, timesheets.length);
            const currentRecords = timesheets.slice(startIndex, endIndex);

            // Create table
            const table = document.createElement('table');
            table.classList.add('timesheet-table');
            table.innerHTML = `
                <thead>
                    <tr>
                        <th>Date</th>
                        <th>Day</th>
                        <th>Course Code</th>
                        <th>Hours Worked</th>
                        <th>Comments</th>
                    </tr>
                </thead>
                <tbody>
                    ${currentRecords.map(timesheet => {
                        return timesheet.week1.map(entry => `
                            <tr>
                                <td>${entry.date}</td>
                                <td>${entry.day}</td>
                                <td>${entry.courseCode}</td>
                                <td>${entry.hoursWorked}</td>
                                <td>${entry.comments}</td>
                            </tr>
                        `).join('');
                    }).join('')}
                </tbody>
            `;
            tableContainer.appendChild(table);

            // Enable/Disable Pagination Buttons
            prevButton.disabled = currentPage === 1;
            nextButton.disabled = currentPage === totalPages;

            adjustBodyHeight(); // Adjust body height
        }
    }

    // Function to Adjust Body Height Dynamically
    function adjustBodyHeight() {
        const container = document.querySelector('.container');
        if (container) {
            const contentHeight = container.offsetHeight;
            document.body.style.minHeight = contentHeight + 'px';
            document.documentElement.style.minHeight = contentHeight + 'px';
        }
    }
    
    // Get the download link element
    const downloadLink = document.getElementById('download-report-btn');

    // Get the base download report URL from a data attribute
    const baseDownloadUrl = downloadLink.getAttribute('data-download-url');

    // If both from_date and to_date are present, update the download link with query parameters
    if (fromDate && toDate) {
        downloadLink.href = `${baseDownloadUrl}?from_date=${fromDate}&to_date=${toDate}`;
    } else {
        // If no filter is applied, set the download link without date parameters
        downloadLink.href = baseDownloadUrl;
    }

    document.getElementById("download-report-btn").addEventListener("click", function (event) {
        event.preventDefault(); // Prevent the form submission
        const from_date = document.getElementById("from_date").value;   
        const to_date = document.getElementById("to_date").value;

        const url = `/download_finance_report?from_date=${from_date}&to_date=${to_date}`;
        window.location.href = url; // Trigger download
    });

    // Functionality of toggle switch
    toggles.forEach(toggle => {
        toggle.addEventListener("change", function () {
            const row = this.closest("tr");
            const discrepancyCell = row.querySelector(".discrepancy-cell");
            const facultyNameElement = row.querySelector(".faculty-name");
            const facultyName = facultyNameElement.querySelector("a")
                ? facultyNameElement.querySelector("a").textContent.trim() // New structure
                : facultyNameElement.textContent.trim(); // Old structure

            const status = this.checked ? "✓" : "✗";
            discrepancyCell.textContent = status;
    
            // Make an API call to save the change
            fetch('/update_status', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    faculty_name: facultyName,
                    status: status
                })
            })
            .then(response => response.json())
            .then(data => {
                if (data.status === 'success') {
                    alert("Status updated successfully.");
                } else {
                    alert(data.message);
                }
            })
            .catch(error => {
                console.error("Error:", error);
                alert("An error occurred while saving the data.");
            });
        });
    });
    

    // RegisterForm Functionality
    if (registerForm) {
        registerForm.addEventListener("submit", async function (e) {
            e.preventDefault();
            const username = document.getElementById("username").value;
            const password = document.getElementById("password").value;

            const response = await fetch("/register", {
                method: "POST",
                headers: {
                    "Content-Type": "application/x-www-form-urlencoded",
                },
                body: new URLSearchParams({
                    username: username,
                    password: password,
                }),
            });

            const result = await response.json();
            alert(result.message || result.error);
            if (response.ok) {
                window.location.href = "/login";  // Redirect to login on successful registration
            }
        });
    }

    // LoginForm Functionality
    if (loginForm) {
        loginForm.addEventListener("submit", async function (e) {
            e.preventDefault(); // Prevent the default form submission
    
            const username = document.getElementById("username").value;
            const password = document.getElementById("password").value;
            const role = document.getElementById("roles").value;
    
            // Ensure a role is selected
            if (role === "Select") {
                alert("Please select a role before logging in!");
                return;
            }
    
            // Sending a POST request to the login endpoint
            const response = await fetch("/login", {
                method: "POST",
                headers: {
                    "Content-Type": "application/x-www-form-urlencoded",
                },
                body: new URLSearchParams({
                    username: username,
                    password: password,
                    roles: role,
                }),
            });
    
            const result = await response.json();
    
            // Handle different server responses
            if (response.ok) {
                window.location.href = result.redirect_url || "/"; // Redirect on successful login
            } else {
                // Display error message in a popup
                alert(result.error || "An unknown error occurred during login!");
            }
        });
    }
    
    
});


// Array of course codes
const courseCodes = [
    "ACCT1010", "AISC1000", "AISC1001", "AISC1002", "AISC1003", "AISC1004", "AISC1005", "AISC1006","AISC2000", "AISC2001", "AISC2002", "AISC2003", "AISC2004", "AISC2005", "AISC2006", "AISC2007",
                "AISC2008", "AISC2009", "AISC2010", "AISC2011", "AISC2012", "AISC2013", "AISC2016", "AISC2017","AISC3002", "BUSI1002", "BUSI1016", "BUSI1019", "BUSI1020", "BUSI1021", "BUSI1022", "BUSI1023",
                "BUSI1025", "BUSI1033", "BUSI1034", "BUSI1035", "BUSI1036", "BUSI1037", "BUSI1038", "BUSI1039","BUSI2001", "BUSI2002", "BUSI2004", "BUSI2009", "BUSI2016", "BUSI2017", "BUSI2019", "BUSI2023","BUSI2025",
                "BUSI3005", "BUSI3007", "BUSI3011", "BUSI3024", "BUSI3034", "CLOD1000", "CLOD1001","CLOD1002", "CLOD1003", "CLOD1004", "CLOD1005", "CLOD2000", "CLOD2001", "CLOD2002", "CLOD2003", "CLOD2004", "CLOD2005",
                "CLOD2006", "CLOD2007", "CLOD2008", "COMM1066", "COMM1067", "COMM1076", "COMM1083", "COMP1021", "COMP1022", "COMP1025", "COMP1026", "COMP1027", "COMP1028", "COMP1029","COMP1030", "COMP1031", "COMP1032",
                "COMP2005", "COMP2006", "COMP2007", "COMP2008", "COMP2009", "COMP2010", "COMP2011", "COMP2012", "COMP2013", "CSDD1000", "CSDD1001", "CSDD1002", "CSDD1003","CSDD1004", "CSDD1005", "CSDD1006", "CSDD1007",
                "CSDD1008", "CSDD2000", "CSDD2001", "CSDD2002","CSDD2003", "CSDD2004", "CYSE1000", "CYSE1001", "CYSE1002", "CYSE1003", "CYSE1004", "CYSE1005","CYSE1006", "CYSE1007", "CYSE1008", "CYSE1009", "CYSE2000",
                "CYSE2001", "CYSE2002", "CYSE2003", "CYSE2004", "ECON2000", "ENTR2009", "GBMG1000", "GBMG1001", "GBMG1002", "GBMG1003", "GBMG1004","GBMG1005", "GBMG2000", "GBMG2001", "GBMG2002", "GBMG2003", "GBMG2004",
                "GBMG2005", "GBMG2007", "GNED1009", "GNED1044", "GNED1052", "GNED1100", "GPMG2000", "GPMG2001", "GPMG2002", "GPMG2003","GPMG2004", "GPMG2006", "GPMG2009", "GPMG2010", "GPMG2011", "HOSP1041", "HOSP1042", "HOSP1043",
                "HOSP1044", "HOSP1045", "HRPG3002", "HRPG3004", "LAWS2018", "LOGS1004", "LOGS1005", "LOGS1009","LOGS1010", "LOGS1011", "LOGS2000", "LOGS2001", "LOGS2002", "LOGS2003", "LOGS2004", "LOGS2005",
                "LOGS2006", "LOGS2013", "LOGS2014", "LOGS3000", "MATH1033", "MATH1044", "MATH1045", "MATH1047","MATH2014", "MEDI1022", "MRKT1005", "MRKT1011", "MRKT2006", "MRKT2007", "MRKT2008", "PROF1018",
                "PROF1020", "PROF1021", "PROF2035", "PROF2044", "PROF2045", "PROF2047", "QEMG1000", "QEMG1001","QEMG1002", "QEMG1003", "QEMG1004", "QEMG1005", "QEMG1006", "QEMG2000", "QEMG2001", "QEMG2002",
                "QEMG2003", "QEMG2004", "QEMG2005", "QEMG2006", "QEMG2007", "QEMG2008", "QEMG2009", "QEMG2010","QEMG2011", "QEMG2012", "QEMG2013", "QEMG2015", "QEMG2016", "QEMG3002", "SALE1006", "SALE1010",
                "SALE2015", "SALE2016", "SALE2017", "SUST1000", "SUST1002", "SUST2001", "WINP1000", "WINP1001","WINP1002", "WINP1003", "WINP1004", "WINP1005", "WINP1006", "WINP1007", "WINP1008", "WINP1009",
                "WINP1010", "WINP2000", "WINP2001", "WINP2002", "WINP2003", "WINP2004", "WKPL1040", "WKPL2083","AIP", "Academic Orientaion", "Co-op Orientation", "Co-op Course", "Moodle Orientation", 
                "PC Meeting", "PD Session", "Mock Interview", "Tutoring", "Workshop"
                
    ];
    
// Populate course code dropdown
const datalist = document.getElementById('course-codes');
courseCodes.forEach(code => {
    const option = document.createElement('option');
    option.value = code;
    datalist.appendChild(option);
});

// Helper function to format dates to 'YYYY-MM-DD'
function formatDate(date) {
    const year = date.getFullYear();
    const month = String(date.getMonth() + 1).padStart(2, '0'); // Months are 0-based
    const day = String(date.getDate()).padStart(2, '0');
    return `${year}-${month}-${day}`;
}

// Set End Date Function and update min/max for date inputs
function setEndDate() {
    const startDateInput = document.getElementById('start-date');
    if (startDateInput.value) {
        const startDate = new Date(startDateInput.value);
        const endDate = new Date(startDate);
        endDate.setDate(startDate.getDate() + 13); // Set end date to 14 days after start date

        // Format the start and end dates to 'YYYY-MM-DD'
        const formattedStartDate = formatDate(startDate);
        const formattedEndDate = formatDate(endDate);

        // Set the value of the end-date input
        document.getElementById('end-date').value = formattedEndDate;

        // Set min and max values for all date inputs within the timesheet
        document.querySelectorAll('.date-input').forEach(input => {
            input.setAttribute('min', formattedStartDate); // Min date is the start date
            input.setAttribute('max', formattedEndDate); // Max date is the end date
            input.value = ''; // Clear the previous date input value if any
        });
    } else {
        alert("Please select a start date.");
    }
}

// Add new entry row function
function addEntry(week) {
    const table = document.getElementById(week + '-table').getElementsByTagName('tbody')[0];
    const rowClass = week + '-row';
    const newRow = document.querySelector('.' + rowClass).cloneNode(true);

    // Clear the values of cloned row inputs
    newRow.querySelectorAll('input').forEach(input => {
        if (input.type === "date") {
            input.value = ''; // Ensure that the date field is cleared
            input.setAttribute('min', document.getElementById('start-date').value); // Set min date to start date
            input.setAttribute('max', document.getElementById('end-date').value); // Set max date to end date
        } else {
            input.value = ''; // Clear other input fields as well
        }
    });

    // Reset select fields
    newRow.querySelectorAll('select').forEach(select => select.value = ''); // Reset select values

    // Create and add a "Delete" button (for new rows only)
    const deleteButton = document.createElement('button');
    deleteButton.textContent = 'Delete';
    deleteButton.type = 'button';
    deleteButton.classList.add('delete-row');
    deleteButton.onclick = function () {
        newRow.remove(); // Remove the row on click
    };

    // Append the "Delete" button to the row
    const deleteCell = document.createElement('td');
    deleteCell.appendChild(deleteButton);
    newRow.appendChild(deleteCell);

    // Append the new row to the table
    table.appendChild(newRow);

    // Add day auto-fill functionality for new rows
    newRow.querySelectorAll('.date-input').forEach(input => {
        input.addEventListener('change', function () {
            const dateValue = this.value;
            if (dateValue) {
                const [year, month, day] = dateValue.split('-');
                const date = new Date(year, month - 1, day);
                const dayOptions = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday'];
                const dayOfWeek = date.getDay();
                this.closest('tr').querySelector('.day-select').value = dayOptions[dayOfWeek];
            }
        });
    });
}

// Auto-fill day based on date input for the initial row
document.querySelectorAll('.date-input').forEach(input => {
    input.addEventListener('change', function () {
        const dateValue = this.value;
        if (dateValue) {
            const [year, month, day] = dateValue.split('-');
            const date = new Date(year, month - 1, day);
            const dayOptions = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday'];
            const dayOfWeek = date.getDay();
            this.closest('tr').querySelector('.day-select').value = dayOptions[dayOfWeek];
        }
    });
});

// Form submission handling
// document.getElementById('timesheet-form').addEventListener('submit', async function (e) {
//     e.preventDefault(); // Prevent form submission

//     // Extract form data
//     const startDate = document.getElementById('start-date').value;
//     const endDate = document.getElementById('end-date').value;

//     const week1Rows = document.querySelectorAll('#week1-table tbody tr');
//     const week1Data = Array.from(week1Rows).map(row => {
//         return {
//             date: row.querySelector('input[type="date"]').value,
//             day: row.querySelector('.day-select').value,
//             courseCode: row.querySelector('input[list="course-codes"]').value,
//             hoursWorked: row.querySelector('input[type="number"]').value,
//             comments: row.querySelector('input[type="text"]').value
//         };
//     });

//     // Create the final object to send to Flask
//     const timesheetData = {
//         startDate: startDate,
//         endDate: endDate,
//         week1: week1Data
//     };

//     console.log(timesheetData);

//     try {
//         // Send data to the Flask backend
//         const response = await fetch('/submit_timesheet', {
//             method: 'POST',
//             headers: {
//                 'Content-Type': 'application/json'
//             },
//             body: JSON.stringify(timesheetData)
//         });

//         if (response.ok) {
//             const result = await response.json();
//             alert('Timesheet submitted successfully');
//         } else {
//             alert('Failed to submit timesheet');
//         }
//     } catch (error) {
//         console.error('Error:', error);
//         alert('Error submitting timesheet');
//     }
// });

document.getElementById('timesheet-form').addEventListener('submit', function(event) {
    event.preventDefault();  // Prevent default form submission

    // Get form data
    const startDate = document.getElementById('start-date').value;
    const endDate = document.getElementById('end-date').value;

    const dateInputs = document.querySelectorAll('input[name="date1[]"]');
    const daySelects = document.querySelectorAll('select[name="day1[]"]');
    const courseCodeInputs = document.querySelectorAll('input[name="course-code1[]"]');
    const hoursWorkedInputs = document.querySelectorAll('input[name="hours-worked1[]"]');
    const commentsInputs = document.querySelectorAll('input[name="comments1[]"]');

    // Prepare the data object
    let timesheetData = [];

    for (let i = 0; i < dateInputs.length; i++) {
        let date = dateInputs[i].value;
        let day = daySelects[i].value;
        let courseCode = courseCodeInputs[i].value;
        let hoursWorked = hoursWorkedInputs[i].value;
        let comments = commentsInputs[i].value;

        // Push each entry to the timesheetData array
        if (date && day && courseCode && hoursWorked) {
            timesheetData.push({
                date: date,
                day: day,
                course_code: courseCode,
                hours_worked: hoursWorked,
                comments: comments
            });
        }
    }

    // Send data to Flask backend using Fetch API
    fetch('/submit_timesheet', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ start_date: startDate, end_date: endDate, timesheet_data: timesheetData }),
    })
    .then(response => response.json())
    .then(data => {
        if (data.status === 'success') {
            alert('Timesheet submitted successfully!');
            // Optionally, redirect to another page or show success message
        } else if (data.status === 'warning') {
            // Prompt user for override confirmation
            const confirmOverride = confirm(data.message);
            if (confirmOverride) {
                // Proceed with submitting the data to override
                submitTimesheetData(timesheetData);
            }
        } else {
            alert(data.message);
        }
    })
    .catch(error => {
        console.error('Error:', error);
        alert('Error submitting timesheet.');
    });
});

function submitTimesheetData(timesheetData) {
    fetch('/submit_timesheet', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ timesheet_data: timesheetData, confirm_override: true }),
    })
    .then(response => response.json())
    .then(data => {
        if (data.status === 'success') {
            alert('Timesheet submitted successfully!');
        } else {
            alert('Error submitting timesheet.');
        }
    });
}
     
            

// Chat Bot Content
function toggleChatbot() {
    const chatbotWindow = document.getElementById('chatbot-window');
    //chatbotWindow.style.display = chatbotWindow.style.display === 'block' ? 'none' : 'block';
    chatbotWindow.style.display = chatbotWindow.style.display === 'none' || chatbotWindow.style.display === '' ? 'flex' : 'none';
}


async function sendMessage() {
    const userInput = document.getElementById('user-input');
    const userMessage = userInput.value.trim();
    const chatMessages = document.getElementById('chat-messages'); // Chat messages container

    if (userMessage) {
        // Display user's message in the chat
        const userMessageDiv = document.createElement("div");
        userMessageDiv.className = "user-message";
        userMessageDiv.textContent = userMessage;
        chatMessages.appendChild(userMessageDiv);

        // Scroll to the bottom of chat
        chatMessages.scrollTop = chatMessages.scrollHeight;

        try {
            // Make a request to the chatbot backend API
            const response = await fetch("http://127.0.0.1:5000/chatbot", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({ question: userMessage })
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const data = await response.json();

            // Display bot's response
            const botMessageDiv = document.createElement("div");
            botMessageDiv.className = "bot-message";
            botMessageDiv.textContent = data.response || "Sorry, I couldn't process that.";
            chatMessages.appendChild(botMessageDiv);
        } catch (error) {
            // Display error message
            const errorMessageDiv = document.createElement("div");
            errorMessageDiv.className = "bot-message error";
            errorMessageDiv.textContent = "Error: Unable to connect to the chatbot.";
            chatMessages.appendChild(errorMessageDiv);
            console.error("Error fetching chatbot response:", error);
        }

        // Scroll to the bottom of chat
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }

    // Clear user input field
    userInput.value = '';
}


function addMessage(sender, text) {
    const chatMessages = document.getElementById('chat-messages');
    const messageDiv = document.createElement('div');
    messageDiv.classList.add(sender === 'User' ? 'user-message' : 'bot-message');
    messageDiv.textContent = text;
    chatMessages.appendChild(messageDiv);
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

