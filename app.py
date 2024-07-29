import streamlit as st
import sqlite3
import os
import random

# Ensure database directory exists
db_path = 'users.db'
if not os.path.exists(db_path):
    with open(db_path, 'w'):
        pass

# Database functions
def create_usertable():
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute('CREATE TABLE IF NOT EXISTS users(username TEXT, password TEXT)')
    conn.commit()
    conn.close()

def add_userdata(username, password):
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute('INSERT INTO users(username, password) VALUES (?, ?)', (username, password))
    conn.commit()
    conn.close()

def login_user(username, password):
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute('SELECT * FROM users WHERE username =? AND password = ?', (username, password))
    data = c.fetchall()
    conn.close()
    return data

# App layout and logic
def login_page():
    st.title("Login Page")
    username = st.text_input("Username")
    password = st.text_input("Password", type='password')
    if st.button("Login"):
        result = login_user(username, password)
        if result:
            st.session_state["logged_in"] = True
            st.session_state["username"] = username
        else:
            st.warning("Incorrect Username/Password")

def signup_page():
    st.title("Sign Up")
    new_user = st.text_input("Username")
    new_password = st.text_input("Password", type='password')
    if st.button("Sign Up"):
        add_userdata(new_user, new_password)
        st.success("You have successfully created an account!")
        st.info("Go to the Login page to log in.")

def show_monthly_report(tracker):
    st.markdown(
        """
        <style>
        .report-box {
            margin: 20px auto;
            border: 2px solid #cccccc;
            padding: 20px;
            border-radius: 15px;
            background-color: #2f2f2f;
            width: 50%;
            text-align: center;
            color: #ffffff;
        }
        .report-content {
            text-align: left;
            display: flex;
            flex-wrap: wrap;
            justify-content: space-between;
            margin-top: 20px;
        }
        .report-item {
            width: 48%;
            border: 1px solid #cccccc;
            padding: 10px;
            margin-bottom: 10px;
            box-sizing: border-box;
            border-radius: 10px;
            color: #ffffff;
        }
        </style>
        """, unsafe_allow_html=True)
    st.markdown(f"<div class='report-box'><h3>Monthly Report for {tracker}</h3></div>", unsafe_allow_html=True)
    report_content = "<div class='report-content'>"
    for day in range(1, 31):
        report_content += f"<div class='report-item'>Date: 2024-07-{day}, {tracker} usage: {day * 10}</div>"
    report_content += "</div>"
    st.markdown(report_content, unsafe_allow_html=True)

# Define weights for electricity, water, and petrol usage
WEIGHTS = {
    'electricity': 0.4,
    'water': 0.3,
    'petrol': 0.3
}

# Define max possible usage for normalization (adjust based on realistic values)
MAX_USAGE = {
    'electricity': 100,  # e.g., kWh
    'water': 500,        # e.g., liters
    'petrol': 50         # e.g., liters
}

# Initialize data storage for daily usage and green scores
daily_usage = {
    'electricity': [],
    'water': [],
    'petrol': [],
    'green_scores': []
}

# Function to calculate daily green score
def calculate_daily_green_score(electricity_usage, water_usage, petrol_usage):
    normalized_electricity = electricity_usage / MAX_USAGE['electricity']
    normalized_water = water_usage / MAX_USAGE['water']
    normalized_petrol = petrol_usage / MAX_USAGE['petrol']
    
    green_score = (normalized_electricity * WEIGHTS['electricity'] +
                   normalized_water * WEIGHTS['water'] +
                   normalized_petrol * WEIGHTS['petrol'])
    
    return green_score

# Function to add daily usage data and calculate daily green score
def add_daily_usage(electricity_usage, water_usage, petrol_usage):
    daily_usage['electricity'].append(electricity_usage)
    daily_usage['water'].append(water_usage)
    daily_usage['petrol'].append(petrol_usage)
    
    daily_green_score = calculate_daily_green_score(electricity_usage, water_usage, petrol_usage)
    daily_usage['green_scores'].append(daily_green_score)
    
    return daily_green_score

# Function to calculate cumulative monthly green score
def calculate_monthly_green_score():
    total_days = len(daily_usage['green_scores'])
    cumulative_score = sum(daily_usage['green_scores'])
    average_monthly_green_score = cumulative_score / total_days if total_days > 0 else 0
    return average_monthly_green_score

# Function to calculate interest rate based on green score
def calculate_interest_rate(green_score, base_rate=5.0, discount_rate=2.0):
    # Assuming green_score is between 0 and 1
    interest_rate = base_rate - (green_score * discount_rate)
    return max(interest_rate, 0)  # Ensure the interest rate is not negative

