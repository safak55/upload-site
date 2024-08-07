import requests
import configparser
import gunicorn
from flask import Flask, request, redirect, url_for, render_template_string, Response
import os

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['ALLOWED_EXTENSIONS'] = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'exe', 'rar', 'zip'}

if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

def secure_filename(filename):
    """ Safely remove or replace special characters from the filename. """
    return filename.replace(" ", "_").replace("..", "_")

@app.route('/')
def index():
    return render_template_string('''
        <!doctype html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Upload File</title>
            <style>
                body {
                    display: flex;
                    justify-content: center;
                    align-items: center;
                    height: 100vh;
                    margin: 0;
                    background: url('https://wallpaper.forfun.com/fetch/81/819e8ff5a34a1d8170d7de4bb429dd0b.jpeg') no-repeat center center fixed;
                    background-size: cover;
                    font-family: Arial, sans-serif;
                    position: relative;
                    overflow: hidden;
                }
                .container {
                    text-align: center;
                    padding: 40px; /* Increased padding */
                    background-color: rgba(0, 0, 0, 0.8); /* Slightly transparent black background */
                    border-radius: 12px;
                    box-shadow: 0 0 15px rgba(0, 0, 0, 0.5);
                    color: #ffffff;
                    position: relative;
                    z-index: 1;
                    width: 80%; /* Increased width */
                    max-width: 600px; /* Maximum width to prevent overflow */
                }
                h1 {
                    margin-bottom: 30px; /* Increased margin */
                    color: #ffffff;
                    font-size: 2.5em; /* Larger font size */
                }
                input[type="file"] {
                    margin-bottom: 20px; /* Increased margin */
                    font-size: 18px; /* Larger font size */
                    color: #ffffff;
                    background: #333;
                    border: none;
                    padding: 12px; /* Increased padding */
                    border-radius: 5px;
                }
                input[type="submit"] {
                    padding: 15px 35px; /* Increased padding */
                    font-size: 20px; /* Larger font size */
                    color: #ffffff;
                    background-color: #007bff;
                    border: none;
                    border-radius: 5px;
                    cursor: pointer;
                }
                input[type="submit"]:hover {
                    background-color: #0056b3;
                }
                /* Snow animation */
                .snowflakes {
                    position: absolute;
                    top: 0;
                    left: 0;
                    width: 100%;
                    height: 100%;
                    pointer-events: none;
                    z-index: 0;
                    overflow: hidden;
                    background: transparent;
                }
                .snowflake {
                    position: absolute;
                    width: 12px; /* Slightly larger snowflakes */
                    height: 12px; /* Slightly larger snowflakes */
                    background-color: #ffffff;
                    border-radius: 50%;
                    opacity: 0.8;
                    animation: snowflake-fall linear infinite;
                }
                @keyframes snowflake-fall {
                    to {
                        transform: translateY(100vh);
                    }
                }
                /* Generating snowflakes */
                .snowflake:nth-child(1) { left: 10%; animation-duration: 8s; animation-delay: 0s; }
                .snowflake:nth-child(2) { left: 20%; animation-duration: 9s; animation-delay: 1s; }
                .snowflake:nth-child(3) { left: 30%; animation-duration: 8s; animation-delay: 2s; }
                .snowflake:nth-child(4) { left: 40%; animation-duration: 10s; animation-delay: 3s; }
                .snowflake:nth-child(5) { left: 50%; animation-duration: 12s; animation-delay: 4s; }
                .snowflake:nth-child(6) { left: 60%; animation-duration: 9s; animation-delay: 5s; }
                .snowflake:nth-child(7) { left: 70%; animation-duration: 11s; animation-delay: 6s; }
                .snowflake:nth-child(8) { left: 80%; animation-duration: 8s; animation-delay: 7s; }
                .snowflake:nth-child(9) { left: 90%; animation-duration: 10s; animation-delay: 8s; }
                .snowflake:nth-child(10) { left: 5%; animation-duration: 13s; animation-delay: 9s; }
                .snowflake:nth-child(11) { left: 15%; animation-duration: 9s; animation-delay: 10s; }
                .snowflake:nth-child(12) { left: 25%; animation-duration: 12s; animation-delay: 11s; }
                .snowflake:nth-child(13) { left: 35%; animation-duration: 11s; animation-delay: 12s; }
                .snowflake:nth-child(14) { left: 45%; animation-duration: 10s; animation-delay: 13s; }
                .snowflake:nth-child(15) { left: 55%; animation-duration: 12s; animation-delay: 14s; }
                .snowflake:nth-child(16) { left: 65%; animation-duration: 9s; animation-delay: 15s; }
                .snowflake:nth-child(17) { left: 75%; animation-duration: 13s; animation-delay: 16s; }
                .snowflake:nth-child(18) { left: 85%; animation-duration: 11s; animation-delay: 17s; }
                .snowflake:nth-child(19) { left: 95%; animation-duration: 12s; animation-delay: 18s; }
                .snowflake:nth-child(20) { left: 50%; animation-duration: 9s; animation-delay: 19s; }
            </style>
        </head>
        <body>
            <div class="snowflakes">
                <!-- The snowflakes will be dynamically generated by JavaScript -->
            </div>
            <div class="container">
                <h1>fastupload.fun</h1>
                <form action="/upload" method="post" enctype="multipart/form-data">
                    <input type="file" name="file">
                    <br>
                    <input type="submit" value="Upload">
                </form>
            </div>
            <script>
                function createSnowflakes() {
                    const snowflakesContainer = document.querySelector('.snowflakes');
                    for (let i = 0; i < 100; i++) {
                        const snowflake = document.createElement('div');
                        snowflake.classList.add('snowflake');
                        snowflake.style.left = `${Math.random() * 100}vw`;
                        snowflake.style.animationDuration = `${Math.random() * 10 + 6}s`; // Slightly faster
                        snowflake.style.animationDelay = `${Math.random() * 10}s`;
                        snowflake.style.opacity = `${Math.random() * 0.5 + 0.5}`;
                        snowflake.style.width = `${Math.random() * 15 + 5}px`;
                        snowflake.style.height = `${Math.random() * 15 + 5}px`;
                        snowflakesContainer.appendChild(snowflake);
                    }
                }
                createSnowflakes();
            </script>
        </body>
        </html>
    ''')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return redirect(request.url)
    file = request.files['file']
    if file.filename == '':
        return redirect(request.url)
    if file and allowed_file(file.filename):
        original_filename = secure_filename(file.filename)
        base, ext = os.path.splitext(original_filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], original_filename)

        # Ensure unique filename by adding a number suffix if the file already exists
        counter = 1
        new_filename = original_filename  # Initialize new_filename with the original filename
        while os.path.exists(file_path):
            new_filename = f"{base}_{counter}{ext}"
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], new_filename)
            counter += 1

        file.save(file_path)
        # Redirect using the filename that was actually saved (with suffix if added)
        return redirect(url_for('file_uploaded', filename=new_filename))
    else:
        return 'Invalid file type', 400

