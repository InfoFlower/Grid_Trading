const express = require('express');
const { PythonShell } = require('python-shell');
const path = require('path');
const app = express();
const port = 3000;

// Configuration des chemins
const PYTHON_SCRIPT_PATH = path.join(__dirname, '..', '..', 'main.py');
const PUBLIC_DIR = path.join(__dirname, 'public');
const INDEX_PAGE = path.join(PUBLIC_DIR, 'index.html');

// Middleware
app.use(express.json());
app.use(express.static(PUBLIC_DIR));

// Route par défaut - Redirige vers setup.html
app.get('/', (req, res) => {
    res.sendFile(INDEX_PAGE);
});


// Route pour exécuter le script Python
app.post('/run-script', (req, res) => {
    const options = {
        mode: 'text',
        pythonPath: 'python3', // ou 'python' selon votre système
        pythonOptions: ['-u'], // Sortie non bufferisée
        args: [JSON.stringify(req.body)]
    };

    // Vérification que le fichier Python existe
    const fs = require('fs');
    if (!fs.existsSync(PYTHON_SCRIPT_PATH)) {
        return res.status(404).json({ 
            error: 'Script Python introuvable',
            path: PYTHON_SCRIPT_PATH
        });
    }

    PythonShell.run(PYTHON_SCRIPT_PATH, options, (err, results) => {
        if (err) {
            console.error('Erreur Python:', err);
            return res.status(500).json({ 
                error: err.message,
                stack: err.stack
            });
        }
        
        // Envoi des résultats avec le chemin exécuté pour debug
        res.json({
            results,
            executedScript: PYTHON_SCRIPT_PATH,
            indexPage: INDEX_PAGE
        });
    });
});

// Route de test
app.get('/test', (req, res) => {
    res.json({
        status: 'OK',
        indexPage: INDEX_PAGE,
        pythonScriptPath: PYTHON_SCRIPT_PATH,
        publicDir: PUBLIC_DIR,
        currentDir: __dirname
    });
});

// Gestion des erreurs 404
app.use((req, res) => {
    res.status(404).send('Endpoint non trouvé');
});

// Gestion des erreurs serveur
app.use((err, req, res, next) => {
    console.error(err.stack);
    res.status(500).send('Erreur interne du serveur');
});

// Démarrer le serveur
app.listen(port, () => {
    console.log(`Serveur démarré sur http://localhost:${port}`);
    console.log(`Script Python: ${PYTHON_SCRIPT_PATH}`);
    console.log(`Dossier public: ${PUBLIC_DIR}`);
    console.log(`Script Python: ${INDEX_PAGE}`);
});