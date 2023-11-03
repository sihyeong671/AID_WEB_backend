FROM python:3.10.9-slim

WORKDIR /app

# COPY ./app .

COPY ./pyproject.toml ./poetry.lock ./

# Docker layer cache 최적화 하기
RUN pip install poetry && poetry config virtualenvs.create false
RUN poetry install

# CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]
