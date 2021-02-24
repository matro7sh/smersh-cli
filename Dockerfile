FROM debian:latest

RUN apt-get update
RUN apt-get -y full-upgrade
RUN apt-get install -y python3 python3-pip

COPY . /smersh-cli
RUN pip3 install -r /smersh-cli/requirements.txt

ENTRYPOINT ["python3", "/smersh-cli/main.py"]