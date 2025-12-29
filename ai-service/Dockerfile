# FIX: Downgrade to 3.11-slim. 
# MediaPipe supports 3.11 fully; 3.12 is often unstable for C++ extensions.
FROM python:3.11-slim

# Set the working directory inside the container
WORKDIR /app

# 1. Install System Dependencies
# Required for OpenCV and MediaPipe
RUN apt-get update && apt-get install -y \
    libgl1 \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# 2. Install Python Dependencies
COPY requirements.txt .
# Copy the task file if you are using the Task API, otherwise it's safe to keep
COPY pose_landmarker_heavy.task .
RUN pip install --no-cache-dir -r requirements.txt

# 3. Copy the Application Code
COPY . .

# 4. Expose the Port
EXPOSE 8001

# 5. Start the Service
CMD ["python", "main.py"]