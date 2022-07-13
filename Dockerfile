FROM alpine:3.16.0
RUN apk update \
    && apk add --no-cache gcc git python3 python3-dev py3-pip libgit2-dev musl-dev