FROM python:3.11-slim

WORKDIR /workshop

COPY pyproject.toml .
RUN pip install --no-cache-dir -e ".[test]"

COPY . .

ENV PYTHONPATH=/workshop/src

ENTRYPOINT ["pytest", "tests/", "-v"]
