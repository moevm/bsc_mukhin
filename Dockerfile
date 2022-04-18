FROM python:3.9-slim
WORKDIR /zoom

COPY . ./

RUN pip install -r requirements.txt
RUN playwright install webkit chromium
