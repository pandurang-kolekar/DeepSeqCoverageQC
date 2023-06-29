# syntax=docker/dockerfile:1

################## BASE IMAGE #############################
FROM python:3.9-slim-buster

################## METADATA ###############################
LABEL "org.opencontainers.image.title"="DeepSeqCoverageQC"
LABEL "org.opencontainers.image.description"="Compute coverage QC metrics for deep targeted sequencing data"
LABEL "org.opencontainers.image.version"="0.1.0"
LABEL "org.opencontainers.image.base.name"="python:3.9-slim-buster"
LABEL "org.opencontainers.image.url"="https://github.com/pandurang-kolekar/panelQC"
LABEL "org.opencontainers.image.licenses"="Apache License, Version 2.0"
LABEL "about.tags"="NGS BAM panel coverage QC depth targeted sequencing"
LABEL "org.opencontainers.image.authors"="Pandurang Kolekar <pandurang.kolekar@gmail.com>"

################## INSTALLATION ###########################
WORKDIR /DeepSeqCoverageQC
COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt
COPY . .
RUN pip3 install -e .
ENTRYPOINT ["DeepSeqCoverageQC"]
