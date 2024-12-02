FROM python:3.10-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
EXPOSE 5005
CMD ["python", "run.py"]
# docker build -t my-flask-app .
# docker run -p 5005:5005 my-flask-app