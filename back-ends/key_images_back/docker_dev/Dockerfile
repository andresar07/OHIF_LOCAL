FROM python:3.10.13 as builder

# build code
RUN mkdir /code
WORKDIR /code
COPY ./key_images_back/requirements.txt /code/requirements.txt
RUN pip install --user --no-cache-dir -r requirements.txt

RUN mkdir pyGoogleAuthLib
COPY ./pyGoogleAuthLib/ /code/pyGoogleAuthLib/
RUN pip install /code/pyGoogleAuthLib --user --no-cache-dir 


FROM python:3.10.13-slim as app

RUN apt-get update
RUN apt-get install -y libpq-dev
RUN apt-get clean

#RUN apk add --no-cache libpq
#RUN pip install chardet

# setup application code 
RUN mkdir /code
WORKDIR /code
COPY --from=builder /root/.local /root/.local
COPY ./key_images_back/ /code/
COPY ./key_images_back/docker_dev/run.sh /code

# production
ENV PYTHONUNBUFFERED 1
ENV PATH=/root/.local/bin:$PATH
ENV DJANGO_SETTINGS_MODULE=key_images_back.settings_prod

RUN pip install --no-cache-dir gunicorn

EXPOSE 8000

RUN ls && chmod +x ./run.sh

CMD ["/bin/sh", "./run.sh"]
