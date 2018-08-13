#from python:3.6.6-alpine3.8
FROM alpine:3.8

# make sure we use the latest versions
RUN apk --update upgrade

# helper packages (you never know)
RUN apk add --no-cache --virtual .helper \
        bash \
        wget \
        curl \
        tar \
        nano

# build dependencies
RUN apk add --no-cache --virtual .build-deps \
        libpng-dev \
        freetype-dev \
        py-numpy-dev \
        build-base

# actual packages we require for the visuals
RUN apk add --no-cache --repository http://dl-cdn.alpinelinux.org/alpine/edge/community \
        py3-paho-mqtt \
        py3-numpy \
        py3-scipy

# another package that is required for the visuals
RUN python3 -mpip install -U matplotlib

# remove clutter
RUN apk del .build-deps

# runtime-dependency
RUN apk add --no-cache --virtual \
        freetype