import os, zipfile, nbformat
from flask import Flask, render_template, request, send_from_directory, send_file
from werkzeug.utils import secure_filename
from nbconvert.preprocessors import ExecutePreprocessor


app = Flask(__name__)

app.config['MAX_CONTENT_LENGTH'] = 2 * 1024 * 1024 * 1024
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 43200
app.config['UPLOAD_EXTENSIONS'] = ['.mp4']
app.config['UPLOAD_PATH'] = 'ByteTrack/videos'

@app.errorhandler(413)
def too_large(e):
    return "File is too large", 413

@app.route('/')
def index():
    # Remove all files in the upload path
    for f in os.listdir(app.config['UPLOAD_PATH']):
        os.remove(os.path.join(app.config['UPLOAD_PATH'], f))

    # Remove all folder and files in the download path
    os.system('rm -rf ByteTrack/YOLOX_outputs/yolox_x_mix_det/track_vis/*')

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

        # Create tmp directory if it does not exist
        os.makedirs('tmp', exist_ok=True)

        # Move results file from ByteTrack to the tmp folder
        os.system('mv ByteTrack/YOLOX_outputs/yolox_x_mix_det/track_vis/*.txt tmp/results.txt')
        os.system('mv ByteTrack/YOLOX_outputs/yolox_x_mix_det/track_vis/20*/*.mp4 tmp/results.mp4')

        # Convert video to HTML5 format 
        # It takes a long time and should only be done lazily
        # There are better ways to do on the fly
        print('Converting video to a web compatible format')
        os.system('ffmpeg -i tmp/results.mp4 -vcodec h264 -acodec aac -strict -2 tmp/results_web.mp4')
        
        # Run the analytics notebook using nbformat and nbconvert
        #  https://nbconvert.readthedocs.io/en/latest/execute_api.html
        
        # Open the notebook after copying it to tmp folder
        os.system('cp notebooks/analytics.ipynb tmp/analytics.ipynb')
        with open('notebooks/analytics.ipynb') as f:
            nb = nbformat.read(f, as_version=4)
        
        # Execute the notebook
        ep = ExecutePreprocessor(timeout=600, kernel_name='python3')
        ep.preprocess(nb, {'metadata': {'path': 'notebooks/'}})

        # Save the executed notebook 
        with open('tmp/analytics.ipynb', 'w', encoding='utf-8') as f:
            nbformat.write(nb, f)
        
        # Convert the executed notebook to html for viewing
        os.system('jupyter nbconvert --to html tmp/analytics.ipynb')

        # Render results page
        return render_template('results.html')

    else:
        # Upload not complete, restore upload page
        return render_template('index.html')


@app.route('/play-mp4', methods=['GET', 'POST'])
def play_mp4():
    # Play the video
    return send_from_directory('tmp', 'results_web.mp4')

@app.route('/view-txt', methods=['GET', 'POST'])
def view_txt():    
    # Display the text results
    print('View text')
    return send_from_directory('tmp', 'results.txt')

@app.route('/view-analytics', methods=['GET', 'POST'])
def view_analytics():  
    # Display the analytics
    print('View analytics')
    return send_from_directory('tmp', 'analytics.html')

@app.route('/download-zip')
def download_zip():
    # Create zipfile
    zip_file = zipfile.ZipFile('static/results.zip', 'w')
    
    # Iterate over all the files in the directory
    for root, dirs, files in os.walk('tmp'):
        for file in files:
           zip_file.write(os.path.join(root, file), file)

    # Close the zip file
    zip_file.close()

    # Send the zip file to the user
    return send_file('static/results.zip', as_attachment=True)


if __name__ == "__main__":
    app.run(debug=True)