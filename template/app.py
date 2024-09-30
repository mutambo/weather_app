from flask import Flask, render_template, request, redirect, url_for, session
import pandas as pd
import os
import seaborn as sns
import matplotlib.pyplot as plt
import pyodbc
import plotly.express as px

app = Flask(__name__, template_folder='templates')
app.secret_key = "your_secret_key"

# Setup SQLite Database (or any other DB)
#app.config["SQLALCHEMY_DATABASE_URI"] = "mssql+pyodbc://DESKTOP-MBNSD8O/SQLEXPRESS/users_1?driver=ODBC+Driver+17+for+SQL+Server"
#app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False



#Database Connection config
#conn = mysql.connector.connect(
    #    host='localhost',
    #    user='',
    #    password='',
     #   database=' '
   # )
   # return conn
def get_db_connection():
    conn = pyodbc.connect(
        "Driver={ODBC Driver 17 for SQL Server};"
        "Server=DESKTOP-MBNSD8O\\SQLEXPRESS;"  # Replace with your server name
        "Database=users_1;" # Replace with your database name
        "Trusted_Connection=yes;"  # Or add 'UID=user;PWD=password;' for SQL authentication
        )
    return conn    

# Define the user model
#class User(db.Model):
  #  id = db.Column(db.Integer, primary_key=True)
   # username = db.Column(db.String(150), unique=True, nullable=False)
   # password = db.Column(db.String(150), nullable=False)"""

#Route for the root URL
@app.route("/")
def home():
    return render_template("home.html")    


# Route for login page
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE username=? AND password=?", (username, password))
        user = cursor.fetchone()
        conn.close()

        if user:
            session["username"] = user[1]  # Assuming the second column is the username
            return redirect(url_for("dashboard"))
        else:
            return "Login failed. Check your username and password."
    return render_template("login.html")


# Route for signup page
@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        conn = get_db_connection()
        cursor = conn.cursor()

        # Check if user already exists
        cursor.execute("SELECT * FROM users WHERE username=?", (username,))
        existing_user = cursor.fetchone()

        if existing_user:
            conn.close()
            return "User already exists!"

        # Insert new user into the database
        cursor.execute("INSERT INTO dbo.users (username, password) VALUES (?, ?)", (username, password))
        if request.method == "POST":
         username = request.form["username"]
        password = request.form["password"]
        conn = get_db_connection()
        cursor = conn.cursor()

        # Check if user already exists
        cursor.execute("SELECT * FROM users WHERE username=?", (username,))
        existing_user = cursor.fetchone()

        if existing_user:
            conn.close()
            return "User already exists!"

        # Insert new user into the database
        cursor.execute("INSERT INTO dbo.users (username, password) VALUES (?, ?)", (username, password))
        conn.commit()
        conn.close()
        return redirect(url_for("login"))
    return render_template("signup.html")


# Route for the dashboard (Data Display)
@app.route("/dashboard")
def dashboard():
    if "username" in session:
        # Load and process the weather data
        df = pd.read_csv("seattle-weather.csv")
        df["date"] = pd.to_datetime(df["date"], format="%Y-%m-%d")
        
        
        # Generate the Seaborn pairplot
        #sns.pairplot(df[['precipitation', 'temp_max', 'temp_min', 'wind']])
        #plt.title('Seaborn Pair Plot of Weather Data')

        # Save the plot as an image in the static folder
        #img_path = os.path.join("static", "images", "weather_plot.png")
        #plt.savefig(img_path)
        #plt.close()
        fig1 = px.scatter(df, x='precipitation', y='temp_max', title=' Weather Data')
        fig2 = px.scatter(df, x='precipitation', y='wind', title=' Weather Data')

# Save the plot as an HTML file to be rendered
        fig1.write_html('static/plots/weather_plot.html')
        fig2.write_html('static/plots/wind_vs_precip.html')

        
        
        avg_precip = df["precipitation"].mean()
        avg_max_temp = df["temp_max"].mean()
        avg_min_temp = df["temp_min"].mean()
        avg_wind = df["wind"].mean()

        # Pass the average data to the HTML
        return render_template(
            "dashboard.html",
            avg_precip=avg_precip,
            avg_max_temp=avg_max_temp,
            avg_min_temp=avg_min_temp,
            avg_wind=avg_wind,
        )
    else:
        return redirect(url_for("login"))



# Route for logging out
@app.route("/logout")
def logout():
    session.pop("username", None)
    return redirect(url_for("login"))


if __name__ == "__main__":
    #db.create_all()  # Creates database tables (only need to run once)
    app.run(debug=True)

