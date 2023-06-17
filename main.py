from flask import Flask, render_template, request, redirect, url_for, session
from flask_mysqldb import MySQL
import MySQLdb.cursors
import MySQLdb.cursors, re, hashlib

app = Flask(__name__)

app.secret_key = 'alivaKey'

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'password'
app.config['MYSQL_DB'] = 'pythonlogin'

mysql = MySQL(app)

#login
@app.route('/pythonlogin/', methods=['GET', 'POST'])
def login():
    msg = ''
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
       
        username = request.form['username']
        password = request.form['password']

        hash = password + app.secret_key
        hash = hashlib.sha1(hash.encode())
        password = hash.hexdigest()
        
        # Using MySQL check account exists or not
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM accounts WHERE username = %s AND password = %s', (username, password,))
        # Fetch the record and return the result
        account = cursor.fetchone()
        
        # If account exists in table show in database
        if account:
            # Create session data, we can access this data in other routes
            session['loggedin'] = True
            session['id'] = account['id']
            session['username'] = account['username']
            # Redirect to home page
            return redirect(url_for('home'))
        else:
            # Account doesn't exist 
            msg = 'Incorrect username/password!'

#logout
@app.route('/pythonlogin/logout')
def logout():
   session.pop('loggedin', None)
   session.pop('id', None)
   session.pop('username', None)
   return redirect(url_for('login'))

#register
@app.route('/pythonlogin/register', methods=['GET', 'POST'])
def register():
    # Output message if something goes wrong...
    msg = ''
    # Check if "username", "password" and "email" POST requests exist (user submitted form)
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form and 'email' in request.form:
        # For easy access create variables
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']
        
        # Check if account exists using MySQL
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM accounts WHERE username = %s', (username,))
        account = cursor.fetchone()
        # If account exists show error and validation checks
        if account:
            msg = 'Account already exists!'
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            msg = 'Invalid email address!'
        elif not re.match(r'[A-Za-z0-9]+', username):
            msg = 'Username must contain only characters and numbers!'
        elif not username or not password or not email:
            msg = 'Please fill out the form!'
        else:
            # Hash the password
            hash = password + app.secret_key
            hash = hashlib.sha1(hash.encode())
            password = hash.hexdigest()
            # Account doesn't exist, and the form data is valid, insert the new account into the table
            cursor.execute('INSERT INTO accounts VALUES (NULL, %s, %s, %s)', (username, password, email,))
            mysql.connection.commit()
            msg = 'You have successfully registered!'
    elif request.method == 'POST':
        # Form is empty... (no POST data)
        msg = 'Please fill out the form!'
    # Show registration form with message (if any)
    return render_template('register.html', msg=msg)

# Grocery Store page
@app.route('/pythonlogin/home')
def home():
    # Check if the user is logged in
    if 'loggedin' in session:
        # User is loggedin show them the home page
        return render_template('home.html', username=session['username'])
    # User is not loggedin redirect to login page
    return redirect(url_for('login'))

# Connect to the MySQL database
db = mysql.connector.connect(
    host='local_host',
    user='root',
    password='password',
    database='pythonlogin'
)

# Define a route for the form page
@app.route('/')
def form():
    return render_template('home.html')
# Define a route to handle form submission
@app.route('/add_item', methods=['POST'])
def add_item():
    # Retrieve the form data
    item_name = request.form['item_name']
    item_type = request.form['item_type']
    quantity = int(request.form['quantity'])
    price = float(request.form['price'])

    # Insert the item into the database
    cursor = db.cursor()
    query = "INSERT INTO items (name, type, quantity, price) VALUES (%s, %s, %s, %s)"
    values = (item_name, item_type, quantity, price)
    cursor.execute(query, values)
    db.commit()
    cursor.close()

    return "Item added successfully!"
# Define a route to handle table display
@app.route('/table')
def display_table():
    cursor = db.cursor()
    query = "SELECT * FROM items"
    cursor.execute(query)
    rows = cursor.fetchall()
    cursor.close()

    return render_template('table.html', rows=rows)