# Generate random daily usage data for 30 days
def generate_random_daily_usage():
    days_in_month = 30
    for day in range(days_in_month):
        electricity_usage = random.uniform(0, MAX_USAGE['electricity'])
        water_usage = random.uniform(0, MAX_USAGE['water'])
        petrol_usage = random.uniform(0, MAX_USAGE['petrol'])
        
        daily_green_score = add_daily_usage(electricity_usage, water_usage, petrol_usage)
        print(f"Day {day+1}: Electricity = {electricity_usage:.2f} kWh, Water = {water_usage:.2f} liters, Petrol = {petrol_usage:.2f} liters")
        print(f"Day {day+1} Green Score: {daily_green_score:.2f}")

# Example usage
generate_random_daily_usage()

# Calculate cumulative monthly green score
monthly_green_score = calculate_monthly_green_score()
print(f"Monthly Green Score: {monthly_green_score:.2f}")

# Calculate interest rate based on the monthly green score
interest_rate = calculate_interest_rate(monthly_green_score)
print(f"Interest Rate: {interest_rate:.2f}%")

def dashboard():
    st.title("Dashboard")
    st.write(f"Welcome {st.session_state['username']}")

    trackers = [
        {"name": "Electricity", "today": 50, "month": 1500},
        {"name": "Transport", "today": 20, "month": 600},
        {"name": "Water", "today": 100, "month": 3000},
        {"name": "Green Score", "today": 0, "month": 0},  # Initialize Green Score tracker
    ]

    st.markdown(
        """
        <style>
        .container {
            display: flex;
            flex-wrap: wrap;
            justify-content: space-between;
        }
        .box {
            flex: 0 0 48%;
            border-radius: 15px;
            border: 2px solid #cccccc;
            padding: 20px;
            margin: 10px 0;
            text-align: center;
            position: relative;
            cursor: pointer;
            transition: transform 0.2s ease;
        }
        .box:hover {
            transform: scale(1.05);
        }
        .circle {
            width: 100px;
            height: 100px;
            border-radius: 50%;
            border: 10px solid #4CAF50;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 20px;
            margin: 0 auto;
        }
        .circle-filled {
            width: 100px;
            height: 100px;
            border-radius: 50%;
            background: conic-gradient(#4CAF50 {percentage}%, #cccccc {percentage}%);
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 20px;
            color: #ffffff;
        }
        .details {
            margin-top: 10px;
            font-size: 18px;
        }
        .tracker-name {
            font-size: 22px;
            margin-bottom: 10px;
            font-weight: bold;
        }
        </style>
        """, unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    for i, tracker in enumerate(trackers):
        percentage_today = tracker['today']  # Assuming the 'today' value is the percentage for display
        circle_class = "circle-filled" if percentage_today > 0 else "circle"

        if i % 2 == 0:
            with col1:
                with st.form(key=f"form_{tracker['name']}"):
                    button_html = f"""
                    <div class="box">
                        <div class="tracker-name">{tracker['name']}</div>
                        <div class="{circle_class.replace("{percentage}", str(percentage_today))}">
                            {percentage_today}%
                        </div>
                        <div class="details">Units Today: {tracker['today']} | Units This Month: {tracker['month']}</div>
                        <input type="submit" value="Select">
                    </div>
                    """
                    st.markdown(button_html, unsafe_allow_html=True)
                    if st.form_submit_button(f"Select"):
                        show_monthly_report(tracker['name'])
        else:
            with col2:
                with st.form(key=f"form_{tracker['name']}"):
                    button_html = f"""
                    <div class="box">
                        <div class="tracker-name">{tracker['name']}</div>
                        <div class="{circle_class.replace("{percentage}", str(percentage_today))}">
                            {percentage_today}%
                        </div>
                        <div class="details">Units Today: {tracker['today']} | Units This Month: {tracker['month']}</div>
                        <input type="submit" value="Select">
                    </div>
                    """
                    st.markdown(button_html, unsafe_allow_html=True)
                    if st.form_submit_button(f"Select"):
                        show_monthly_report(tracker['name'])

    st.markdown(f"<div class='report-box'><h3>Monthly Green Score: {monthly_green_score:.2f}</h3></div>", unsafe_allow_html=True)
    st.markdown(f"<div class='report-box'><h3>Interest Rate: {interest_rate:.2f}%</h3></div>", unsafe_allow_html=True)

# Main app
create_usertable()

if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False

if st.session_state["logged_in"]:
    dashboard()
else:
    option = st.sidebar.selectbox("Login/Sign Up", ["Login", "Sign Up"])
    if option == "Login":
        login_page()
    else:
        signup_page()
