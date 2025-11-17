FROM astrocrpublic.azurecr.io/runtime:3.1-5
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

RUN python -m venv dbt_venv && source dbt_venv/bin/activate && \
    pip install --no-cache-dir dbt-postgres && deactivate