FROM python:3.8.2

RUN mkdir /server
COPY requirements.txt /server
COPY server /server

ENV TZ=Europe/Kiev
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

RUN pip install --upgrade pip && \
    pip install -r /server/requirements.txt

EXPOSE 5000
WORKDIR /server
CMD ["python", "run.py"]
