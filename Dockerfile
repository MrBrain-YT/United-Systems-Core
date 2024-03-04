FROM python:3.12
EXPOSE 5000

COPY . ./USC
RUN pip install -r ./USC/requirements.txt
WORKDIR /USC/USC


ENTRYPOINT /bin/sh -c bash