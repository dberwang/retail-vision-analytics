# update 
sudo apt-get update
sudo apt-get -y upgrade

# install dependencies
sudo apt install -y protobuf-compiler libprotoc-dev python3-opencv python3.8-dev python3.8-venv

# # clone the github repository
# git clone https://github.com/ifzhang/ByteTrack.git
cd ByteTrack

# setup the virtual environment for python
python3 -m venv venv
source venv/bin/activate

# install the python libraries
python3 -m pip install --upgrade pip
pip3 install numpy

# error occurs because docker sed torch version in requirements file! 
# *** change to use new req file at rva path
pip3 install -r requirements.txt
python3 setup.py develop
# pip3 install cython
pip3 install 'git+https://github.com/cocodataset/cocoapi.git#subdirectory=PythonAPI'
# pip3 install cython_bbox

# download the pre-trained model
mkdir videos
mkdir pretrained
cd pretrained
gdown "1P4mY0Yyd3PPTybgZkjMYhFri88nTmJX5"
cd ..
cd ..

# run the demo track
# python3 tools/demo_track.py video -f exps/example/mot/yolox_x_mix_det.py -c pretrained/bytetrack_x_mot17.pth.tar --fp16 --fuse --save_result



# to get flask running
# pip3 install Werkzeug==2.2.2
# pip3 install markupsafe==2.1.1
# pip3 install jinja2 3.1.2
# pip3 install flask==2.1.0
# python3 -m pip install numpy==1.23
