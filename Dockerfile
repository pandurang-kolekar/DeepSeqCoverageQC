# syntax=docker/dockerfile:1

################## BASE IMAGE #############################
FROM python:3.9-slim-buster

################## METADATA ###############################
LABEL "org.opencontainers.image.title"="DeepSeqCoverageQC"
LABEL "org.opencontainers.image.description"="Compute coverage QC metrics for deep targeted sequencing data"
LABEL "org.opencontainers.image.version"="0.3.3"
LABEL "org.opencontainers.image.base.name"="python:3.9-slim-buster"
LABEL "org.opencontainers.image.url"="https://github.com/pandurang-kolekar/DeepSeqCoverageQC"
LABEL "org.opencontainers.image.licenses"="Apache License, Version 2.0"
LABEL "about.tags"="NGS BAM panel coverage QC depth targeted sequencing"
LABEL "org.opencontainers.image.authors"="Pandurang Kolekar <pandurang.kolekar@gmail.com>"

################## INSTALLATION ###########################

RUN pip3 install deepseqcoverageqc
ENV PATH=${PATH}:/usr/local/bin/
