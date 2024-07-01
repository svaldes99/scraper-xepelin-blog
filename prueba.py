import pygsheets


# spreadsheetId = '1LkprScAhdP0wKBxP2d5IabcTQhUryC8H-Zkq7Pi_lHY
# Escribir en el google sheets
# Lista falsa
news = [
    {
        "title": "Title 1",
        "category": "Category 1",
        "read_time": 5,
        "author": "Author 1"
    },
    {
        "title": "Title 2",
        "category": "Category 2",
        "read_time": 10,
        "author": "Author 2"
    },
    {
        "title": "Title 3",
        "category": "Category 3",
        "read_time": 15,
        "author": "Author 3"
    }
]

# Crear un cliente de Google Sheets
gc = pygsheets.authorize(service_file='./credentials.json')

# Abrir la hoja de cálculo
sh = gc.open_by_key('1LkprScAhdP0wKBxP2d5IabcTQhUryC8H-Zkq7Pi_lHY')

# Seleccionar la primera hoja
wks = sh[0]

# Obtener la lista de títulos de las columnas
columns = list(news[0].keys())

# Obtener la lista de valores de las filas
values = [list(news_item.values()) for news_item in news]

# Insertar los títulos de las columnas
wks.insert_rows(row=0, number=0, values=[columns])

# Insertar los valores de las filas
wks.insert_rows(row=1, number=len(values), values=values)

print("News details have been written to the Google Sheet.")
