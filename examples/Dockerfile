FROM ubuntu:20.04

# Info
LABEL org.opencontainers.image.authors="raffael@nice.pink"

# General installs
RUN apt-get update && apt-get install -y \
    git \
    curl \
    tar \
    python3.8 \
    python3-pip
    
# Golang
RUN curl -O https://storage.googleapis.com/golang/go1.17.linux-amd64.tar.gz
RUN tar -xvf go1.17.linux-amd64.tar.gz
RUN mv go /usr/local

ENV GOPATH=$HOME/work
ENV PATH=$PATH:/usr/local/go/bin:$GOPATH/bin

# Kubectl 

RUN curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl"
RUN install -o root -g root -m 0755 kubectl /usr/local/bin/kubectl

# # Kubeseal
RUN (cd /; GO111MODULE=on go install github.com/bitnami-labs/sealed-secrets/cmd/kubeseal@main)

# Workdir
WORKDIR /src

# Dependencies
COPY requirements.txt /src
RUN python3.8 -m pip install --upgrade pip
RUN python3.8 -m pip install -r requirements.txt

# Copy your .kube/config file
COPY kube/ /root/.kube

# Code
COPY seal_current_key.py /src

# Run
CMD [ "python3.8", "seal_current_key.py" ]
