FROM astrocrpublic.azurecr.io/runtime:3.0-5
WORKDIR "/usr/local/airflow"
RUN python -m venv astro_venv && source astro_venv/bin/activate \
    && pip install --no-cache-dir -r requirements.txt && deactivate