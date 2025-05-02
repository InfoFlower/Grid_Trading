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
    const progressBar = document.getElementById('progress-bar');
    // Launch backtest
    console.log('socket_opening')
    const socket = new io();
    socket.on('connect', () => {
        console.log("Connected to server");  // Log when connected successfully
        
    });
    socket.on('message',(message)=>{
        data = message
        output.textContent = data.message;
    });
    socket.on('progress',(progress)=>{
        data = progress
        progressBar.style.width = `${data.value}%`;
    });
    socket.on('close',(data) =>{
        console.log(data)
        addOutputLine('Success')
        progressBar.style.backgroundColor = 'green';
        document.querySelector('.btn-secondary').classList.remove('hidden');
        socket.disconnect();
    });
    document.getElementById('runBtn').addEventListener('click', async () => {
        const output = document.getElementById('output');
        progressBar.style.width = '1%';
        progressBar.style.backgroundColor = 'blue';
        output.textContent = 'Initiating backtest...';
        const config = {
            DataFile : document.getElementById('datafile').value,
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
        console.log('sending request')
        socket.emit('start_backtest',config)
    });
    document.getElementById('viewResultsBtn').addEventListener('click', async () => {
        await fetch(`/put_data/datafile/${document.getElementById('datafile').value}`);
        window.location.href = '/public/reporting_page.html';
    });
});

