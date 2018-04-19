FROM python:2.7
ENV PYTHONUNBUFFERED=1
RUN apt-get install libmysqlclient-dev
RUN mkdir /code
ADD requirements /code/requirements
RUN pip install -r code/requirements/docker.txt
WORKDIR /code
