from flask import Flask, render_template_string, request, jsonify
import os
from datetime import datetime

app = Flask(__name__)
UPLOAD_FOLDER = './photos'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Create the upload folder if it doesn't exist
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

@app.route('/')
def index():
    # Get the status of existing folders
    folders = []
    for folder_name in os.listdir(UPLOAD_FOLDER):
        folder_path = os.path.join(UPLOAD_FOLDER, folder_name)
        if os.path.isdir(folder_path):
            num_photos = len([name for name in os.listdir(folder_path) if os.path.isfile(os.path.join(folder_path, name))])
            folders.append({'name': folder_name, 'photos': num_photos})
    
    return render_template_string('''
    <!doctype html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Upload Photos</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                background-color: #f0f0f5;
                color: #333;
                text-align: center;
                padding: 50px;
            }

            h1 {
                color: #007BFF;
                font-size: 2.5em;
                margin-bottom: 20px;
            }

            form {
                background-color: #fff;
                padding: 20px;
                border-radius: 8px;
                box-shadow: 0px 0px 15px rgba(0, 0, 0, 0.1);
                display: inline-block;
                width: 100%;
                max-width: 400px;
                box-sizing: border-box;
            }

            input[type=file] {
                margin: 10px 0;
            }

            input[type=submit] {
                background-color: #007BFF;
                color: white;
                border: none;
                padding: 10px 20px;
                text-transform: uppercase;
                letter-spacing: 1px;
                cursor: pointer;
                border-radius: 4px;
                transition: background-color 0.3s ease;
            }

            input[type=submit]:hover {
                background-color: #0056b3;
            }

            .progress {
                width: 100%;
                background-color: #f0f0f5;
                border-radius: 5px;
                margin-top: 20px;
                overflow: hidden;
                height: 25px;
                display: none;
            }

            .progress-bar {
                height: 100%;
                width: 0;
                background-color: #007BFF;
                text-align: center;
                line-height: 25px;
                color: white;
                transition: width 0.3s;
            }

            .folders {
                margin-top: 50px;
            }

            .folder {
                background-color: #fff;
                padding: 15px;
                border-radius: 8px;
                box-shadow: 0px 0px 15px rgba(0, 0, 0, 0.1);
                margin-bottom: 15px;
                text-align: left;
                position: relative;
            }

            .folder input[type="text"] {
                width: calc(100% - 100px);
                font-size: 1.2em;
                border: none;
                background: none;
                color: #007BFF;
                font-weight: bold;
            }

            .folder input[type="text"]:focus {
                outline: none;
            }

            .folder button {
                position: absolute;
                top: 15px;
                right: 15px;
                background-color: #007BFF;
                color: white;
                border: none;
                padding: 5px 10px;
                cursor: pointer;
                border-radius: 4px;
                transition: background-color 0.3s ease;
            }

            .folder button:hover {
                background-color: #0056b3;
            }

            @media (max-width: 500px) {
                form {
                    padding: 15px;
                }

                .folder input[type="text"] {
                    width: calc(100% - 90px);
                }

                input[type=submit] {
                    padding: 8px 15px;
                }
            }
        </style>
    </head>
    <body>
        <h1>Upload Multiple Photos</h1>
        <form id="uploadForm" method="post" enctype="multipart/form-data">
            <input type="file" name="files[]" multiple required>
            <input type="submit" value="Upload">
        </form>
        <div class="progress" id="progressContainer">
            <div class="progress-bar" id="progressBar">0%</div>
        </div>

        <div class="folders">
            {% for folder in folders %}
            <div class="folder">
                <input type="text" value="{{ folder.name }}" data-original="{{ folder.name }}" readonly>
                <button onclick="editFolderName(this)">Edit</button>
                <p>{{ folder.photos }} photos</p>
            </div>
            {% endfor %}
        </div>

        <script>
            document.getElementById('uploadForm').addEventListener('submit', function(event) {
                event.preventDefault();
                const formData = new FormData(this);
                const xhr = new XMLHttpRequest();
                xhr.open('POST', '/upload', true);

                const progressContainer = document.getElementById('progressContainer');
                progressContainer.style.display = 'block'; // Show progress bar

                xhr.upload.addEventListener('progress', function(e) {
                    if (e.lengthComputable) {
                        const percentComplete = (e.loaded / e.total) * 100;
                        const progressBar = document.getElementById('progressBar');
                        progressBar.style.width = percentComplete + '%';
                        progressBar.innerHTML = Math.floor(percentComplete) + '%';
                    }
                });

                xhr.addEventListener('load', function() {
                    if (xhr.status === 200) {
                        document.getElementById('progressBar').style.width = '100%';
                        document.getElementById('progressBar').innerHTML = 'Upload Complete';
                        setTimeout(() => window.location.reload(), 1000);
                    }
                });

                xhr.send(formData);
            });

            function editFolderName(button) {
                const folderDiv = button.parentElement;
                const input = folderDiv.querySelector('input[type="text"]');
                
                if (input.readOnly) {
                    input.readOnly = false;
                    input.focus();
                    button.textContent = 'Save';
                } else {
                    const newName = input.value;
                    const originalName = input.getAttribute('data-original');
                    
                    if (newName !== originalName) {
                        fetch('/rename_folder', {
                            method: 'POST',
                            headers: {
                                'Content-Type': 'application/json'
                            },
                            body: JSON.stringify({ old_name: originalName, new_name: newName })
                        })
                        .then(response => response.json())
                        .then(data => {
                            if (data.success) {
                                input.readOnly = true;
                                input.setAttribute('data-original', newName);
                                button.textContent = 'Edit';
                            } else {
                                alert('Error renaming folder');
                            }
                        });
                    } else {
                        input.readOnly = true;
                        button.textContent = 'Edit';
                    }
                }
            }
        </script>
    </body>
    </html>
    ''', folders=folders)

@app.route('/upload', methods=['POST'])
def upload_file():
    files = request.files.getlist('files[]')
    current_time = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
    unique_folder_path = os.path.join(app.config['UPLOAD_FOLDER'], current_time)
    os.makedirs(unique_folder_path)

    for file in files:
        if file and file.filename != '':
            filename = file.filename
            file.save(os.path.join(unique_folder_path, filename))
    
    return jsonify(success=True)

@app.route('/rename_folder', methods=['POST'])
def rename_folder():
    data = request.json
    old_name = data['old_name']
    new_name = data['new_name']

    old_path = os.path.join(app.config['UPLOAD_FOLDER'], old_name)
    new_path = os.path.join(app.config['UPLOAD_FOLDER'], new_name)

    if os.path.exists(old_path) and not os.path.exists(new_path):
        os.rename(old_path, new_path)
        return jsonify(success=True)
    else:
        return jsonify(success=False), 400

if __name__ == '__main__':
    app.run(port=5001, host="0.0.0.0")
