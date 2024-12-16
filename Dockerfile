FROM python:3.9-slim-bullseye

WORKDIR /app

RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    software-properties-common \
    git \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt

COPY streamlit_app.py streamlit_app.py
COPY lorna_functions.py lorna_functions.py
COPY lorna_text_objects.py lorna_text_objects.py

# Copy the entire /data directory into the image
COPY data /app/data

EXPOSE 8080

HEALTHCHECK CMD curl --fail http://localhost:8080/_stcore/health

ENTRYPOINT ["streamlit", "run", "streamlit_app.py", "--server.port=8080", "--server.address=0.0.0.0"]