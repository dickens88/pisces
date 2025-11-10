FROM python:3.8.10

# We copy just the requirements.txt first to leverage Docker cache
COPY ./requirements.txt /app/requirements.txt

WORKDIR /app

RUN pip install -r requirements.txt 

ENTRYPOINT [ "python" ]

CMD [ "app.py" ]
