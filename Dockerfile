FROM python:3.12
LABEL authors="breno"

WORKDIR .

COPY . .

RUN chmod +x ./entrypoint.sh

RUN pip install -r requirements.txt

EXPOSE 8000
EXPOSE 5432

RUN python manage.py makemigrations
RUN python manage.py migrate
