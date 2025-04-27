const express = require('express');
const { spawn } = require('child_process');
const path = require('path');
const fs = require('fs'); // Ajout pour vérifier l'existence des fichiers

const app = express();
const port = 3000;
const publicDir = path.join(__dirname, 'public');
const pythonScript = path.resolve(__dirname, '../../DebugMain.py');

// Vérification des chemins au démarrage
if (!fs.existsSync(publicDir)) {
  console.error(`ERREUR: Le dossier public n'existe pas: ${publicDir}`);
  process.exit(1);
}

if (!fs.existsSync(pythonScript)) {
  console.error(`ERREUR: Le script Python n'existe pas: ${pythonScript}`);
  process.exit(1);
}

// Middleware
app.use(express.json());
app.use(express.static(publicDir));

// Routes
app.get('/', (req, res) => {
  const indexPath = path.join(publicDir, 'index.html');
  
  if (!fs.existsSync(indexPath)) {
    return res.status(500).json({ 
      error: 'Fichier index.html introuvable',
      path: indexPath
    });
  }
  
  res.sendFile(indexPath);
});

app.post('/run-script', (req, res) => {
  try {
    const pythonProcess = spawn('python', [pythonScript]);
    
    console.log(`Exécution du script: ${pythonScript}`);
    console.log(`PID du processus: ${pythonProcess.pid}`);

    let output = '';
    let errorOutput = '';

    pythonProcess.stdout.on('data', (data) => {
      output += data.toString();
      console.log(`[Python stdout] ${data.toString().trim()}`);
    });

    pythonProcess.stderr.on('data', (data) => {
      errorOutput += data.toString();
      console.error(`[Python stderr] ${data.toString().trim()}`);
    });

    pythonProcess.on('error', (err) => {
      console.error('Erreur du processus Python:', err);
      res.status(500).json({
        error: 'Échec du lancement du script Python',
        details: err.message
      });
    });

    pythonProcess.on('close', (code) => {
      console.log(`Script terminé avec code ${code}`);
      if (code !== 0) {
        return res.status(500).json({
          error: 'Erreur dans le script Python',
          exitCode: code,
          errorOutput: errorOutput.trim()
        });
      }
      res.json({ 
        success: true,
        output: output.trim() 
      });
    });

    // Envoyer les données d'entrée au processus Python si nécessaire
    if (req.body) {
      pythonProcess.stdin.write(JSON.stringify(req.body));
      pythonProcess.stdin.end();
    }

  } catch (err) {
    console.error('Erreur serveur:', err);
    res.status(500).json({
      error: 'Erreur interne du serveur',
      details: err.message
    });
  }
});

// Démarrer le serveur
app.listen(port, () => {
  console.log(`Serveur démarré sur http://localhost:${port}`);
  console.log(`Dossier public: ${publicDir}`);
  console.log(`Script Python: ${pythonScript}`);
});