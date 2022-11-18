FROM python:3.11

COPY requirements.txt /tmp

RUN pip install -r /tmp/requirements.txt

WORKDIR /app

COPY ./app .

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]