FROM python:3.11

COPY . .

WORKDIR /app

RUN pip install pipenv

RUN pipenv install --deploy

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host=0.0.0.0", "--reload"]