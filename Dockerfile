FROM joyzoursky/python-chromedriver:3.8-selenium

RUN apt update -y
RUN DEBIAN_FRONTEND=noninteractive apt install -y libx11-xcb1 fonts-ipafont-gothic xfonts-scalable fluxbox xorg xvfb dbus-x11 \
                   xfonts-100dpi xfonts-75dpi xfonts-cyrillic scrot python3-tk ffmpeg
WORKDIR /opt/recorder/
RUN pip install --upgrade pip
COPY src/requirements.txt .
RUN pip install -r requirements.txt

RUN mkdir -p /opt/downloads

COPY src/ .

RUN chmod +x run_xvfb.sh
RUN chmod +x entrypoint.sh

ENTRYPOINT [ "./entrypoint.sh" ]
