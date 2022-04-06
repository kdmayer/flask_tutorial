FROM python:3.8-slim-buster

WORKDIR /app
ADD . /app
RUN pip install flask
RUN pip install Flask-SQLAlchemy

EXPOSE 5000

CMD ["python", "app.py", "--port=5000"]