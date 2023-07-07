# Use the official lightweight Python image.
# https://hub.docker.com/_/python
FROM python:3.11-slim

# Allow statements and log messages to immediately appear in the logs
ENV PYTHONUNBUFFERED True

# Copy local code to the container image.
ENV APP_HOME /app

WORKDIR $APP_HOME

RUN apt-get update && apt-get install -y \
    build-essential \
    software-properties-common \
    git \
    && rm -rf /var/lib/apt/lists/*

COPY . ./

# Install production dependencies.
RUN pip3 install --no-cache-dir -r requirements.txt

# Run the web service on container startup
ENTRYPOINT streamlit run Home.py --server.port=$PORT --server.address=0.0.0.0
