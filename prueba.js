const { google } = require('googleapis');
const sheets = google.sheets('v4');
const fs = require('fs');

// Cargar las credenciales del archivo JSON
const credentials = JSON.parse(fs.readFileSync('./credentials.json'));

// Configurar la autenticación
const auth = new google.auth.GoogleAuth({
  credentials,
  scopes: ['https://www.googleapis.com/auth/spreadsheets']
});

// Lista falsa de noticias
const news = [
  {
    title: "Title 1",
    category: "Hola",
    read_time: 5,
    author: "Author 1"
  },
  {
    title: "Title 2",
    category: "Category 2",
    read_time: 10,
    author: "Author 2"
  },
  {
    title: "Title 3",
    category: "Category 3",
    read_time: 15,
    author: "Author 3"
  }
];

// ID de la hoja de cálculo
const spreadsheetId = '1LkprScAhdP0wKBxP2d5IabcTQhUryC8H-Zkq7Pi_lHY';

// Convertir la lista de noticias en filas
const columns = Object.keys(news[0]);
const values = news.map(item => Object.values(item));

// Añadir las cabeceras a las filas
values.unshift(columns);

// Función para escribir en la hoja de cálculo
async function writeToSheet() {
  const client = await auth.getClient();
  const request = {
    spreadsheetId,
    range: 'Hoja 1!A1', // Asegúrate de que la hoja se llama "Sheet1" y el rango es correcto
    valueInputOption: 'RAW',
    resource: {
      values
    },
    auth: client
  };

  try {
    const response = await sheets.spreadsheets.values.update(request);
    console.log('News details have been written to the Google Sheet.');
  } catch (error) {
    console.error('Error writing to the Google Sheet:', error.errors[0].message);
  }
}

writeToSheet();
