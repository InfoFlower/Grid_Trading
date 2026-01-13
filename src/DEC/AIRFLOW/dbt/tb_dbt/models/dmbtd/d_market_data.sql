{{
    config(
        unique_key=['SYMBOL','OPEN_TIME']
    )
}}

select *
from {{ source('dmbtc', 'c_market_data') }}