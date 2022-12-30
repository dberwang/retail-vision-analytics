# update 
sudo apt-get update
sudo apt-get -y upgrade

# install dependencies
sudo apt install -y protobuf-compiler libprotoc-dev python3-opencv python3.8-dev python3.8-venv

# setup the virtual environment for python
python3 -m venv venv
source venv/bin/activate

# install the python libraries
python3 -m pip install --upgrade pip
pip3 install numpy
pip3 install -r requirements.txt
cd ByteTrack
python3 setup.py develop
pip3 install cython
pip3 install 'git+https://github.com/cocodataset/cocoapi.git#subdirectory=PythonAPI'
pip3 install cython_bbox

# download the pre-trained model
mkdir videos
mkdir pretrained
cd pretrained
gdown "1P4mY0Yyd3PPTybgZkjMYhFri88nTmJX5"
cd ..
cd ..

# setup flask app
export FLASK_APP=index.py
export FLASK_DEBUG=1

flask run -h 0.0.0.0

# run the demo track
# python3 tools/demo_track.py video -f exps/example/mot/yolox_x_mix_det.py -c pretrained/bytetrack_x_mot17.pth.tar --fp16 --fuse --save_result

