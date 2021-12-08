# syntax=docker/dockerfile:1

FROM python:3.8.3-slim-buster

WORKDIR /server

COPY requirements.txt /server
RUN pip install -r requirements.txt

COPY . .
EXPOSE 8000 

ADD https://github.com/ufoscout/docker-compose-wait/releases/download/2.2.1/wait /wait
RUN chmod +x /wait

# Run the app
CMD /wait && python server.py

# CMD [ "python", "-m" , "server"]