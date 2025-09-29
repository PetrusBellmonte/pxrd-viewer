# ----------- Builder stage -----------
FROM python:3.11-slim AS builder

WORKDIR /app

COPY pyproject.toml /app

RUN pip install --upgrade pip && \
    pip install pip-tools wheel

# Compile requirements and build wheels
RUN pip-compile pyproject.toml --output-file requirements.txt && \
    pip wheel --wheel-dir=/app/wheels -r requirements.txt

# ----------- Final stage -----------
FROM python:3.11-slim

WORKDIR /app

COPY pxrd_viewer /app/pxrd_viewer
COPY --from=builder /app/wheels /wheels

RUN pip install --upgrade pip && \
    pip install --no-index --find-links=/wheels /wheels/*

EXPOSE 8501

CMD ["streamlit", "run", "App.py"]
