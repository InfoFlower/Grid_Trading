select *
from {{ source('dmbte', 'e_market_data') }}