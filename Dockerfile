from python:3.10-alpine

COPY operator.py /
COPY requirements.txt /

RUN pip install --no-cache-dir install -r requirements.txt && \
    rm -rf requirements.txt

ENTRYPOINT ["kopf", "run", "/operator.py"]