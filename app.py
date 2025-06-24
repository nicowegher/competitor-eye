# --- IMPORTS NECESARIOS ---
from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import pandas as pd
import requests
import io
import os
from datetime import datetime
import firebase_admin
from firebase_admin import credentials, firestore
from google.cloud import storage
from dotenv import load_dotenv
import json

# --- CONFIGURACIÓN FLASK Y CORS ---
app = Flask(__name__)
CORS(app)  # CRÍTICO para Firebase Studio

# --- Cargar variables de entorno ---
load_dotenv()
GCS_BUCKET_NAME = os.environ.get('GCS_BUCKET_NAME')
GOOGLE_APPLICATION_CREDENTIALS = os.environ.get('GOOGLE_APPLICATION_CREDENTIALS')

# --- Inicializar Firebase Admin SDK ---
# Lee el JSON de la variable de entorno
firebase_creds = os.environ.get("FIREBASE_SERVICE_ACCOUNT")
if firebase_creds:
    cred_dict = json.loads(firebase_creds)
    cred = credentials.Certificate(cred_dict)
    firebase_admin.initialize_app(cred)
else:
    # Modo local, usa el archivo
    cred = credentials.Certificate("firebase_service_account.json")
    firebase_admin.initialize_app(cred)

db = firestore.client()
storage_client = storage.Client()
bucket = storage_client.bucket(GCS_BUCKET_NAME)

# --- FUNCIÓN DE CONEXIÓN A APIS EXTERNAS ---
def obtener_datos_externos():
    try:
        # Conectar a tu API externa aquí
        headers = {
            'Authorization': 'Bearer TU_TOKEN_AQUI',
            'Content-Type': 'application/json'
        }
        response = requests.get('TU_API_URL_AQUI', headers=headers)
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f"Error en API: {response.status_code}")
    except Exception as e:
        # Datos de ejemplo para testing
        return [
            {"id": 1, "nombre": "Dato de prueba 1", "fecha": datetime.now().isoformat()},
            {"id": 2, "nombre": "Dato de prueba 2", "fecha": datetime.now().isoformat()}
        ]

# --- ENDPOINT HEALTH CHECK ---
@app.route('/', methods=['GET'])
def health_check():
    return {"status": "Backend funcionando correctamente", "timestamp": datetime.now().isoformat()}

# --- ENDPOINT OBTENER DATOS JSON ---
@app.route('/datos', methods=['GET'])
def obtener_datos():
    try:
        datos = obtener_datos_externos()
        return {"success": True, "datos": datos, "total": len(datos)}
    except Exception as e:
        return {"error": str(e)}, 500

# --- ENDPOINT DESCARGAR CSV ---
@app.route('/descargar-csv', methods=['GET', 'POST'])
def descargar_csv():
    try:
        datos = obtener_datos_externos()
        df = pd.DataFrame(datos)
        csv_buffer = io.StringIO()
        df.to_csv(csv_buffer, index=False, encoding='utf-8')
        csv_buffer.seek(0)
        with open('temp_archivo.csv', 'w', encoding='utf-8') as f:
            f.write(csv_buffer.getvalue())
        return send_file('temp_archivo.csv', 
                        as_attachment=True, 
                        download_name=f'datos_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv',
                        mimetype='text/csv')
    except Exception as e:
        return {"error": str(e)}, 500

# --- ENDPOINT DESCARGAR EXCEL ---
@app.route('/descargar-excel', methods=['GET', 'POST'])
def descargar_excel():
    try:
        datos = obtener_datos_externos()
        df = pd.DataFrame(datos)
        excel_buffer = io.BytesIO()
        df.to_excel(excel_buffer, index=False, engine='openpyxl')
        excel_buffer.seek(0)
        return send_file(
            excel_buffer,
            as_attachment=True,
            download_name=f'datos_{datetime.now().strftime("%Y%m%d_%H%M%S")}.xlsx',
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
    except Exception as e:
        return {"error": str(e)}, 500

# --- ENDPOINT EXISTENTE DE SCRAPER (SE MANTIENE) ---
@app.route('/run-scraper', methods=['POST'])
def run_scraper():
    from apify_scraper import scrape_booking_data
    data = request.json
    # Validar campos obligatorios
    required_fields = ["taskId", "setName", "ownHotelUrl", "competitorHotelUrls", "daysToScrape", "userId"]
    for field in required_fields:
        if field not in data:
            return jsonify({"error": f"Falta el campo obligatorio: {field}"}), 400
    task_id = data["taskId"]
    set_name = data["setName"]
    own_hotel_url = data["ownHotelUrl"]
    competitor_hotel_urls = data["competitorHotelUrls"]
    days = data["daysToScrape"]
    user_id = data["userId"]
    all_urls = [own_hotel_url] + competitor_hotel_urls
    try:
        resultados = scrape_booking_data(all_urls, days)
        # Generar archivos CSV y XLSX
        df = pd.DataFrame(resultados)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        csv_filename = f"{task_id}_{timestamp}.csv"
        xlsx_filename = f"{task_id}_{timestamp}.xlsx"
        df.to_csv(csv_filename, index=False)
        df.to_excel(xlsx_filename, index=False)
        # Subir archivos a GCS
        blob_csv = bucket.blob(f"reports/{csv_filename}")
        blob_xlsx = bucket.blob(f"reports/{xlsx_filename}")
        blob_csv.upload_from_filename(csv_filename)
        blob_xlsx.upload_from_filename(xlsx_filename)
        # Hacer públicos los archivos (opcional, según reglas del bucket)
        blob_csv.make_public()
        blob_xlsx.make_public()
        csv_url = blob_csv.public_url
        xlsx_url = blob_xlsx.public_url
        # Actualizar Firestore
        doc_ref = db.collection("scraping_reports").document(task_id)
        doc_ref.update({
            "status": "completed",
            "completedAt": firestore.SERVER_TIMESTAMP,
            "csvFileUrl": csv_url,
            "xlsxFileUrl": xlsx_url
        })
        # Devolver respuesta al frontend
        return jsonify({
            "status": "completed",
            "completedAt": datetime.now().isoformat(),
            "csvFileUrl": csv_url,
            "xlsxFileUrl": xlsx_url
        })
    except Exception as e:
        # Actualizar Firestore con error
        doc_ref = db.collection("scraping_reports").document(task_id)
        doc_ref.update({
            "status": "failed",
            "completedAt": firestore.SERVER_TIMESTAMP,
            "error": str(e)
        })
        return jsonify({
            "status": "failed",
            "completedAt": datetime.now().isoformat(),
            "error": str(e)
        }), 500

# --- CONFIGURACIÓN PARA RENDER.COM ---
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port) 