select *
    , '{{ run_started_at }}'::timestamp as execution_timestamp
    , '{{ invocation_id }}' as invocation_id
from {{ source('dmbte', 'e_order') }}