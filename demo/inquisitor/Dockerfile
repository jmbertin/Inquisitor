FROM debian:bullseye-slim

COPY ./inquisitor.py /home/inquisitor.py

RUN apt-get update && \
    apt-get install -y python3 python3-pip && \
    pip3 install scapy netifaces argparse

CMD ["tail", "-f", "/dev/null"]
