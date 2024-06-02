FROM quay.io/fedora/python-311:311

COPY import.py /import.py
RUN /usr/bin/python3.11 -m pip --no-cache-dir install webdavclient3 exifread PyYAML
WORKDIR /
ENTRYPOINT /usr/bin/python3.11 /import.py
