FROM python:3.8-slim-buster

WORKDIR /python-docker

RUN apt-get update && \ 
    apt-get install -y curl && \
    curl -s https://install.speedtest.net/app/cli/install.deb.sh | bash && \
    apt-get install -y speedtest && \
    apt-get update

COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt

COPY . .

CMD [ "python3", "-m" , "flask", "run", "--host=0.0.0.0", "--port=9516"]