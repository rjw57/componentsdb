FROM python:3.12
WORKDIR /usr/src
RUN pip install poetry~=1.8 poetry-plugin-export~=1.8
COPY poetry.lock pyproject.toml .
RUN \
  poetry export -f requirements.txt --output /tmp/requirements.txt && \
  pip install -r /tmp/requirements.txt && \
  rm /tmp/requirements.txt
COPY ./ ./
RUN pip install -e .
ENTRYPOINT ["componentsdb"]
