fetch('/full_graph')
  .then(response => response.json())
  .then(data => {
    const times = data.prices.map(p => p.Time);
    const prices = data.prices.map(p => p.Close);

    const priceTrace = {
      x: times,
      y: prices,
      type: 'scatter',
      mode: 'lines',
      name: 'Close Price',
      line: { color: 'white' }
    };

    const buyOrders = data.orders.filter(o => o.OrderType === "BUY");
    const sellOrders = data.orders.filter(o => o.OrderType === "SELL");

    const buyTrace = {
      x: buyOrders.map(o => o.OrderTime),
      y: buyOrders.map(o => o.OrderPrice),
      mode: 'markers',
      name: 'BUY',
      marker: { color: 'green', size: 8, symbol: 'circle' },
      type: 'scatter'
    };

    const sellTrace = {
      x: sellOrders.map(o => o.OrderTime),
      y: sellOrders.map(o => o.OrderPrice),
      mode: 'markers',
      name: 'SELL',
      marker: { color: 'red', size: 8, symbol: 'diamond' },
      type: 'scatter'
    };

    const entries = data.positions.filter(p => p.EventCode.includes("OPEN"));
    const exits = data.positions.filter(p => p.EventCode.includes("STOPLOSS"));

    const entryTrace = {
      x: entries.map(p => p.EventData_Time),
      y: entries.map(p => p.PositionEntryPrice),
      mode: 'markers',
      name: 'Entry',
      marker: { color: 'blue', size: 6, symbol: 'triangle-up' },
      type: 'scatter'
    };

    const exitTrace = {
      x: exits.map(p => p.EventData_Time),
      y: exits.map(p => p.PositionClosePrice),
      mode: 'markers',
      name: 'Exit',
      marker: { color: 'yellow', size: 6, symbol: 'triangle-down' },
      type: 'scatter'
    };

    const layout = {
      paper_bgcolor: '#121212',
      plot_bgcolor: '#1e1e1e',
      font: { color: 'white' },
      title: 'BTCUSDT Backtest Visualization',
      xaxis: { title: 'Time' },
      yaxis: { title: 'Price' },
      margin: { t: 50 }
    };

    Plotly.newPlot('chart', [priceTrace, buyTrace, sellTrace, entryTrace, exitTrace], layout, { responsive: true });
  });
