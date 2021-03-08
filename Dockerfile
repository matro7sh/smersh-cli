FROM debian:latest

RUN apt-get update
RUN apt-get -y full-upgrade
RUN apt-get install -y git python3 python3-pip

COPY . /smersh-cli
WORKDIR /smersh-cli
RUN python3 setup.py install

ENTRYPOINT ["smersh-cli"]