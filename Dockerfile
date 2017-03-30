FROM resin/raspberrypi3-python:2.7

RUN apt-get update && apt-get install -y -q \
    libasound2-dev \
    libpulse-dev \
    libsox-fmt-mp3 \
    sox \
    swig \
    vlc-nox \
    --no-install-recommends

