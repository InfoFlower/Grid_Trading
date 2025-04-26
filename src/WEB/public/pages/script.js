

document.addEventListener('DOMContentLoaded', function() {
    const runBtn = document.getElementById('runBtn');
    const output = document.getElementById('output');
    
    runBtn.addEventListener('click', function() {
        // Construction de l'objet de configuration
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

        // Affichage dans la console
        output.textContent = "Configuration envoyée :\n" + JSON.stringify(config, null, 2);
        
        // Appel du script Python via Electron (si vous utilisez Electron)
        if (typeof require !== 'undefined') {
            const { spawn } = require('child_process');
            const pythonProcess = spawn('python', [
                '../../../main.py',
                JSON.stringify(config)
            ]);

            pythonProcess.stdout.on('data', (data) => {
                output.textContent += "\n\nSortie Python:\n" + data.toString();
            });

            pythonProcess.stderr.on('data', (data) => {
                output.textContent += "\n\nErreur Python:\n" + data.toString();
            });

            pythonProcess.on('close', (code) => {
                output.textContent += "\n\nProcessus terminé avec code: " + code;
            });
        } else {
            output.textContent += "\n\nErreur: L'environnement Node.js n'est pas disponible";
        }
    });
});