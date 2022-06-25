FROM alpine:3.16.0
RUN apk update \
    && apk add --no-cache git python3 py3-pip