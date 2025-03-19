FROM python:3.12-slim

WORKDIR /app

ENV PIP_ROOT_USER_ACTION=ignore
ENV PIP_NO_CACHE_DIR=1
ENV PYTHONPATH=src

COPY requirements.txt .

RUN pip install --upgrade pip && pip install -r requirements.txt

COPY src src

EXPOSE 8000

CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
