# update 
sudo apt-get update
sudo apt-get -y upgrade

# install dependencies
sudo apt install -y python3-venv
sudo apt-get install -y protobuf-compiler libprotoc-dev
sudo apt install python3-opencv

# clone the github repository
git clone https://github.com/ifzhang/ByteTrack.git
cd ByteTrack

# setup the virtual environment for python
sudo apt-get install -y python3.8-dev python3.8-venv
python3 -m venv venv
source venv/bin/activate

# install the python libraries
pip3 install -r requirements.txt
python3 setup.py develop
pip3 install cython
pip3 install 'git+https://github.com/cocodataset/cocoapi.git#subdirectory=PythonAPI'
pip3 install cython_bbox

# download the pre-trained model
mkdir pretrained
cd pretrained
gdown "1P4mY0Yyd3PPTybgZkjMYhFri88nTmJX5"
cd ..

# run the demo track
python3 tools/demo_track.py video -f exps/example/mot/yolox_x_mix_det.py -c pretrained/bytetrack_x_mot17.pth.tar --fp16 --fuse --save_result
