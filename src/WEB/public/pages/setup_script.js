

document.addEventListener('DOMContentLoaded', function() {
    const runBtn = document.getElementById('runBtn');
    const output = document.getElementById('output');
    
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

    runBtn.addEventListener('click', async function() {
        output.textContent = "Exécution en cours...";
        
        try {
            // Appel de l'API de votre serveur Express
            const response = await fetch('/run-script', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(config)  // Envoi de votre configuration
            });
            console.log("Appel envoyé:", response); // Debugging
            const data = await response.json();
            
            if (data.error) {
                output.textContent = "Erreur : " + data.error;
            } else {
                output.textContent = "Résultat :\n" + data.results;
            }
        } catch (err) {
            output.textContent = "Erreur réseau : " + err.message;
        }
    });
});





// // Construction de l'objet de configuration
// const config = {
//     DataStructure: {
//         TimeCol: document.getElementById('timeCol').value,
//         CloseCol: document.getElementById('closeCol').value,
//         LowCol: document.getElementById('lowCol').value,
//         HighCol: document.getElementById('highCol').value
//     },
//     GridOrders_params: {
//         qty: parseFloat(document.getElementById('qty').value),
//         leverage: parseInt(document.getElementById('leverage').value),
//         take_profit: parseFloat(document.getElementById('takeProfit').value),
//         stop_loss: parseFloat(document.getElementById('stopLoss').value),
//         justif: "init",
//         state: "open"
//     },
//     Grid_Metadata: {
//         prct_of_intervall: parseFloat(document.getElementById('prctInterval').value),
//         nb_orders: parseInt(document.getElementById('nbOrders').value)
//     },
//     money_balance: parseFloat(document.getElementById('moneyBalance').value),
//     time_4_epoch: parseInt(document.getElementById('timeEpoch').value)
// };
