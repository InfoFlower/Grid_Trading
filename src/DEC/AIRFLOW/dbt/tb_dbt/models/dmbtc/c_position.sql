select *
    , '{{ run_started_at }}' as execution_timestamp
    , '{{ invocation_id }}' as invocation_id
from {{ source('dmbte', 'e_position') }}