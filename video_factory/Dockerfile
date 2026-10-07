# Reproducible factory: docker build -t video-factory . 
#   docker run --rm -v "$PWD/workspace:/app/workspace" -v "$PWD/library:/app/library" -v "$PWD/models:/app/models" video-factory watch
FROM python:3.12-slim
RUN apt-get update && apt-get install -y --no-install-recommends ffmpeg fontconfig && rm -rf /var/lib/apt/lists/*
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
RUN python -m factory setup --models none
ENTRYPOINT ["python", "-m", "factory"]
CMD ["watch"]
