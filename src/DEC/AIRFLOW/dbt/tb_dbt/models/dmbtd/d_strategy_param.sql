{{
    config(
        unique_key=['BACKTEST_ID','PARAM_ID']
    )
}}

select *
from {{ source('dmbtc', 'c_strategy_param') }}