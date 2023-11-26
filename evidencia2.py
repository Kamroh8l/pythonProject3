import streamlit as st
import requests
import mysql.connector
import os

@st.cache
def obtener_datos_desde_api(api_url):
    response = requests.get(api_url)
    if response.status_code == 200:
        return response.json()
    else:
        st.error(f"Error al obtener datos de la API. Código de estado: {response.status_code}")
        return None

@st.cache
def conectar_base_de_datos():
    # Configuración de la base de datos desde variables de entorno
    db_config = {
        'host': os.environ.get('DB_HOST'),
        'user': os.environ.get('DB_USER'),
        'password': os.environ.get('DB_PASSWORD'),
        'database': os.environ.get('DB_NAME')
    }

    return mysql.connector.connect(**db_config)

def crear_tabla_si_no_existe(conn):
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS stands (
            id INT PRIMARY KEY,
            name VARCHAR(255),
            alternateName VARCHAR(255),
            japaneseName VARCHAR(255),
            image VARCHAR(255),
            standUser VARCHAR(255),
            chapter VARCHAR(255),
            abilities TEXT,
            battlecry TEXT
        )
    ''')

@st.cache
def insertar_datos_en_db(conn, data):
    cursor = conn.cursor()
    for stand in data:
        cursor.execute('''
            INSERT IGNORE INTO stands (id, name, alternateName, japaneseName, image, standUser, chapter, abilities, battlecry)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        ''', (
            stand.get("id"), stand.get("name"), stand.get("alternateName"),
            stand.get("japaneseName"), stand.get("image"), stand.get("standUser"),
            stand.get("chapter"), stand.get("abilities"), stand.get("battlecry")
        ))
    conn.commit()

def main():
    # URL de la API
    api_url = "https://stand-by-me.herokuapp.com/api/v1/stands"

    # Obtener datos desde la API
    data = obtener_datos_desde_api(api_url)

    if data is not None:
        # Mostrar los datos en la aplicación Streamlit
        st.title("Datos de Stands")
        st.table(data)

        # Conectar a la base de datos MySQL
        conn = conectar_base_de_datos()

        # Crear tabla si no existe
        crear_tabla_si_no_existe(conn)

        # Insertar datos en la tabla evitando duplicados
        insertar_datos_en_db(conn, data)

        # Cerrar la conexión
        conn.close()

        st.success("Datos exportados a la base de datos MySQL con éxito.")

if __name__ == "__main__":
    main()
