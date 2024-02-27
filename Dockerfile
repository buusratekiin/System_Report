FROM python:3.10 


# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

COPY requirements.txt .
# install python dependencies
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# running migrations
RUN python manage.py migrate

EXPOSE 8000
# gunicorn
CMD ["python3","manage.py","runserver","0.0.0.0:8000"]
