from flask import Flask, request, redirect, render_template, session, url_for, flash
import os
import shutil
import pymysql


app = Flask(__name__)
app.secret_key = 'Accounts'

# Configure MySQL connection parameters
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'Armath'

conn = pymysql.connect(host = app.config['MYSQL_HOST'], user = app.config['MYSQL_USER'], password= app.config['MYSQL_PASSWORD'], db = app.config['MYSQL_DB'])

cur = conn.cursor()

# Set base upload folder
BASE_UPLOAD_FOLDER = r'D:/blender fruits model file'  # Use raw string for Windows path
app.config['BASE_UPLOAD_FOLDER'] = BASE_UPLOAD_FOLDER

# Ensure the base upload folder exists
if not os.path.exists(BASE_UPLOAD_FOLDER):
    os.makedirs(BASE_UPLOAD_FOLDER)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        uname = request.form['username']
        passw = request.form['password']
        
        # Execute query to check if the user exists in the admin table
        cur.execute("SELECT * FROM admin WHERE username = %s AND password = %s", (uname, passw))
        user = cur.fetchone()

        if user:  # If the user exists
            session['username'] = uname  # Store username in session
            return redirect(url_for('upload_file'))
        else:
            
            return render_template('index.html')

        
@app.route('/file_upload')
def upload_file():
    if 'username' in session:  # Check if the user is logged in
        return render_template('file_upload.html')
    else:
        flash('You need to log in first')
        return redirect(url_for('login')) 

@app.route('/upload', methods=['POST'])
def upload_files():
    
    # Get folder name from the user
    folder_name = request.form['folder_name']
    folder_path = os.path.join(app.config['BASE_UPLOAD_FOLDER'], folder_name)
    
    # Check if the folder exists; if yes, delete its contents
    if os.path.exists(folder_path):
        shutil.rmtree(folder_path)
    
    # Create the folder (either new or replace old one)
    os.makedirs(folder_path)

    # Check if files were uploaded
    if 'files' not in request.files:
        return 'No file part'
    
    files = request.files.getlist('files')

    # Iterate through the uploaded files
    for file in files:
        if file.filename == '':
            return 'One of the files does not have a filename.'
        
        # Save the files in the new/existing (but cleared) folder
        file.save(os.path.join(folder_path, file.filename))
    
    success_message = f'Files uploaded successfully to folder "{folder_name}"!'
    return render_template('file_upload.html', success_message=success_message)

@app.route('/logout')
def logout():
    session.pop('username', None)  # Clear the session
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
