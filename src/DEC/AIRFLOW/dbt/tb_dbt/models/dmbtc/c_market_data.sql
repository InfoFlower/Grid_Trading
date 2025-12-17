select *
    , '{{ run_started_at }}' as execution_timestamp
from {{ source('dmbte', 'e_market_data') }}