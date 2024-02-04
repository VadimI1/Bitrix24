FROM python:3.9-slim

RUN mkdir code
WORKDIR code

ADD . /code/

RUN pip install -r requirements.txt

CMD python main.py