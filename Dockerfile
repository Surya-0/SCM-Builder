FROM python:3.9-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first to leverage Docker cache
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the entrypoint script and make it executable
COPY docker-entrypoint.sh .
RUN chmod +x docker-entrypoint.sh

# Copy the rest of the application
COPY . .

RUN mkdocs build

# Expose the port Streamlit runs on
EXPOSE 8502

# Set the entrypoint script
ENTRYPOINT ["./docker-entrypoint.sh"]

# Command to run the application
CMD ["streamlit", "run", "Home.py", "--server.address", "0.0.0.0", "--server.port", "8502"]
