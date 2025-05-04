function addOutputLine(message, type = 'info') {
    const line = document.createElement('div');
    line.className = `output-line status-${type}`;
    line.textContent = message;
    
    const output = document.getElementById('output');
    output.prepend(line);
    
    // Keep only 20 lines
    while (output.children.length > 5) {
        output.removeChild(output.lastChild);
    }
};

function sleep(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
}

document.addEventListener('DOMContentLoaded', function() {
    document.getElementById('runBtn').disabled = false;
    document.getElementById('runBtn').classList.remove('disabled');
    const progressBar = document.getElementById('progress-bar');
    
    document.getElementById('runBtn').addEventListener('click', async () => {
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
        const output = document.getElementById('output');
        const request = {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(config)
          };
    
        progressBar.style.width = '1%';
        progressBar.style.backgroundColor = 'blue';
        output.textContent = 'Initiating backtest...';
        console.log('sending request')
        const response = await fetch('/LaunchBacktest',request)
        current_uuid = response.uuid
        console.log(response)
        const progress = 0
        function get_progress(){
            const progress = fetch(`/get_data/${current_uuid}_status`);
            data = progress;
            console.log(data)
            progressBar.style.width = `${data.status}%`;
            return data.status
        }
        while (progress!=100){
            progress =  get_progress();
            await sleep(1000);
            }
        
        // console.log(data)
        // addOutputLine('Success')
        // progressBar.style.backgroundColor = 'green';
        // document.querySelector('.btn-secondary').classList.remove('hidden');
        // document.getElementById('runBtn').disabled = false;
        // document.getElementById('runBtn').classList.remove('disabled');
        // document.getElementById('runBtn').disabled = true;
        // document.getElementById('runBtn').classList.add('disabled');
    });
    document.getElementById('viewResultsBtn').addEventListener('click', async () => {
        await fetch(`/put_data/datafile/${document.getElementById('datafile').value}`);
        window.location.href = '/public/reporting_page.html';
    });
});

