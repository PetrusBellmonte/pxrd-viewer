# Use official Python image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Copy project files
COPY . /app

# Install pip and pip-tools
RUN pip install --upgrade pip && \
    pip install pip-tools

# Compile and install dependencies from pyproject.toml
RUN pip-compile pyproject.toml --output-file requirements.txt && \
    pip install -r requirements.txt

# Expose Streamlit default port
EXPOSE 8501

# Run Streamlit app
CMD ["streamlit", "run", "App.py"]