@app.route('/uploaded/<filename>')
def file_uploaded(filename):
    file_download_url = url_for('serve_file', filename=filename, _external=True)
    file_uploaded_url = url_for('file_uploaded', filename=filename, _external=True)
    index_url = url_for('index', _external=True)
    return render_template_string('''
        <!doctype html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>File Uploaded</title>
            <style>
                body {
                    display: flex;
                    justify-content: center;
                    align-items: center;
                    height: 100vh;
                    margin: 0;
                    background: url('https://wallpaper.forfun.com/fetch/81/819e8ff5a34a1d8170d7de4bb429dd0b.jpeg') no-repeat center center fixed;
                    background-size: cover;
                    font-family: Arial, sans-serif;
                    position: relative;
                    overflow: hidden;
                }
                .container {
                    text-align: center;
                    padding: 40px; /* Increased padding */
                    background-color: rgba(0, 0, 0, 0.8); /* Slightly transparent black background */
                    border-radius: 12px;
                    box-shadow: 0 0 15px rgba(0, 0, 0, 0.5);
                    color: #ffffff;
                    position: relative;
                    z-index: 1;
                    width: 80%; /* Increased width */
                    max-width: 600px; /* Maximum width to prevent overflow */
                }
                h1 {
                    margin-bottom: 30px; /* Increased margin */
                    color: #ffffff;
                    font-size: 2.5em; /* Larger font size */
                }
                p {
                    font-size: 1.5em; /* Larger font size */
                }
                input[type="text"] {
                    width: 100%;
                    padding: 15px; /* Increased padding */
                    margin-bottom: 20px;
                    border: none;
                    border-radius: 5px;
                    font-size: 20px; /* Larger font size */
                    color: #ffffff;
                    background-color: #333;
                }
                button {
                    padding: 15px 35px; /* Increased padding */
                    font-size: 20px; /* Larger font size */
                    color: #ffffff;
                    background-color: #007bff;
                    border: none;
                    border-radius: 5px;
                    cursor: pointer;
                }
                button:hover {
                    background-color: #0056b3;
                }
                .back-link {
                    margin-top: 30px;
                    display: inline-block;
                    color: #ffffff;
                    text-decoration: underline;
                    font-size: 20px; /* Larger font size */
                }
                /* Snow animation */
                .snowflakes {
                    position: absolute;
                    top: 0;
                    left: 0;
                    width: 100%;
                    height: 100%;
                    pointer-events: none;
                    z-index: 0;
                    overflow: hidden;
                    background: transparent;
                }
                .snowflake {
                    position: absolute;
                    width: 12px; /* Slightly larger snowflakes */
                    height: 12px; /* Slightly larger snowflakes */
                    background-color: #ffffff;
                    border-radius: 50%;
                    opacity: 0.8;
                    animation: snowflake-fall linear infinite;
                }
                @keyframes snowflake-fall {
                    to {
                        transform: translateY(100vh);
                    }
                }
                /* Generating snowflakes */
                .snowflake:nth-child(1) { left: 10%; animation-duration: 8s; animation-delay: 0s; }
                .snowflake:nth-child(2) { left: 20%; animation-duration: 9s; animation-delay: 1s; }
                .snowflake:nth-child(3) { left: 30%; animation-duration: 8s; animation-delay: 2s; }
                .snowflake:nth-child(4) { left: 40%; animation-duration: 10s; animation-delay: 3s; }
                .snowflake:nth-child(5) { left: 50%; animation-duration: 12s; animation-delay: 4s; }
                .snowflake:nth-child(6) { left: 60%; animation-duration: 9s; animation-delay: 5s; }
                .snowflake:nth-child(7) { left: 70%; animation-duration: 11s; animation-delay: 6s; }
                .snowflake:nth-child(8) { left: 80%; animation-duration: 8s; animation-delay: 7s; }
                .snowflake:nth-child(9) { left: 90%; animation-duration: 10s; animation-delay: 8s; }
                .snowflake:nth-child(10) { left: 5%; animation-duration: 13s; animation-delay: 9s; }
                .snowflake:nth-child(11) { left: 15%; animation-duration: 9s; animation-delay: 10s; }
                .snowflake:nth-child(12) { left: 25%; animation-duration: 12s; animation-delay: 11s; }
                .snowflake:nth-child(13) { left: 35%; animation-duration: 11s; animation-delay: 12s; }
                .snowflake:nth-child(14) { left: 45%; animation-duration: 10s; animation-delay: 13s; }
                .snowflake:nth-child(15) { left: 55%; animation-duration: 12s; animation-delay: 14s; }
                .snowflake:nth-child(16) { left: 65%; animation-duration: 9s; animation-delay: 15s; }
                .snowflake:nth-child(17) { left: 75%; animation-duration: 13s; animation-delay: 16s; }
                .snowflake:nth-child(18) { left: 85%; animation-duration: 11s; animation-delay: 17s; }
                .snowflake:nth-child(19) { left: 95%; animation-duration: 12s; animation-delay: 18s; }
                .snowflake:nth-child(20) { left: 50%; animation-duration: 9s; animation-delay: 19s; }
            </style>
        </head>
        <body>
            <div class="snowflakes">
                <!-- The snowflakes will be dynamically generated by JavaScript -->
            </div>
            <div class="container">
                <h1>fastupload.fun</h1>
                <p>Download it <a href="{{ file_download_url }}">here</a>.</p>
                <input type="text" id="fileLink" value="{{ file_uploaded_url }}" readonly>
                <br>
                <button onclick="copyLink()">Share Link</button>
                <br>
                <a href="{{ index_url }}" class="back-link">Upload your own files!</a>
                <script>
                    function copyLink() {
                        var link = document.getElementById('fileLink');
                        link.select();
                        document.execCommand('copy');
                        alert('Link copied to clipboard!');
                    }
                </script>
            </div>
            <script>
                function createSnowflakes() {
                    const snowflakesContainer = document.querySelector('.snowflakes');
                    for (let i = 0; i < 100; i++) {
                        const snowflake = document.createElement('div');
                        snowflake.classList.add('snowflake');
                        snowflake.style.left = `${Math.random() * 100}vw`;
                        snowflake.style.animationDuration = `${Math.random() * 10 + 6}s`; // Slightly faster
                        snowflake.style.animationDelay = `${Math.random() * 10}s`;
                        snowflake.style.opacity = `${Math.random() * 0.5 + 0.5}`;
                        snowflake.style.width = `${Math.random() * 15 + 5}px`;
                        snowflake.style.height = `${Math.random() * 15 + 5}px`;
                        snowflakesContainer.appendChild(snowflake);
                    }
                }
                createSnowflakes();
            </script>
        </body>
        </html>
    ''', file_download_url=file_download_url, file_uploaded_url=file_uploaded_url, index_url=index_url)

@app.route('/uploads/<filename>')
def serve_file(filename):
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    
    if not os.path.exists(file_path):
        return "File not found", 404

    response = Response()
    response.headers['Content-Disposition'] = f'attachment; filename="{filename}"'
    response.headers['Content-Type'] = 'application/octet-stream'
    
    with open(file_path, 'rb') as file:
        response.set_data(file.read())
    
    return response

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
