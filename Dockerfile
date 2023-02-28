# Base image
FROM python:3.10-slim-buster

# Set working directory
WORKDIR /gistapi

# Copy poetry.lock and pyproject.toml
COPY pyproject.toml poetry.lock /gistapi/

# Install Poetry
RUN pip install poetry

# Install dependencies
RUN poetry install --no-root --no-dev

# Copy the rest of the application files
COPY . /gistapi

# Expose port 5000 for the Flask app
EXPOSE 5000

# Set the entrypoint to run the Flask app
ENTRYPOINT ["poetry", "run", "python", "gistapi/gistapi.py"]
