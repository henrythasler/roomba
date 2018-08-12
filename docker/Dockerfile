from python:3.7.0-alpine3.8

RUN set -ex \
    && apk add --no-cache --virtual .build-deps  \
		build-base

RUN set -ex \
    && apk add --no-cache --virtual .build-deps \
        libpng-dev \
        freetype-dev \
        lapack-dev

RUN set -ex \
    && pip3 install \
        numpy \
        paho-mqtt \
        matplotlib

RUN set -ex \
    && apk add --no-cache --virtual .build-deps  \
		gfortran

RUN set -ex \
    && pip3 install \
        scipy
