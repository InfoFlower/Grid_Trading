import polars as pl
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import os
from dotenv import load_dotenv
load_dotenv()
WD = os.getenv('WD')
data_file = 'data_raw_BTCUSDT_175.csv'

if len(data_file.split('_'))>3:
    data_file = WD + 'data/OPE_DATA/DATA_RAW_S_ORIGIN_test_code/' + data_file
else :
    data_file = WD + 'data/DATA_RAW_S_ORIGIN/' + data_file

# Load price data with Polars
price_df = pl.read_csv(data_file,truncate_ragged_lines=True)
price_df = price_df.with_columns([
    pl.col("Open time").cast(pl.Datetime).alias("Time")  # Convert time from milliseconds to datetime
])

# Load order data with Polars
orders_df = pl.read_csv('src/OPE/reporting/data_logger/Order.csv')
orders_df = orders_df.with_columns([
    pl.col("OrderTime").cast(pl.Datetime).alias("OrderTime")  # Convert time to datetime
])

# Load position data with Polars
positions_df = pl.read_csv('src/OPE/reporting/data_logger/Position.csv')
positions_df = positions_df.with_columns([
    pl.col("EventData_Time").cast(pl.Datetime).alias("EventData_Time")  # Convert time to datetime
])

# Convert price_df to Pandas for easier plotting
price_df_pd = price_df.to_pandas()

# Create plot with a dark background (Binance-like style)
plt.style.use('dark_background')  # Use dark background theme for the chart

# Create figure and axis
fig, ax = plt.subplots(figsize=(12, 6))

# Plot the price data (Close price)
ax.plot(price_df_pd["Time"], price_df_pd["Close"], label="Close Price", color="white", lw=1.5)

# Plot the order events (BUY and SELL)
for order in orders_df.to_dicts():
    if order["OrderType"] == "BUY":
        ax.plot(order["OrderTime"], order["OrderPrice"], 'go', markersize=7, label=f'BUY {order["OrderPrice"]}')
    elif order["OrderType"] == "SELL":
        ax.plot(order["OrderTime"], order["OrderPrice"], 'ro', markersize=7, label=f'SELL {order["OrderPrice"]}')

# Plot positions (Entry and Close prices)
for position in positions_df.to_dicts():
    if position["EventCode"] == "OPEN SELL":
        ax.plot(position["EventData_Time"], position["PositionEntryPrice"], 'bo', markersize=7, label=f'Entry {position["PositionEntryPrice"]}')
    if position["EventCode"] == "STOPLOSS SELL":
        ax.plot(position["EventData_Time"], position["PositionClosePrice"], 'yo', markersize=7, label=f'Exit {position["PositionClosePrice"]}')

# Format the x-axis with time
ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d %H:%M:%S'))
ax.xaxis.set_major_locator(mdates.HourLocator(interval=1))
plt.xticks(rotation=45)

# Customize grid and background
ax.grid(True, which='both', linestyle='--', linewidth=0.5, color='gray')
fig.patch.set_facecolor('#2b2b2b')  # Dark background color
ax.set_facecolor('#1e1e1e')  # Dark plot area

# Labels and title
ax.set_title("Price, Orders, and Positions over Time", fontsize=14, color='white')
ax.set_xlabel("Time", fontsize=12, color='white')
ax.set_ylabel("Price", fontsize=12, color='white')

# Adding a legend
ax.legend(loc="upper left", fontsize=10)

# Save the plot as an SVG
plt.tight_layout()

# Display the plot
plt.show()