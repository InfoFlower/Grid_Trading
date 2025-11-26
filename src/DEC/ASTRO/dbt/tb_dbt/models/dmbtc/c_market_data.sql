select *
    , current_timestamp
from {{ source('dmbte', 'e_market_data') }}