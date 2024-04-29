FROM python:3.12
LABEL authors="breno"

WORKDIR .

COPY . .

RUN pip install -r requirements.txt

EXPOSE 8000
CMD [ "python", "manage.py", "makemigrations" ]
CMD [ "python", "manage.py", "migrate" ]
CMD [ "python", "manage.py", "runserver", "--noreload" ]