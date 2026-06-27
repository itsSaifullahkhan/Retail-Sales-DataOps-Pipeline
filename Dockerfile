FROM spark:3.5.1-python3

USER root

WORKDIR /app

RUN python3 -m pip install --no-cache-dir requests==2.32.3 pytest==8.2.2

COPY . .

CMD ["bash", "-lc", "python3 src/ingestion/fetch_carts_api.py && /opt/spark/bin/spark-submit src/jobs/transform_orders.py"]