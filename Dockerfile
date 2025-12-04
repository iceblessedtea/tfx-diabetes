FROM quay.io/astronomer/astro-runtime:8.0.0

RUN pip config set global.index-url https://pypi.org/simple

RUN pip install --no-cache-dir \
    tfx==1.24.0 \
    tensorflow==2.11.0 \
    tensorflow-transform \
    tfx-bsl \
    apache-beam[gcp]==2.53.0
