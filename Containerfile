FROM quay.io/fedora/fedora

RUN dnf install -y python3 python3-pip
COPY import.py /import.py
RUN chmod 755 /import.py
RUN /usr/bin/python3 -m pip --no-cache-dir install webdavclient3 exifread PyYAML
WORKDIR /
ENTRYPOINT /import.py
