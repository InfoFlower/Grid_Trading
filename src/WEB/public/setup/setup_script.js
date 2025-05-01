function addOutputLine(message, type = 'info') {
    const line = document.createElement('div');
    line.className = `output-line status-${type}`;
    line.textContent = message;
    
    const output = document.getElementById('output');
    output.prepend(line);
    
    // Keep only 20 lines
    while (output.children.length > 20) {
        output.removeChild(output.lastChild);
    }
}

document.addEventListener('DOMContentLoaded', function() {
    document.getElementById('runBtn').addEventListener('click', async () => {
        const progressBar = document.getElementById('progress-bar');
        const output = document.getElementById('output');
        progressBar.style.width = '100%';
        progressBar.style.backgroundColor = 'blue';
        output.textContent = 'Starting backtest...';

        const config = {
            DataStructure: {
                TimeCol: document.getElementById('timeCol').value,
                CloseCol: document.getElementById('closeCol').value,
                LowCol: document.getElementById('lowCol').value,
                HighCol: document.getElementById('highCol').value
            },
            GridOrders_params: {
                qty: parseFloat(document.getElementById('qty').value),
                leverage: parseInt(document.getElementById('leverage').value),
                take_profit: parseFloat(document.getElementById('takeProfit').value),
                stop_loss: parseFloat(document.getElementById('stopLoss').value),
                justif: "init",
                state: "open"
            },
            Grid_Metadata: {
                prct_of_intervall: parseFloat(document.getElementById('prctInterval').value),
                nb_orders: parseInt(document.getElementById('nbOrders').value)
            },
            money_balance: parseFloat(document.getElementById('moneyBalance').value),
            time_4_epoch: parseInt(document.getElementById('timeEpoch').value)
        };

        // Launch backtest
        try {
            const response = await fetch('/LaunchBacktest', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(config)  // Your config object
            });
            const resultText = await response.json(); 
    
            addOutputLine(resultText.message,'Success')
            progressBar.style.backgroundColor = 'green';
            document.getElementById('viewResultsBtn').classList.remove('hidden');
        } catch (err) {
            addOutputLine(err.message, 'Error');
            progressBar.style.backgroundColor = 'red';
        }
    });
    document.getElementById('viewResultsBtn').addEventListener('click', async () => {
        window.location.href = '/public/reporting_page.html';
    });
});