FROM python:3.8-buster
ARG pyrs990_version
VOLUME /data/
RUN pip install pyrs990==$pyrs990_version
RUN pyrs990 --help
ENTRYPOINT ["pyrs990"]
