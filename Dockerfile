FROM resin/raspberrypi3-python:2.7

RUN apt-get update && apt-get install -y -q \
    libasound2-dev \
    libpulse-dev \
    libsox-fmt-mp3 \
    sox \
    swig \
    vlc-nox \
    --no-install-recommends

RUN git clone --depth=1 https://github.com/alexa-pi/AlexaPi.git && \
    cd AlexaPi/src && \
    pip install -r requirements.txt && \
    touch /var/log/alexa.log && \
    cp config.template.yaml config.yaml

WORKDIR AlexaPi

COPY credentials.py ./src
CMD python src/credentials.py && python src/main.py

