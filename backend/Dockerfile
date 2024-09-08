# FROM ubuntu:20.04
# # Setting non interactive env during installation
# ENV DEBIAN_FRONTEND=noninteractive

# RUN apt-get update && \
#     apt-get install -y \
#     python3.10 \
#     python3-pip \
#     texlive-full && \
#     apt-get clean 

# RUN update-alternatives --install /usr/bin/python python /usr/bin/python3.10 1 && \
#     update-alternatives --install /usr/bin/pip pip /usr/bin/pip3 1

# WORKDIR /app

# COPY requirements.txt . 

# RUN pip install --no-cache-dir -r requirements.txt

# COPY . . 

# EXPOSE 3000

FROM python:3.10

# the entire container dir will be 'app'
WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt && \
    apt-get update && \
    apt-get install -y texlive-full
	
COPY . . 
# expose port 3000 of container which will later be mapped for accessing from the user application
EXPOSE 3000

