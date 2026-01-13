{{
    config(
        unique_key=['BACKTEST_ID','ORDER_ID', 'ORDER_EVENT_TIMESTAMP','ORDER_EVENT_TYPE']
    )
}}

select *
from {{ source('dmbtc', 'c_order') }}