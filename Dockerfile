FROM python:3.12-slim

# Set the working directory
WORKDIR /app

# Copy all files
COPY . .

# Install system dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    gcc \
    libffi-dev \
    ffmpeg \
    aria2 \
    make \
    g++ \
    cmake \
    unzip \
    wget \
    ca-certificates && \
    rm -rf /var/lib/apt/lists/*

# Install Bento4 tools (for mp4decrypt)
RUN wget -q https://github.com/axiomatic-systems/Bento4/archive/v1.6.0-639.zip && \
    unzip v1.6.0-639.zip && \
    cd Bento4-1.6.0-639 && \
    mkdir build && \
    cd build && \
    cmake .. && \
    make -j$(nproc) && \
    cp mp4decrypt /usr/local/bin/ && \
    cd ../.. && \
    rm -rf Bento4-1.6.0-639 v1.6.0-639.zip

# Install Python dependencies
RUN pip3 install --no-cache-dir --upgrade pip && \
    pip3 install --no-cache-dir -r requirements.txt && \
    pip3 install --no-cache-dir yt-dlp

# Run the application
CMD ["sh", "-c", "gunicorn app:app & python3 main.py"]









