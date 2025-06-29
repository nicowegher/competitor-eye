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
from google.oauth2 import service_account
import threading
import logging

# --- CONFIGURACIÓN DE LOGGING ---
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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
    gcs_credentials = service_account.Credentials.from_service_account_info(cred_dict)
    storage_client = storage.Client(credentials=gcs_credentials, project=cred_dict.get("project_id"))
else:
    # Modo local, usa el archivo
    cred = credentials.Certificate("firebase_service_account.json")
    firebase_admin.initialize_app(cred)
    storage_client = storage.Client()

db = firestore.client()
bucket = storage_client.bucket(GCS_BUCKET_NAME)

# --- VARIABLE GLOBAL PARA EL ESTADO DEL SCRAPER ---
scraper_status = {
    "is_running": False,
    "progress": 0,
    "total_tasks": 0,
    "completed_tasks": 0,
    "error": None,
    "result": None
}

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

# --- FUNCIÓN ASÍNCRONA PARA EL SCRAPER ---
def run_scraper_async(hotel_base_urls, days, taskId):
    global scraper_status
    try:
        logger.info("Iniciando scraper asíncrono")
        scraper_status["is_running"] = True
        scraper_status["error"] = None
        scraper_status["progress"] = 0
        
        from apify_scraper import scrape_booking_data
        
        # Actualizar Firestore con estado inicial usando taskId
        doc_ref = db.collection("scraping_reports").document(taskId)
        doc_ref.update({
            "status": "running",
            "startedAt": datetime.now(),
            "hotels": len(hotel_base_urls),
            "days": days
        })
        
        # Ejecutar scraper
        logger.info(f"Ejecutando scraper para {len(hotel_base_urls)} hoteles por {days} días")
        result = scrape_booking_data(hotel_base_urls, days)
        
        if not result:
            raise Exception("No se obtuvieron datos del scraper")
        
        # Generar archivos
        df = pd.DataFrame(result)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        csv_filename = f"run-scraper_{timestamp}.csv"
        xlsx_filename = f"run-scraper_{timestamp}.xlsx"
        
        # Guardar archivos localmente
        df.to_csv(csv_filename, index=False)
        df.to_excel(xlsx_filename, index=False)
        
        # Subir a GCS
        blob_csv = bucket.blob(f"reports/{csv_filename}")
        blob_xlsx = bucket.blob(f"reports/{xlsx_filename}")
        blob_csv.upload_from_filename(csv_filename)
        blob_xlsx.upload_from_filename(xlsx_filename)
        
        # Hacer públicos
        blob_csv.make_public()
        blob_xlsx.make_public()
        csv_url = blob_csv.public_url
        xlsx_url = blob_xlsx.public_url
        
        # Limpiar archivos locales
        os.remove(csv_filename)
        os.remove(xlsx_filename)
        
        # Actualizar Firestore con éxito usando taskId
        doc_ref.update({
            "status": "completed",
            "completedAt": datetime.now(),
            "csvFileUrl": csv_url,
            "xlsxFileUrl": xlsx_url,
            "totalRecords": len(result)
        })
        
        # Actualizar estado global
        scraper_status["is_running"] = False
        scraper_status["progress"] = 100
        scraper_status["result"] = {
            "csvFileUrl": csv_url,
            "xlsxFileUrl": xlsx_url,
            "totalRecords": len(result)
        }
        
        logger.info("Scraper completado exitosamente")
        
    except Exception as e:
        logger.error(f"Error en scraper asíncrono: {str(e)}")
        scraper_status["is_running"] = False
        scraper_status["error"] = str(e)
        
        # Actualizar Firestore con error usando taskId
        doc_ref = db.collection("scraping_reports").document(taskId)
        doc_ref.update({
            "status": "failed",
            "completedAt": datetime.now(),
            "error": str(e)
        })

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

# --- ENDPOINT MEJORADO DE SCRAPER ---
@app.route('/run-scraper', methods=['POST'])
def run_scraper():
    global scraper_status
    
    try:
        data = request.get_json()
        taskId = data.get("taskId")
        if not taskId:
            return jsonify({"error": "taskId is required"}), 400
        
        hotel_base_urls = [data["ownHotelUrl"]] + data["competitorHotelUrls"]
        days = data.get("daysToScrape", 2)
        
        # Verificar si ya hay un scraper ejecutándose
        if scraper_status["is_running"]:
            return jsonify({
                "status": "already_running",
                "message": "Ya hay un scraper ejecutándose"
            }), 409
        
        # Iniciar scraper en un hilo separado, pasando el taskId
        thread = threading.Thread(
            target=run_scraper_async,
            args=(hotel_base_urls, days, taskId)
        )
        thread.daemon = True
        thread.start()
        
        return jsonify({
            "status": "started",
            "message": "Scraper iniciado correctamente",
            "hotels": len(hotel_base_urls),
            "days": days,
            "taskId": taskId
        })
        
    except Exception as e:
        logger.error(f"Error al iniciar scraper: {str(e)}")
        return jsonify({"error": str(e)}), 500

# --- ENDPOINT PARA VERIFICAR ESTADO DEL SCRAPER ---
@app.route('/scraper-status', methods=['GET'])
def get_scraper_status():
    global scraper_status
    return jsonify(scraper_status)

# --- CONFIGURACIÓN PARA RENDER.COM ---
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port) 