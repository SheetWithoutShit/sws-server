FROM python:3.8.2

RUN mkdir /server
COPY requirements.txt /server
COPY server /server
WORKDIR /server

RUN pip install --upgrade pip && \
    pip install -r requirements.txt

EXPOSE 5000

CMD ["python", "run.py"]
