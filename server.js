const express = require('express');
const { spawn } = require('child_process');
const fs = require('fs');
const axios = require('axios');

const app = express();
app.use(express.json());
require('dotenv').config();

// Ruta POST para iniciar el scraping y procesar los datos
app.post('/scrape', async (req, res) => {
  const { category, webhookUrl } = req.body;

  if (!category || !webhookUrl) {
    return res.status(400).send('Missing category or webhookUrl');
  }

  console.log(`Scraping data for category: ${category}`);

  const pythonProcess = spawn('python3', ['scraper.py', category]);

  let scrapedDataString = '';

  pythonProcess.stdout.on('data', (data) => {
    scrapedDataString += data.toString();
    console.log(`Python stdout: ${data.toString()}`);
  });

  pythonProcess.stdout.on('end', async () => {
    try {
      // Leer el email desde .env
      const email = process.env.EMAIL;

      // ID de la hoja de cálculo de .env
      const spreadsheetId = process.env.SPREADSHEET_ID;



      // Enlace de Google Sheets
      const googleSheetsLink = `https://docs.google.com/spreadsheets/d/${spreadsheetId}`;


      // Enviar solicitud al webhook indicando el link del Google Sheets y el email  en el body y content-type application/json
        await axios.post(webhookUrl, {
            'email': email,
            'link': googleSheetsLink,
        }, {
            headers: {
                'Content-Type': 'application/json'
            }
        });

      console.log('Webhook request sent with Google Sheets link:', googleSheetsLink);
      res.status(200).send('Scraping completed and webhook request sent');
    } catch (error) {
      console.error('Error sending webhook request:', error.message);
      res.status(500).send(`Error sending webhook request: ${error.message}`);
    }
  });

  pythonProcess.stderr.on('data', (data) => {
    console.error(`Error running scraper: ${data.toString()}`);
    res.status(500).send(`Error running scraper: ${data.toString()}`);
  });

  pythonProcess.on('exit', (code) => {
    console.log(`Python process exited with code ${code}`);
  });
});

const PORT = process.env.PORT || 3000;
app.listen(PORT, () => {
  console.log(`Server is running on port ${PORT}`);
});
