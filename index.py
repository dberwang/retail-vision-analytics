import imghdr
import os
from flask import Flask, render_template, request, redirect, url_for, abort, send_from_directory
from werkzeug.utils import secure_filename

app = Flask(__name__)

app.config['MAX_CONTENT_LENGTH'] = 2 * 1024 * 1024 * 1024
app.config['UPLOAD_EXTENSIONS'] = ['.mp4']
app.config['UPLOAD_PATH'] = 'ByteTrack/videos'
app.config['DOWNLOAD_PATH'] = 'ByteTrack/YOLOX_outputs/yolox_x_mix_det/track_vis'

@app.errorhandler(413)
def too_large(e):
    return "File is too large", 413

@app.route('/')
def index():
    # remove previous files in the upload path
    for f in os.listdir(app.config['UPLOAD_PATH']):
        os.remove(os.path.join(app.config['UPLOAD_PATH'], f))
    
    # remove all folder and files in the download path
    os.system('rm -rf ' + app.config['DOWNLOAD_PATH'] + '/*')

    # render the upload webpage
    return render_template('index.html')

@app.route('/', methods=['POST'])
def upload_process_video():
    # Upload video
    uploaded_file = request.files['file']
    filename = secure_filename(uploaded_file.filename)
    if filename != '':
        file_ext = os.path.splitext(filename)[1]
        if file_ext not in app.config['UPLOAD_EXTENSIONS']:
            return render_template('index.html')
        uploaded_file.save(os.path.join(app.config['UPLOAD_PATH'], filename))
        
        # Process video
        os.chdir('/workspace/retail-vision-analytics/ByteTrack')
        os.system('python3 tools/demo_track.py video --path videos/' + filename + \
            ' -f exps/example/mot/yolox_x_mix_det.py -c pretrained/bytetrack_x_mot17.pth.tar --fp16 --fuse --save_result')
        os.chdir('/workspace/retail-vision-analytics')
        # os.chdir('/home/paperspace/retail-vision-analytics/ByteTrack')
        # os.system('python3 tools/demo_track.py video --path videos/' + filename + \
        #     ' -f exps/example/mot/yolox_x_mix_det.py -c pretrained/bytetrack_x_mot17.pth.tar --fp16 --fuse --save_result')
        # os.chdir('/home/paperspace/retail-vision-analytics')     
        return render_template('results.html')

    else:
        # Upload not complete, restore upload page
        return render_template('index.html')


@app.route('/viewmp4', methods=['GET', 'POST'])
def viewmp4():
    # create a string for the mp4 path and filename
    mp4_path = ''
    mp4_filename = ''

    # find the folder where of the annotated video file
    # set mp4_path to the path of the only directory in the download path
    for f in os.listdir(app.config['DOWNLOAD_PATH']):
        if os.path.isdir(os.path.join(app.config['DOWNLOAD_PATH'], f)):
            mp4_path = app.config['DOWNLOAD_PATH'] + '/' + f
    
    # find the annotated video file in the mp4_path
    # it will be the only file in the mp4_path
    mp4_filename = os.listdir(mp4_path)[0]

    # check if it has the mp4 extension, fail if it does not
    assert(os.path.splitext(os.path.join(mp4_path, mp4_filename))[1] == '.mp4')

    # play the video
    # works, but error in safari: failed to load resource: plug-in handled load
    # does not work in brave
    return send_from_directory(directory=mp4_path, filename=mp4_filename)


@app.route('/viewtxt', methods=['GET', 'POST'])
def viewtxt():
    txt_filename = ''

    # find the name of the text file
    # it will be the only text file in the download path with the .txt extension
    for f in os.listdir(app.config['DOWNLOAD_PATH']):
        if os.path.splitext(os.path.join(app.config['DOWNLOAD_PATH'], f))[1] == '.txt':
            txt_filename = f
    
    # display the text results
    return send_from_directory(directory=app.config['DOWNLOAD_PATH'], filename=txt_filename)    

if __name__ == "__main__":
    app.run(debug=True)