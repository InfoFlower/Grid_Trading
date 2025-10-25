FROM quay.io/astronomer/astro-runtime:8.8.0
WORKDIR /usr/local/airflow
RUN python -m venv /usr/local/airflow/astro_venv
COPY requirements.txt . 
RUN /usr/local/airflow/astro_venv/bin/pip install --no-cache-dir -r requirements.txt

ENV PATH="/usr/local/airflow/astro_venv/bin:$PATH"