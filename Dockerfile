FROM nvcr.io/nvidia/tensorrt:21.09-py3

ENV DEBIAN_FRONTEND=noninteractive
ENV FLASK_APP=index.py
ENV FLASK_DEBUG=1
ARG USERNAME=user
ARG WORKDIR=/workspace/retail-vision-analytics

RUN apt-get update && apt-get -y upgrade && apt-get install -y \
        automake autoconf libpng-dev nano python3-pip \
        curl zip unzip libtool swig zlib1g-dev pkg-config \
        python3-mock libpython3-dev libpython3-all-dev \
        g++ gcc cmake make pciutils cpio gosu wget \
        libgtk-3-dev libxtst-dev sudo apt-transport-https \
        build-essential gnupg git xz-utils vim \
        libva-drm2 libva-x11-2 vainfo libva-wayland2 libva-glx2 \
        libva-dev libdrm-dev xorg xorg-dev protobuf-compiler \
        openbox libx11-dev libgl1-mesa-glx libgl1-mesa-dev \
        libtbb2 libtbb-dev libopenblas-dev libopenmpi-dev \
        libprotoc-dev python3-opencv python3.8-dev python3.8-venv ffmpeg \
    && sed -i 's/# set linenumbers/set linenumbers/g' /etc/nanorc \
    && apt clean \
    && rm -rf /var/lib/apt/lists/*

# added this section to clone my repo and cd
RUN git clone https://github.com/dberwang/retail-vision-analytics \
    && cd retail-vision-analytics \
    && cd ByteTrack \
    && mkdir -p YOLOX_outputs/yolox_x_mix_det/track_vis \
    && sed -i 's/torch>=1.7/torch==1.9.1+cu111/g' requirements.txt \
    && sed -i 's/torchvision==0.10.0/torchvision==0.10.1+cu111/g' requirements.txt \
    && sed -i "s/'cuda'/0/g" tools/demo_track.py \
    && pip3 install pip --upgrade \
    && pip3 install -r requirements.txt -f https://download.pytorch.org/whl/torch_stable.html \
    && python3 setup.py develop \
    && pip3 install cython \
    && pip3 install 'git+https://github.com/cocodataset/cocoapi.git#subdirectory=PythonAPI' \
    && pip3 install cython_bbox gdown \
    && mkdir pretrained \
    && cd pretrained \
    && gdown "1P4mY0Yyd3PPTybgZkjMYhFri88nTmJX5" \
    && cd .. \
    && ldconfig \
    && pip cache purge

RUN git clone https://github.com/NVIDIA-AI-IOT/torch2trt \
    && cd torch2trt \
    && git checkout 0400b38123d01cc845364870bdf0a0044ea2b3b2 \
    # https://github.com/NVIDIA-AI-IOT/torch2trt/issues/619
    && wget https://github.com/NVIDIA-AI-IOT/torch2trt/commit/8b9fb46ddbe99c2ddf3f1ed148c97435cbeb8fd3.patch \
    && git apply 8b9fb46ddbe99c2ddf3f1ed148c97435cbeb8fd3.patch \
    && python3 setup.py install

# Doesn't work with the above torch and torchvision packages, but works with the below
RUN pip3 uninstall -y torch torchvision \
    && pip3 install torch torchvision --no-cache-dir

# RUN apt-get update && apt-get install -y --no-install-recommends nvidia-container-runtime

# added the below section to install nvidia drivers compatible with tensorrt
# RUN wget https://developer.download.nvidia.com/compute/cuda/repos/ubuntu2004/x86_64/cuda-keyring_1.0-1_all.deb \
#     && dpkg -i cuda-keyring_1.0-1_all.deb \
#     && apt-get update \
#     && apt-get -y install cuda

RUN echo "root:root" | chpasswd \
    && adduser --disabled-password --gecos "" "${USERNAME}" \
    && echo "${USERNAME}:${USERNAME}" | chpasswd \
    && echo "%${USERNAME}    ALL=(ALL)   NOPASSWD:    ALL" >> /etc/sudoers.d/${USERNAME} \
    && chmod 0440 /etc/sudoers.d/${USERNAME}
USER ${USERNAME}
RUN sudo chown -R ${USERNAME}:${USERNAME} ${WORKDIR}
WORKDIR ${WORKDIR}
