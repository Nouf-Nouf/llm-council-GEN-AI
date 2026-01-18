
FROM python:3.14.2-slim-trixie

WORKDIR /usr/src/app
COPY . .
RUN pip install --no-cache-dir -r requirements.txt
EXPOSE 8001
CMD ["python", "-u", "main.py"]