# Use the latest Ubuntu LTS image
FROM ubuntu:24.04

# Prevent interactive prompts during package installation in Debian/Ubuntu systems
ENV DEBIAN_FRONTEND=noninteractive

# Install packages
RUN apt-get update && apt-get install -y --no-install-recommends \
        software-properties-common \
        gnupg \
        wget \
        lsb-release \
        ca-certificates \
        git \
        build-essential \
        autotools-dev \
        automake \
        libtool \
        libtiff-dev \
        zlib1g-dev \
        libjpeg-dev \
        libpng-dev \
        libleptonica-dev \
        libjbig2dec0-dev \
        poppler-utils \
        unpaper \
        inotify-tools \
        pngquant \
        python3 \
        python3-pip \
        python3.12-venv

RUN add-apt-repository ppa:alex-p/tesseract-ocr-devel -y \
    && apt-get update && apt-get install -y --no-install-recommends \
        tesseract-ocr \
        #tesseract-ocr-all \
        tesseract-ocr-pol \
        tesseract-ocr-eng \
        ocrmypdf \
    && rm -rf /var/lib/apt/lists/*

# Install jbig2enc from source
RUN git clone https://github.com/agl/jbig2enc.git /tmp/jbig2enc \
    && cd /tmp/jbig2enc \
    && ./autogen.sh \
    && ./configure \
    && make \
    && make install \
    && rm -rf /tmp/jbig2enc

# Download trained models for Tesseract
#RUN git clone https://github.com/tesseract-ocr/tessdata.git \
#    && mv -f tessdata/*traineddata /usr/share/tesseract-ocr/5/tessdata/ \
#    && mv -f tessdata/script /usr/share/tesseract-ocr/5/tessdata/ \
#    && rm -rf tessdata

# Download only selected languages for Tesseract (Polish + English)
RUN wget -O /usr/share/tesseract-ocr/5/tessdata/pol.traineddata https://github.com/tesseract-ocr/tessdata_best/raw/main/pol.traineddata \
    && wget -O /usr/share/tesseract-ocr/5/tessdata/eng.traineddata https://github.com/tesseract-ocr/tessdata_best/raw/main/eng.traineddata

WORKDIR /app

# Install Python dependencies
RUN python3 -m venv /venv
ENV PATH="/venv/bin:$PATH"
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY app /app/

# Expose port for the web app
EXPOSE 8080

# Create non-root user and switch
RUN useradd -m appuser
USER appuser

# Set default command
CMD ["python3", "-m", "main"]
