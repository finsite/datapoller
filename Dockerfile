FROM python:3.11-slim as base

WORKDIR /app

# Accept environment variables as build arguments
ARG STOCK_API_KEY
ARG NEWS_API_KEY
ARG POLL_INTERVAL

# Set the environment variables in the container
ENV STOCK_API_KEY=${STOCK_API_KEY}
ENV NEWS_API_KEY=${NEWS_API_KEY}
ENV POLL_INTERVAL=${POLL_INTERVAL}

# Copy the application requirements file into the container
COPY requirements.txt .

# Upgrade pip
RUN pip install --upgrade pip

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code into the container
COPY . .

# Expose any necessary ports
# EXPOSE 8080

# Ensure Python doesn't buffer the output
ENV PYTHONUNBUFFERED=1

# Set a default command to run when the container starts
CMD ["python", "main.py"]

