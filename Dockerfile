FROM python:3.12

USER root

WORKDIR /app

COPY . .
RUN pip install -r requirements.txt
CMD ["python", "main.py"]