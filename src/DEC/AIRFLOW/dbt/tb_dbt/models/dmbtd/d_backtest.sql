{{
    config(
        unique_key='BACKTEST_ID'
    )
}}

select *
from {{ source('dmbtc', 'c_backtest') }}