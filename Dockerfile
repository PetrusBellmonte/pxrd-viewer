# Use official Python image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Copy project files
COPY . /app

# Install pip and poetry
RUN pip install --upgrade pip && \
    pip install poetry

# Install dependencies from pyproject.toml
RUN poetry install --no-interaction --no-ansi

# Expose Streamlit default port
EXPOSE 8501

# Run Streamlit app
CMD ["streamlit", "run", "App.py"]