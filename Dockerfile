FROM ubuntu:22.04

ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONUNBUFFERED=1

RUN apt-get update && apt-get install -y \
    build-essential \
    autoconf \
    bison \
    flex \
    gcc \
    g++ \
    git \
    libprotobuf-dev \
    libnl-route-3-dev \
    libtool \
    make \
    pkg-config \
    protobuf-compiler \
    python3 \
    python3-pip \
    python3-dev \
    python3-numpy \
    python3-pandas \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

RUN git clone https://github.com/google/nsjail.git /nsjail && \
    cd /nsjail && \
    make && \
    cp nsjail /usr/local/bin/ && \
    rm -rf /nsjail

WORKDIR /app

COPY requirements.txt .
RUN pip3 install --no-cache-dir -r requirements.txt

COPY app.py .
COPY nsjail.cfg .

RUN useradd -m -u 1000 appuser && \
    chown -R appuser:appuser /app


EXPOSE 8080

HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python3 -c "import requests; requests.get('http://localhost:8080/health')" || exit 1

CMD ["python3", "app.py"]
