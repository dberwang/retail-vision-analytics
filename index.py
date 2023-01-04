import imghdr
import os
from flask import Flask, render_template, request, redirect, url_for, abort, send_from_directory, \
    send_file, stream_with_context, Response
from werkzeug.utils import secure_filename
import zipfile
import requests


app = Flask(__name__)

app.config['MAX_CONTENT_LENGTH'] = 2 * 1024 * 1024 * 1024
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 43200
app.config['UPLOAD_EXTENSIONS'] = ['.mp4']
app.config['UPLOAD_PATH'] = 'ByteTrack/videos'
app.config['DOWNLOAD_PATH'] = 'ByteTrack/YOLOX_outputs/yolox_x_mix_det/track_vis'

@app.errorhandler(413)
def too_large(e):
    return "File is too large", 413

@app.route('/')
def index():
    # Remove all files in the upload path
    for f in os.listdir(app.config['UPLOAD_PATH']):
        os.remove(os.path.join(app.config['UPLOAD_PATH'], f))
    
    # Remove all folder and files in the download path
    os.system('rm -rf ' + app.config['DOWNLOAD_PATH'] + '/*')

    # render the upload webpage
    return render_template('index.html')

@app.route('/', methods=['POST'])
def upload_process_video():
    # Upload video
    uploaded_file = request.files['file']
    filename = secure_filename(uploaded_file.filename)

    # Do not upload if filename is blank or not of the type in UPLOAD EXTENSIONS
    if filename != '':
        file_ext = os.path.splitext(filename)[1]
        if file_ext not in app.config['UPLOAD_EXTENSIONS']:
            return render_template('index.html')
        print('Uploading... Please wait')
        uploaded_file.save(os.path.join(app.config['UPLOAD_PATH'], filename))
        print('Upload complete')

        # Process video
        print('Processing... Please wait a while')
        os.chdir('/workspace/retail-vision-analytics/ByteTrack')
        os.system('python3 tools/demo_track.py video --path videos/' + filename + \
            ' -f exps/example/mot/yolox_x_mix_det.py -c pretrained/bytetrack_x_mot17.pth.tar --fp16 --fuse --save_result')
        os.chdir('/workspace/retail-vision-analytics')

        # Render results page
        return render_template('results.html')

    else:
        # Upload not complete, restore upload page
        return render_template('index.html')


@app.route('/play-mp4', methods=['GET', 'POST'])
def play_mp4():
    # Create a string for the mp4 path and filename
    mp4_path = ''
    mp4_filename = ''

    # Find and set mp4_path to the folder of the annotated video file
    for file in os.listdir(app.config['DOWNLOAD_PATH']):
        if os.path.isdir(os.path.join(app.config['DOWNLOAD_PATH'], file)):
            mp4_path = app.config['DOWNLOAD_PATH'] + '/' + file
    
    # Find and set the mp4_filename to the the annotated video file
    mp4_filename = os.listdir(mp4_path)[0]

    # Assert video file has the mp4 extension
    assert(os.path.splitext(os.path.join(mp4_path, mp4_filename))[1] in app.config['UPLOAD_EXTENSIONS'])

    # Play the video
    # works, but error in safari: failed to load resource: plug-in handled load
    # does not work in brave
    return send_from_directory(mp4_path, mp4_filename)

@app.route('/view-txt', methods=['GET', 'POST'])
def view_txt():
    # Create a string for the txt filename
    txt_filename = ''

    # Set the name of the text file to the .txt file in the download path
    for file in os.listdir(app.config['DOWNLOAD_PATH']):
        if os.path.splitext(os.path.join(app.config['DOWNLOAD_PATH'], file))[1] == '.txt':
            txt_filename = file
    
    # Display the text results
    return send_from_directory(app.config['DOWNLOAD_PATH'], txt_filename)

@app.route('/download-zip')
def download_zip():
    # Create directory if it does not exist
    directory = 'tmp'
    os.makedirs(directory, exist_ok=True)

    # Create zipfile
    zip_file = zipfile.ZipFile('tmp/results.zip', 'w')
    
    # Iterate over all the files in the directory
    for root, dirs, files in os.walk(app.config['DOWNLOAD_PATH']):
        for file in files:
            if os.path.splitext(os.path.join(app.config['DOWNLOAD_PATH'], file))[1] == '.txt':
            # Add txt file to the zip file
                zip_file.write(os.path.join(root, file), file)

    # Close the zip file
    zip_file.close()

    # Send the zip file to the user
    return send_file('tmp/results.zip', as_attachment=True)

if __name__ == "__main__":
    app.run(debug=True)
