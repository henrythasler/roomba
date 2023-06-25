FROM python:3.10.5-alpine3.16

# docker build -t python3-imaging .

# make sure we use the latest versions
RUN apk upgrade --update \
#
### tools
    && apk add \
            bash \
            wget \
            curl \
            tar \
            nano \
            freetype \
            openblas \
            libstdc++ \
#
# build dependencies
    && apk add --no-cache --virtual .build-deps \
        build-base \
        gfortran \
        openblas-dev \
#
### python libraries
    && python3 -m pip install -U paho-mqtt numpy matplotlib scipy \
# # remove clutter
    && apk del .build-deps