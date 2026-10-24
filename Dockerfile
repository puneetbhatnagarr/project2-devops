FROM python:3.12-slim

WORKDIR /app

COPY app/requirements.txt .

RUN pip install --default-timeout=100 --no-cache-dir -i https://mirrors.aliyun.com/pypi/simple/ -r requirements.txt
COPY app/app.py .

EXPOSE 8000

CMD ["python", "app.py"]