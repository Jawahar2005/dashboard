import streamlit as st
import sqlite3

# Database functions
def create_usertable():
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute('CREATE TABLE IF NOT EXISTS users(username TEXT, password TEXT)')
    conn.commit()
    conn.close()

def add_userdata(username, password):
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute('INSERT INTO users(username, password) VALUES (?, ?)', (username, password))
    conn.commit()
    conn.close()

def login_user(username, password):
    conn = sqlite3.connect('users.db')
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
            st.experimental_set_query_params(rerun="true")  # Use query params to trigger rerun
        else:
            st.warning("Incorrect Username/Password")

def signup_page():
    st.title("Sign Up")
    new_user = st.text_input("Username")
    new_password = st.text_input("Password", type='password')
    if st.button("Sign Up"):
        create_usertable()
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

def dashboard():
    st.title("Dashboard")
    st.write(f"Welcome {st.session_state['username']}")

    trackers = [
        {"name": "Electricity", "today": 50, "month": 1500},
        {"name": "Transport", "today": 20, "month": 600},
        {"name": "Water", "today": 100, "month": 3000},
        {"name": "Incentives", "today": 10, "month": 300},
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
        if i % 2 == 0:
            with col1:
                with st.form(key=f"form_{tracker['name']}"):
                    button_html = f"""
                    <div class="box">
                        <div class="tracker-name">{tracker['name']}</div>
                        <div class="circle">{tracker['today']}%</div>
                        <div class="details">
                            <p>Units Today: {tracker['today']} | Units This Month: {tracker['month']}</p>
                        </div>
                    """
                    st.markdown(button_html, unsafe_allow_html=True)
                    submit_button = st.form_submit_button(label="Select")
                    if submit_button:
                        st.session_state["selected_tracker"] = tracker['name']
                        st.experimental_set_query_params(rerun="true")
        else:
            with col2:
                with st.form(key=f"form_{tracker['name']}"):
                    button_html = f"""
                    <div class="box">
                        <div class="tracker-name">{tracker['name']}</div>
                        <div class="circle">{tracker['today']}%</div>
                        <div class="details">
                            <p>Units Today: {tracker['today']} | Units This Month: {tracker['month']}</p>
                        </div>
                    """
                    st.markdown(button_html, unsafe_allow_html=True)
                    submit_button = st.form_submit_button(label="Select")
                    if submit_button:
                        st.session_state["selected_tracker"] = tracker['name']
                        st.experimental_set_query_params(rerun="true")
    
    if "selected_tracker" in st.session_state:
        show_monthly_report(st.session_state["selected_tracker"])
        if st.button("Close Report"):
            del st.session_state["selected_tracker"]
            st.experimental_set_query_params(rerun="true")

def main():
    if "logged_in" not in st.session_state:
        st.session_state["logged_in"] = False

    if st.session_state["logged_in"]:
        dashboard()
    else:
        menu = ["Login", "Sign Up"]
        choice = st.selectbox("Menu", menu)
        if choice == "Login":
            login_page()
        elif choice == "Sign Up":
            signup_page()

if __name__ == "__main__":
    main()
