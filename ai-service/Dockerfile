# Use a lightweight Python 3.12 Linux image
FROM python:3.12-slim

# Set the working directory inside the container
WORKDIR /app

# 1. Install System Dependencies
# OpenCV and MediaPipe require these GL libraries to process images
RUN apt-get update && apt-get install -y \
    libgl1-mesa-glx \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# 2. Install Python Dependencies
# We copy requirements first to leverage Docker layer caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 3. Copy the Application Code
# This includes main.py, pose_engine.py, and the .task model file
COPY . .

# 4. Expose the Port
# The AI Service runs on 8001
EXPOSE 8001

# 5. Start the Service
# We use python directly since main.py invokes Uvicorn programmatically
CMD ["python", "main.py"]