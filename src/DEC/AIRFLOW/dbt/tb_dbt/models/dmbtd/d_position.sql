{{
    config(
        unique_key=['BACKTEST_ID','POSITION_ID', 'POSITION_EVENT_TIMESTAMP','POSITION_EVENT_TYPE']
    )
}}

select *
from {{ source('dmbtc', 'c_position') }}