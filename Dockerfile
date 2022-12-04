FROM python:3.11-slim-bullseye as base
RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*
ENV PYTHONUNBUFFERED=true
ENV PYTHONDONTWRITEBYTECODE=1
ARG PORT=80
ENV UVICORN_PORT=$PORT
# for Docker desktop
EXPOSE 80
WORKDIR /code
COPY ./requirements.txt /code/requirements.txt
RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt
COPY ./app /code/app/

CMD ["uvicorn", "app.api:app", "--host", "0.0.0.0"]
# "--port", ""${UVICORN_PORT:-80}
