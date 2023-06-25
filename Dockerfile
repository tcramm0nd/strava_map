FROM python:3.8-slim-buster

# Set environment variables
ENV PIP_DISABLE_PIP_VERSION_CHECK 1
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set work directory
WORKDIR /strava_map

# Install dependencies
COPY ./requirements.txt .
RUN pip install -r requirements.txt

RUN apt-get update &&\
    apt-get install -y gdal-bin
    # apt-get install -y binutils libproj-dev gdal-bin

# Copy project
COPY . .