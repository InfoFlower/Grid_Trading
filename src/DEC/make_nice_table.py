drop table DTM_GridTrading.to_collect_processing ;
create table DTM_GridTrading.to_collect_processing as (
	select open.id,open.timestamp, 
		open.qty, 
        open.entryprice, 
        close.close_price, 
        close.justif,
        open.crypto_balance as Open_crypto_balance,
        close.crypto_balance as Close_crypto_balance,
        open.money_balance as Open_money_balance,
        close.money_balance as Close_money_balance,
        open.signe_buy*(close.close_price - open.entryprice)*open.qty as profit_loss
from DTM_GridTrading.eq_position_hist close
join DTM_GridTrading.eq_position_hist open on open.id=close.id
and close.state='Closing'
and open.state='Opening');

select justif,avg(profit_loss)
from DTM_GridTrading.to_collect_processing 
group by 1;