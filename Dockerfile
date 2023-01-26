# Use an official Python runtime as a parent image
FROM alpine

RUN apk add --no-cache python3-dev \
    py-pip \
    zlib-dev \
    cmake \
    gcc \
    libc-dev \
    jpeg-dev \
    musl-dev \
    postgresql-libs \
    postgresql-dev \
    libffi-dev \
    openssl-dev \
    cargo


# Set environment varibles
# ENV PYTHONUNBUFFERED 1
# ENV DJANGO_ENV dev

COPY ./requirements.txt /code/requirements.txt
RUN pip3 install --upgrade pip
RUN pip3 install pillow \
    Django 
    # djangorestframework

# Upgrade pip3
RUN python3 -m pip install --upgrade pip

# Install any needed packages specified in requirements.txt
RUN pip3 install -r /code/requirements.txt

# Install Azure Cognitive Services Vision librari

RUN pip3 install --upgrade azure-cognitiveservices-vision-computervision

# Copy the current directory contents into the container at /code/
COPY . /code/
# Set the working directory to /code/

WORKDIR /code
# WORKDIR /code/mybackend

# WORKDIR /code/tutorial

#RUN python3 manage.py migrate

# RUN python3 manage.py collectstatic --no-post-process --noinput
RUN chmod +x /code/sleep_infinity.sh
EXPOSE 8000
ENTRYPOINT [ "/code/sleep_infinity.sh" ]
# ENTRYPOINT ["gunicorn", "--bind", "0.0.0.0:8000", "--log-level", "debug", "--access-logfile", "-", "--log-file", "-", "tutorial.wsgi:application"]
