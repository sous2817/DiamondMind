# Use Python 3.11 (Stable for ML)
FROM python:3.11-slim

# Set the working directory inside the container
WORKDIR /app

# 1. Install System Dependencies
# Added 'libsm6', 'libxext6', 'libxrender-dev' to cover all OpenCV base requirements
RUN apt-get update && apt-get install -y \
    libgl1 \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    && rm -rf /var/lib/apt/lists/*

# 2. Install Python Dependencies
COPY requirements.txt .

# Download MediaPipe pose landmarker model (29MB - not in git)
RUN apt-get update && apt-get install -y wget && \
    wget -q https://storage.googleapis.com/mediapipe-models/pose_landmarker/pose_landmarker_heavy/float16/1/pose_landmarker_heavy.task && \
    rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir -r requirements.txt

# 3. Copy the Application Code
COPY . .

# 4. Expose the Port
EXPOSE 8001

# 5. Start the Service
CMD ["python", "main.py"]