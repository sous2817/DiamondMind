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
COPY pose_landmarker_heavy.task .
RUN pip install --no-cache-dir -r requirements.txt

# 3. Copy the Application Code
COPY . .

# 4. Expose the Port
EXPOSE 8001

# 5. Start the Service
CMD ["python", "main.py"]