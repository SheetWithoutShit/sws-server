FROM python:3.8.2

RUN mkdir /server
COPY requirements.txt /server
COPY server /server

RUN pip install --upgrade pip && \
    pip install -r /server/requirements.txt

EXPOSE 5000
WORKDIR /server
CMD ["python", "run.py"]
