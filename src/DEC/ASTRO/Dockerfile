FROM astro_c15280/airflow:latest
WORKDIR /usr/local/airflow
RUN python -m venv /usr/local/airflow/astro_venv
# RUN python -m venv astro_venv && source astro_venv/bin/activate \
#     && pip install --no-cache-dir -r requirements.txt && deactivate
COPY requirements.txt . 
RUN /usr/local/airflow/astro_venv/bin/pip install --no-cache-dir -r requirements.txt

ENV PATH="/usr/local/airflow/astro_venv/bin:$PATH"

