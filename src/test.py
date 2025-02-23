from datetime import datetime
import polars as pl
from matplotlib import pyplot as plt
data=pl.read_csv(f'data\OPE_DATA\DATA_RAW_S_ORIGIN_test_code\data_raw_BTCUSDT_{152}.csv', truncate_ragged_lines=True)
for i in range(153,159):
    data_b =pl.read_csv(f'data\OPE_DATA\DATA_RAW_S_ORIGIN_test_code\data_raw_BTCUSDT_{i}.csv', truncate_ragged_lines=True)
    print(i)
    data=pl.concat([data,data_b])
print(len(data))
plt.plot(data['Close time'],data['Close'])
plt.show()