# Start from a base-image containing Python 3.11 ("slim" is a minimal OS version)
FROM python:3.11-slim

# Defines the target "working" directory to be "/code"
WORKDIR /code

# Copies the file requirements.txt into the "/code" directory
COPY ./requirements.txt /code/requirements.txt

# Install requirements ("--no-cache-dir" to keep a Docker image as small as possible)
RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

# Copy all source code from "/src" to the image
COPY ./server /code/server

# Extend "PYTHONPATH" to reference code outside main.py
ENV PYTHONPATH="$PATH:/code"

# Expose port for request from outside container
EXPOSE 8080

# Use "uvicorn" to start FastAPI service from main.py on exposed port
CMD ["uvicorn", "server.py.main:app", "--host", "0.0.0.0", "--port", "8080"]
