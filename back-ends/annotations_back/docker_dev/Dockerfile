# First stage - install all dependencies for the project
FROM python:3.10.10 as Deps

# build code
RUN mkdir /code
WORKDIR /code
COPY ./annotations_back/requirements.txt /code/requirements.txt
RUN pip install --user --no-cache-dir -r requirements.txt

# Second stage
FROM python:3.10.13-alpine3.19 as app

# Imagen docker alpine of linux
RUN apk add --no-cache libpq
# Image to detect the character encoding of a file 
RUN pip install chardet

# Create directory of code and move files into
RUN mkdir /code
WORKDIR /code
# Install google library for google identity secutiry
COPY ./pyGoogleAuthLib /code
RUN pip install . 

COPY --from=Deps /root/.local /root/.local
COPY ./annotations_back/Annotations_app /code/Annotations_app
COPY ./annotations_back/Annotations_back /code/Annotations_back
COPY ./annotations_back/manage.py /code
COPY ./annotations_back/docker_dev/run.sh /code

ENV DJANGO_SETTINGS_MODULE=Annotations_back.settings_prod

# Set python environment variables
ENV PATH=/root/.local/bin:$PATH
ENV PYTHONUNBUFFERED 1

# This environment variable is used for create a image docker for test in local
# ENV DB_HOSTNAME=host.docker.internal

EXPOSE 8000

RUN ls && chmod +x ./run.sh
CMD ["/bin/sh", "./run.sh"]