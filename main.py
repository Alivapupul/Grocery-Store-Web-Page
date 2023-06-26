from flask import Flask, render_template, request, redirect, url_for, session
from flask_mysqldb import MySQL
import MySQLdb.cursors
import MySQLdb.cursors, re, hashlib

app = Flask(__name__)

app.secret_key = 'alivaKey'

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'Aliva@2001'
app.config['MYSQL_DB'] = 'pythonlogin'

mysql = MySQL(app)

#loginCheck
@app.route('/pythonlogin/', methods=['GET', 'POST'])
def login():
    msg = ''
    # Check if form already submitted
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
        username = request.form['username']
        password = request.form['password']

        # Check if account exists using MySQL
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM accounts WHERE username = %s', (username,))
        account = cursor.fetchone()

        # If account exists 
        if account and hashlib.sha1(password.encode() + app.secret_key.encode()).hexdigest() == account['password']:
            session['loggedin'] = True
            session['id'] = account['id']
            session['username'] = account['username']
            return redirect(url_for('form'))
        else:
            msg = 'Incorrect username/password!'
    return render_template('index.html', msg=msg)

#logoutCheck
@app.route('/pythonlogin/logout')
def logout():
   session.pop('loggedin', None)
   session.pop('id', None)
   session.pop('username', None)

   #go back to login page
   return redirect(url_for('login')) 

#register
@app.route('/pythonlogin/register', methods=['GET', 'POST'])
def register():
    msg = ''

    # Check if form already submitted
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form and 'email' in request.form:
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']
        
        # Check if account exists
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM accounts WHERE username = %s', (username,))
        account = cursor.fetchone()

        # If account exists show error
        if account:
            msg = 'Account already exists!'
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            msg = 'Invalid email address!'
        elif not re.match(r'[A-Za-z0-9]+', username):
            msg = 'Username must contain only characters and numbers!'
        elif not username or not password or not email:
            msg = 'Please fill out the form!'
        else:
            hash = password + app.secret_key
            hash = hashlib.sha1(hash.encode())
            password = hash.hexdigest()
            
            # Add to database
            cursor.execute('INSERT INTO accounts VALUES (NULL, %s, %s, %s)', (username, password, email))
            mysql.connection.commit()
            msg = 'You have successfully registered!'
        
    elif request.method == 'POST':
        msg = 'Please fill out the form!'
    return render_template('register.html', msg=msg)

@app.route('/pythonlogin/form', methods=['GET', 'POST'])
def form():
    if 'loggedin' in session:
        return render_template('form.html', username=session['username'])
    
    return redirect(url_for('login'))

@app.route('/pythonlogin/add_item', methods=['GET', 'POST'])
def add_item():

    if 'loggedin' in session:

        # Get the form data
        item_name = request.form['item_name']
        item_type = request.form['item_type']
        quantity = int(request.form['quantity'])
        price = float(request.form['price'])

        # Add to database
        cursor = mysql.connection.cursor()
        query = "INSERT INTO items (item_name, item_type, quantity, price) VALUES (%s, %s, %s, %s)"
        values = (item_name, item_type, quantity, price)
        cursor.execute(query, values)
        mysql.connection.commit()
        cursor.close()
        msg = 'Item added successfully!'
        
        return render_template('form.html', msg=msg)
    
@app.route('/pythonlogin/table', methods=['GET', 'POST'])
def display_table():
    cursor = mysql.connection.cursor()
    query = "SELECT item_name, item_type, quantity, price FROM items"
    cursor.execute(query)
    rows = cursor.fetchall()
    cursor.close()

    return render_template('table.html', rows=rows)
