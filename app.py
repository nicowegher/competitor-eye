# --- IMPORTS NECESARIOS ---
from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import pandas as pd
import requests
import io
import os
from datetime import datetime, timedelta
import firebase_admin
from firebase_admin import credentials, firestore, auth as firebase_auth
from google.cloud import storage
from dotenv import load_dotenv
import json
from google.oauth2 import service_account
import threading
import logging
from mailersend import emails
from time import sleep
import mercadopago
import time

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

# --- VARIABLE GLOBAL PARA EL ESTADO DEL SCRAPER (SIMPLE) ---
scraper_status = {
    "is_running": False,
    "progress": 0,
    "total_tasks": 0,
    "completed_tasks": 0,
    "error": None,
    "result": None,
    "current_user": None
}

# Variable global para controlar si hay un scraper corriendo
scraper_en_proceso = threading.Event()

# --- LÍMITES POR PLAN ---
PLAN_LIMITS = {
    "free_trial": {
        "max_groups": 1,
        "max_competitors": 2,
        "max_days": 7,
        "scheduling": False
    },
    "esencial": {
        "max_groups": 1,
        "max_competitors": 3,
        "max_days": 30,
        "scheduling": False
    },
    "pro": {
        "max_groups": 3,
        "max_competitors": 5,
        "max_days": 60,
        "scheduling": "weekly"
    },
    "market_leader": {
        "max_groups": 5,
        "max_competitors": 7,
        "max_days": 90,
        "scheduling": "weekly"
    },
    "custom": {
        "max_groups": 8,
        "max_competitors": 7,
        "max_days": 90,
        "scheduling": "weekly"
    }
}

# --- Mapeo de planes a preapproval_plan_id de Mercado Pago ---
MP_PLAN_IDS = {
    "esencial": "2c93808497c462520197d744586508be",
    "pro": "2c93808497c19ac40197d7445b440a20",
    "market_leader": "2c93808497d635430197d7445e1c00bc"
}

def get_user_plan(uid):
    try:
        user_ref = db.collection('users').document(uid)
        user_doc = user_ref.get()
        if user_doc is not None and hasattr(user_doc, 'exists') and user_doc.exists:
            user_dict = user_doc.to_dict() if hasattr(user_doc, 'to_dict') else None
            if user_dict is not None:
                return user_dict.get('plan', 'free_trial')
        return 'free_trial'
    except Exception as e:
        logger.error(f"Error obteniendo plan del usuario {uid}: {e}")
        return 'free_trial'

# --- FUNCIÓN ASÍNCRONA PARA EL SCRAPER (SIMPLE) ---
def run_scraper_async(hotel_base_urls, days, userEmail=None, setName=None, nights=1, currency="USD", report_id=None, userId=None, setId=None):
    global scraper_status
    try:
        logger.info(f"[Scraper] INICIO run_scraper_async para reporte: {report_id} | hoteles: {hotel_base_urls}")
        scraper_status["is_running"] = True
        scraper_status["error"] = None
        scraper_status["progress"] = 0
        
        from apify_scraper import scrape_booking_data
        
        logger.info(f"[Scraper] Ejecutando scraper para {len(hotel_base_urls)} hoteles por {days} días, {nights} noches, moneda {currency}")
        result = scrape_booking_data(hotel_base_urls, days, nights, currency)
        
        if not result:
            raise Exception("No se obtuvieron datos del scraper")
        
        # --- ENRIQUECER DATOS PARA GRÁFICOS ---
        hotelNames = [hotel["Hotel Name"] for hotel in result]
        all_dates = set()
        for hotel in result:
            for k in hotel.keys():
                if k not in ("Hotel Name", "URL"):
                    all_dates.add(k)
        # Ordenar fechas cronológicamente de menor a mayor
        from datetime import datetime as dt
        all_dates = sorted(all_dates, key=lambda x: dt.strptime(x, "%Y-%m-%d"))
        column_order = ["Hotel Name", "URL"] + all_dates
        
        # Generar chartData con el formato correcto para el frontend
        chartData = []
        for date in all_dates:
            day_obj = {"date": date}
            
            # Añadir precios de cada hotel
            for hotel in result:
                name = hotel["Hotel Name"]
                price = hotel.get(date, None)
                if price is not None:
                    try:
                        day_obj[name] = float(price)
                    except:
                        day_obj[name] = None
                else:
                    day_obj[name] = None
            
            # Calcular métricas para esta fecha
            precios_validos = {}
            for hotel in result:
                name = hotel["Hotel Name"]
                price = hotel.get(date, None)
                if price is not None:
                    try:
                        precios_validos[name] = float(price)
                    except:
                        pass
            
            # Calcular promedio de competidores
            hotel_principal = hotelNames[0] if hotelNames else None
            competidores = hotelNames[1:] if len(hotelNames) > 1 else []
            
            if competidores and hotel_principal:
                precios_competidores = [precios_validos.get(comp, 0) for comp in competidores if precios_validos.get(comp, 0) > 0]
                if precios_competidores:
                    promedio = sum(precios_competidores) / len(precios_competidores)
                    day_obj["Tarifa promedio de competidores"] = round(promedio, 2)
                else:
                    day_obj["Tarifa promedio de competidores"] = None
                
                # Calcular disponibilidad (%)
                total_hoteles = len(hotelNames)
                hoteles_con_precio = len([name for name in hotelNames if precios_validos.get(name) is not None])
                disponibilidad_porcentaje = round((hoteles_con_precio / total_hoteles) * 100) if total_hoteles > 0 else 0
                day_obj["Disponibilidad de la oferta (%)"] = disponibilidad_porcentaje
            else:
                day_obj["Tarifa promedio de competidores"] = None
                day_obj["Disponibilidad de la oferta (%)"] = None
            
            chartData.append(day_obj)
        
        # Asegurar que hotelNames esté correctamente ordenado (hotel principal primero)
        # El primer hotel en la lista debe ser el hotel principal del usuario
        if hotelNames:
            hotel_principal = hotelNames[0]
            competidores = hotelNames[1:]
            # Reordenar si es necesario para asegurar que el hotel principal esté primero
            hotelNames = [hotel_principal] + competidores
        
        # Generar filas de métricas para los archivos Excel/CSV
        promedio_competidores_row = {"Hotel Name": "Tarifa promedio de competidores", "URL": ""}
        disponibilidad_row = {"Hotel Name": "Disponibilidad de la oferta (%)", "URL": ""}
        diferencia_row = {"Hotel Name": "Diferencia de mi tarifa vs. la tarifa promedio de los competidores (%)", "URL": ""}
        
        for date in all_dates:
            precios_validos = {}
            for hotel in result:
                name = hotel["Hotel Name"]
                price = hotel.get(date, None)
                if price is not None:
                    try:
                        precios_validos[name] = float(price)
                    except:
                        pass
            
            if competidores and hotel_principal:
                precios_competidores = [precios_validos.get(comp, 0) for comp in competidores if precios_validos.get(comp, 0) > 0]
                if precios_competidores:
                    promedio = sum(precios_competidores) / len(precios_competidores)
                    promedio_competidores_row[date] = str(round(promedio, 2))
                else:
                    promedio_competidores_row[date] = ''
                
                if hotel_principal in precios_validos:
                    disponibilidad_row[date] = "100"
                else:
                    disponibilidad_row[date] = "0"
                
                if hotel_principal in precios_validos and promedio_competidores_row[date] not in (None, ""):
                    mi_precio = precios_validos[hotel_principal]
                    diff_percent = ((mi_precio - float(promedio_competidores_row[date])) / float(promedio_competidores_row[date])) * 100
                    diferencia_row[date] = str(round(diff_percent, 0))
                else:
                    diferencia_row[date] = ''
            else:
                promedio_competidores_row[date] = ''
                disponibilidad_row[date] = ''
                diferencia_row[date] = ''
        
        result.append(promedio_competidores_row)
        result.append(disponibilidad_row)
        result.append(diferencia_row)
        # --- GENERAR ARCHIVOS ---
        def limpiar_nombre(nombre):
            import re
            return re.sub(r'[<>:"/\\|?*]', '', nombre)
        set_name_clean = limpiar_nombre(setName) if setName else "scraping"
        if not report_id:
            report_id = f"{set_name_clean}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        csv_blob_name = f"reports/{report_id}.csv"
        excel_blob_name = f"reports/{report_id}.xlsx"
        # Crear DataFrame y forzar orden de columnas
        df_csv = pd.DataFrame(result)
        df_csv = df_csv.reindex(columns=column_order)
        csv_buffer = io.StringIO()
        df_csv.to_csv(csv_buffer, index=False, decimal=',')
        csv_buffer.seek(0)
        csv_blob = bucket.blob(csv_blob_name)
        # Añadir metadatos personalizados con userId para las reglas de seguridad
        csv_blob.metadata = {'userId': userId}
        csv_blob.upload_from_string(csv_buffer.getvalue(), content_type='text/csv')
        logger.info(f"[Scraper] Archivo CSV generado y subido: {csv_blob_name}")
        df_excel = pd.DataFrame(result)
        df_excel = df_excel.reindex(columns=column_order)
        with pd.ExcelWriter('temp_excel_upload.xlsx', engine='openpyxl') as writer:
            df_excel.to_excel(writer, sheet_name='Tarifas', index=False)
        with open('temp_excel_upload.xlsx', 'rb') as f:
            excel_blob = bucket.blob(excel_blob_name)
            # Añadir metadatos personalizados con userId para las reglas de seguridad
            excel_blob.metadata = {'userId': userId}
            excel_blob.upload_from_file(f, content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        os.remove('temp_excel_upload.xlsx')
        logger.info(f"[Scraper] Archivo Excel generado y subido: {excel_blob_name}")
        # --- GUARDAR EN FIRESTORE ---
        logger.info(f"[Scraper] Preparando para guardar reporte en Firestore con ID: {report_id}")
        now = firestore.SERVER_TIMESTAMP
        report_data = {
            "status": "completed",
            "csvFileUrl": f"https://storage.googleapis.com/{GCS_BUCKET_NAME}/{csv_blob_name}",
            "xlsxFileUrl": f"https://storage.googleapis.com/{GCS_BUCKET_NAME}/{excel_blob_name}",
            "createdAt": now,
            "completedAt": now,
            "chartData": chartData,
            "hotelNames": hotelNames,
            "userId": userId,
            "setId": setId if setId else report_id,
            "setName": setName,
            "result": result,
            "days": days,
            "nights": nights,
            "currency": currency
        }
        try:
            logger.info(f"[Scraper] Guardando documento en Firestore con .set()... (ID: {report_id})")
            db.collection("scraping_reports").document(report_id).set(report_data)
            logger.info(f"[Scraper] Documento guardado exitosamente en Firestore (ID: {report_id})")
        except Exception as e:
            logger.error(f"[Scraper] ERROR al guardar documento en Firestore (ID: {report_id}): {e}")
        # --- ENVIAR CORREO AL USUARIO ---
        try:
            if userEmail:
                mailer = emails.NewEmail(os.environ.get('MAILERSEND_API_KEY'))
                mail_body = {
                    "from": {
                        "email": os.environ.get('MAILERSEND_SENDER_EMAIL', 'noreply@hotelrateshopper.com'),
                        "name": os.environ.get('MAILERSEND_SENDER_NAME', 'Hotel Rate Shopper')
                    },
                    "to": [
                        {
                            "email": userEmail,
                            "name": "Usuario"
                        }
                    ],
                    "subject": f"¡Tu informe para '{setName}' está listo!",
                    "reply_to": [
                        {
                            "email": "nicolas.wegher@gmail.com",
                            "name": "Nicolás Wegher"
                        }
                    ],
                    "html": f"""
<!DOCTYPE html>
<html lang=\"es\">
  <head>
    <meta charset=\"UTF-8\">
    <title>¡Tu informe para '{setName}' está listo!</title>
  </head>
  <body style=\"font-family: Arial, sans-serif; background: #fff; color: #222; margin: 0; padding: 0;\">
    <div style=\"max-width: 600px; margin: 40px auto; padding: 32px 24px; background: #fff; border-radius: 8px; box-shadow: 0 2px 8px rgba(0,0,0,0.04);\">
      <h1 style=\"color: #222; font-size: 2em; margin-bottom: 0.5em;\">¡Tu informe está listo!</h1>
      <p>Hola,</p>
      <p>
        Tu informe de precios para el grupo competitivo <strong>'{setName}'</strong> ya está disponible.
      </p>
      <div style=\"margin: 32px 0;\">
        <a href=\"https://hotelrateshopper.com/\" style=\"display: inline-block; background: #34a853; color: #fff; font-weight: bold; text-decoration: none; padding: 16px 32px; border-radius: 6px; font-size: 1.1em;\">
          Ver mi informe en la plataforma
        </a>
      </div>
      <p>También puedes descargar el informe directamente desde este correo:</p>
      <div style=\"margin: 20px 0;\">
        <a href=\"https://storage.googleapis.com/{GCS_BUCKET_NAME}/{excel_blob_name}\" style=\"display: inline-block; background: #4285f4; color: #fff; font-weight: bold; text-decoration: none; padding: 12px 24px; border-radius: 6px; font-size: 1em; margin-bottom: 8px;\">
          Descargar Informe (Excel)
        </a>
      </div>
      <div style=\"margin-bottom: 24px;\">
        <a href=\"https://storage.googleapis.com/{GCS_BUCKET_NAME}/{csv_blob_name}\" style=\"color: #4285f4; text-decoration: underline; font-size: 1em;\">
          Descargar en formato .CSV
        </a>
      </div>
      <p style=\"margin-top: 32px;\">Gracias por usar <a href=\"https://hotelrateshopper.com\" style=\"color: #4285f4; text-decoration: underline;\">HotelRateShopper.com</a></p>
    </div>
  </body>
</html>
"""
                }
                response = mailer.send(mail_body)
                logger.info(f"[Scraper] Respuesta de MailerSend: {response}")
        except Exception as e:
            logger.error(f"[Scraper] Error enviando correo: {e}")
        # Actualizar estado
        scraper_status["result"] = report_data
        scraper_status["progress"] = 100
        scraper_status["is_running"] = False
        logger.info("[Scraper] FIN run_scraper_async (éxito)")
    except Exception as e:
        logger.error(f"[Scraper] Error en scraper: {e}")
        # Actualizar el documento con status failed y completedAt
        try:
            now = firestore.SERVER_TIMESTAMP
            logger.info(f"[Scraper] Intentando actualizar documento a failed en Firestore (ID: {report_id})...")
            db.collection("scraping_reports").document(report_id).update({
                "status": "failed",
                "completedAt": now,
                "error": str(e)
            })
            logger.info(f"[Scraper] Reporte {report_id} marcado como failed en Firestore")
        except Exception as e2:
            logger.error(f"[Scraper] ERROR actualizando status failed en Firestore: {e2}")
        scraper_status["error"] = str(e)
        scraper_status["is_running"] = False
        scraper_status["current_user"] = None
        logger.info("[Scraper] FIN run_scraper_async (fallo)")

def cola_procesadora_scraping():
    global scraper_en_proceso
    while True:
        try:
            if scraper_en_proceso.is_set():
                time.sleep(5)
                continue
            logger.info("[ColaScraping] Bucle activo. Buscando tareas encoladas...")
            query = (
                db.collection('scraping_reports')
                .where('status', '==', 'queued')
                .order_by('createdAt')
                .limit(1)
            )
            docs = list(query.stream())
            if not docs:
                logger.info("[ColaScraping] No se encontraron tareas encoladas. Esperando 20s...")
                time.sleep(20)
                continue
            doc = docs[0]
            doc_ref = doc.reference
            data = doc.to_dict()
            if data is None:
                logger.error(f"[ColaScraping] El documento {doc_ref.id} no tiene datos. Saltando...")
                continue
            # LOGS DE DEPURACIÓN
            logger.info(f"[ColaScraping][DEBUG] Documento Firestore data: {data}")
            logger.info(f"[ColaScraping][DEBUG] ownHotelUrl: {data.get('ownHotelUrl')} (tipo: {type(data.get('ownHotelUrl'))})")
            logger.info(f"[ColaScraping][DEBUG] competitorHotelUrls: {data.get('competitorHotelUrls')} (tipo: {type(data.get('competitorHotelUrls'))})")
            # Obtener hoteles directamente del documento (denormalización)
            hotel_base_urls = []
            if data.get('ownHotelUrl'):
                hotel_base_urls.append(data['ownHotelUrl'])
            comp_urls = data.get('competitorHotelUrls')
            if comp_urls:
                if isinstance(comp_urls, list):
                    hotel_base_urls.extend(comp_urls)
                elif isinstance(comp_urls, str):
                    hotel_base_urls.append(comp_urls)
                else:
                    logger.warning(f"[ColaScraping][DEBUG] competitorHotelUrls tiene un tipo inesperado: {type(comp_urls)}")
            logger.info(f"[ColaScraping][DEBUG] hotel_base_urls final: {hotel_base_urls}")
            if not hotel_base_urls:
                logger.error(f"[ColaScraping] La tarea {doc_ref.id} no tiene hoteles para analizar. Saltando...")
                doc_ref.update({'status': 'failed', 'error': 'No se encontraron hoteles para analizar'})
                continue
            logger.info(f"[ColaScraping] Procesando tarea: {doc_ref.id} - {data.get('setName', '')} con hoteles: {hotel_base_urls}")
            doc_ref.update({'status': 'pending'})
            # Marcar que hay un scraper en proceso
            scraper_en_proceso.set()
            # Ejecutar el scraper con los datos del documento
            run_scraper_async(
                hotel_base_urls,
                data.get('days', data.get('daysToScrape', 7)),
                data.get('userEmail', None),
                data.get('setName', None),
                data.get('nights', 1),
                data.get('currency', 'USD'),
                report_id=doc_ref.id,
                userId=data.get('userId', None),
                setId=data.get('setId', None)
            )
            # Cuando termine, limpiar el flag
            scraper_en_proceso.clear()
        except Exception as e:
            logger.error(f"[ColaScraping] Error en cola_procesadora_scraping: {e}")
        time.sleep(5)

# --- ENDPOINT PRINCIPAL (SIMPLE) ---
@app.route('/run-scraper', methods=['POST'])
def run_scraper():
    global scraper_status
    
    try:
        data = request.get_json()
        uid = data.get('uid')
        hotel_base_urls = data.get('hotel_base_urls', [])
        days = data.get('days', 7)
        nights = data.get('nights', 1)
        currency = data.get('currency', 'USD')
        setName = data.get('setName', 'Mi Set')
        userEmail = data.get('userEmail')
        report_id = data.get('report_id')
        setId = data.get('setId')  # <-- Tomar el setId del payload
        
        logger.info(f"[run-scraper] Recibido UID: {uid}, report_id: {report_id}, setId: {setId}")
        
        # Verificar si ya hay un scraper corriendo
        if scraper_status["is_running"]:
            return jsonify({
                "success": False,
                "message": "Ya hay un scraper ejecutándose. Espera a que termine."
            }), 400
        
        # Verificar plan del usuario
        user_plan = get_user_plan(uid)
        plan_limits = PLAN_LIMITS.get(user_plan, PLAN_LIMITS["free_trial"])
        
        if len(hotel_base_urls) > plan_limits["max_competitors"] + 1:  # +1 para el hotel principal
            return jsonify({
                "success": False,
                "message": f"Tu plan {user_plan} permite máximo {plan_limits['max_competitors']} competidores"
            }), 400
        
        if days > plan_limits["max_days"]:
            return jsonify({
                "success": False,
                "message": f"Tu plan {user_plan} permite máximo {plan_limits['max_days']} días"
            }), 400
        
        # Iniciar scraper en thread separado
        scraper_status["current_user"] = uid
        thread = threading.Thread(
            target=run_scraper_async,
            args=(hotel_base_urls, days, userEmail, setName, nights, currency, report_id, uid, setId) # Pasar userId y setId
        )
        thread.daemon = True
        thread.start()
        
        return jsonify({
            "success": True,
            "message": "Scraper iniciado correctamente",
            "plan": user_plan
        })
        
    except Exception as e:
        logger.error(f"Error en run-scraper: {e}")
        return jsonify({
            "success": False,
            "message": f"Error: {str(e)}"
        }), 500

# --- ENDPOINTS ADICIONALES (MANTENER) ---
@app.route('/', methods=['GET'])
def health_check():
    return jsonify({"status": "ok", "message": "Backend funcionando"})

@app.route('/datos', methods=['GET'])
def obtener_datos():
    try:
        datos = obtener_datos_externos()
        return jsonify(datos)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/descargar-csv', methods=['GET', 'POST'])
def descargar_csv():
    try:
        data = request.get_json() if request.method == 'POST' else request.args
        report_id = data.get('report_id')
        
        if not report_id:
            return jsonify({"error": "report_id requerido"}), 400
        
        # Obtener reporte de Firestore
        report_ref = db.collection("scraping_reports").document(report_id)
        report = report_ref.get()
        
        if not report.exists:
            return jsonify({"error": "Reporte no encontrado"}), 404
        
        report_data = report.to_dict() or {}
        result = report_data.get('result', [])
        
        # Crear CSV
        df = pd.DataFrame(result)
        csv_buffer = io.StringIO()
        df.to_csv(csv_buffer, index=False, decimal=',')
        csv_buffer.seek(0)
        
        return send_file(
            io.BytesIO(csv_buffer.getvalue().encode('utf-8')),
            mimetype='text/csv',
                        as_attachment=True, 
            download_name=f"tarifas_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        )
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/descargar-excel', methods=['GET', 'POST'])
def descargar_excel():
    try:
        data = request.get_json() if request.method == 'POST' else request.args
        report_id = data.get('report_id')
        
        if not report_id:
            return jsonify({"error": "report_id requerido"}), 400
        
        # Obtener reporte de Firestore
        report_ref = db.collection("scraping_reports").document(report_id)
        report = report_ref.get()
        
        if not report.exists:
            return jsonify({"error": "Reporte no encontrado"}), 404
        
        report_data = report.to_dict() or {}
        result = report_data.get('result', [])
        
        # Crear Excel
        df = pd.DataFrame(result)
        with pd.ExcelWriter('temp_excel_download.xlsx', engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name='Tarifas', index=False)
        with open('temp_excel_download.xlsx', 'rb') as f:
            excel_bytes = f.read()
        os.remove('temp_excel_download.xlsx')
        return send_file(
            io.BytesIO(excel_bytes),
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            as_attachment=True,
            download_name=f"tarifas_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        )
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/scraper-status', methods=['GET'])
def get_scraper_status():
    return jsonify(scraper_status)

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

# --- MANTENER EL RESTO DE ENDPOINTS ---
@app.route('/execute-scheduled-tasks', methods=['POST'])
def execute_scheduled_tasks():
    try:
        data = request.get_json()
        uid = data.get('uid')
        
        if not uid:
            return jsonify({"error": "UID requerido"}), 400
        
        # Obtener grupos del usuario
        grupos_ref = db.collection('users').document(uid).collection('grupos')
        grupos = grupos_ref.stream()
        
        for grupo in grupos:
            grupo_data = grupo.to_dict()
            if grupo_data.get('schedule_enabled', False):
                hotel_urls = [grupo_data.get('hotel_principal')] + grupo_data.get('competidores', [])
                report_doc = {
                    'userId': uid,
                    'setId': grupo_data.get('id'),
                    'setName': grupo_data.get('name'),
                    'hotel_base_urls': hotel_urls,
                    'days': grupo_data.get('days', 7),
                    'nights': grupo_data.get('nights', 1),
                    'currency': grupo_data.get('currency', 'USD'),
                    'userEmail': grupo_data.get('userEmail', None),
                    'status': 'queued',
                    'createdAt': datetime.now(),
                }
                db.collection('scraping_reports').add(report_doc)
        return jsonify({"success": True, "message": "Tareas programadas encoladas"})
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/init-user', methods=['POST'])
def init_user():
    try:
        data = request.get_json()
        uid = data.get('uid')
        email = data.get('email')
        plan = data.get('plan', 'free_trial')
        if not uid or not email:
            return jsonify({"error": "UID y email requeridos"}), 400
        # Crear o actualizar usuario
        user_ref = db.collection('users').document(uid)
        user_ref.set({
            'email': email,
            'plan': plan,
            'created_at': datetime.now()
        })
        return jsonify({"success": True, "message": "Usuario inicializado"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/crear-grupo', methods=['POST'])
def crear_grupo():
    try:
        data = request.get_json()
        uid = data.get('uid')
        nombre = data.get('nombre')
        hotel_principal = data.get('hotel_principal')
        if not uid or not nombre or not hotel_principal:
            return jsonify({"error": "UID, nombre y hotel principal requeridos"}), 400
        # Verificar límites del plan
        user_plan = get_user_plan(uid)
        plan_limits = PLAN_LIMITS.get(user_plan, PLAN_LIMITS["free_trial"])
        # Contar grupos existentes
        grupos_ref = db.collection('users').document(uid).collection('grupos')
        grupos_existentes = len(list(grupos_ref.stream()))
        if grupos_existentes >= plan_limits["max_groups"]:
            return jsonify({
                "error": f"Tu plan {user_plan} permite máximo {plan_limits['max_groups']} grupos"
            }), 400
        # Crear grupo
        grupo_ref = db.collection('users').document(uid).collection('grupos').document()
        grupo_ref.set({
            'name': nombre,
            'hotel_principal': hotel_principal,
            'competidores': [],
            'days': 7,
            'schedule_enabled': False,
            'created_at': datetime.now()
        })
        return jsonify({"success": True, "message": "Grupo creado"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/agregar-competidor', methods=['POST'])
def agregar_competidor():
    try:
        data = request.get_json()
        uid = data.get('uid')
        grupo_id = data.get('grupo_id')
        competidor_url = data.get('competidor_url')
        if not uid or not grupo_id or not competidor_url:
            return jsonify({"error": "UID, grupo_id y competidor_url requeridos"}), 400
        # Verificar límites del plan
        user_plan = get_user_plan(uid)
        plan_limits = PLAN_LIMITS.get(user_plan, PLAN_LIMITS["free_trial"])
        # Obtener grupo actual
        grupo_ref = db.collection('users').document(uid).collection('grupos').document(grupo_id)
        grupo = grupo_ref.get()
        if not grupo.exists:
            return jsonify({"error": "Grupo no encontrado"}), 404
        grupo_data = grupo.to_dict()
        competidores_actuales = len(grupo_data.get('competidores', []))
        if competidores_actuales >= plan_limits["max_competitors"]:
            return jsonify({
                "error": f"Tu plan {user_plan} permite máximo {plan_limits['max_competitors']} competidores"
            }), 400
        # Agregar competidor
        competidores = grupo_data.get('competidores', [])
        competidores.append(competidor_url)
        grupo_ref.update({
            'competidores': competidores
        })
        return jsonify({"success": True, "message": "Competidor agregado"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/configurar-dias', methods=['POST'])
def configurar_dias():
    try:
        data = request.get_json()
        uid = data.get('uid')
        grupo_id = data.get('grupo_id')
        dias = data.get('dias')
        if not uid or not grupo_id or not dias:
            return jsonify({"error": "UID, grupo_id y dias requeridos"}), 400
        # Verificar límites del plan
        user_plan = get_user_plan(uid)
        plan_limits = PLAN_LIMITS.get(user_plan, PLAN_LIMITS["free_trial"])
        if dias > plan_limits["max_days"]:
            return jsonify({
                "error": f"Tu plan {user_plan} permite máximo {plan_limits['max_days']} días"
            }), 400
        # Actualizar días
        grupo_ref = db.collection('users').document(uid).collection('grupos').document(grupo_id)
        grupo_ref.update({
            'days': dias
        })
        return jsonify({"success": True, "message": "Días configurados"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/configurar-schedule', methods=['POST'])
def configurar_schedule():
    try:
        data = request.get_json()
        uid = data.get('uid')
        grupo_id = data.get('grupo_id')
        enabled = data.get('enabled', False)
        if not uid or not grupo_id:
            return jsonify({"error": "UID y grupo_id requeridos"}), 400
        # Verificar si el plan permite scheduling
        user_plan = get_user_plan(uid)
        plan_limits = PLAN_LIMITS.get(user_plan, PLAN_LIMITS["free_trial"])
        if enabled and not plan_limits["scheduling"]:
            return jsonify({
                "error": f"Tu plan {user_plan} no permite programación automática"
            }), 400
        # Actualizar schedule
        grupo_ref = db.collection('users').document(uid).collection('grupos').document(grupo_id)
        grupo_ref.update({
            'schedule_enabled': enabled
        })
        return jsonify({"success": True, "message": "Schedule configurado"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/create-subscription-checkout', methods=['POST'])
def create_subscription_checkout():
    try:
        data = request.get_json()
        plan = data.get('plan')
        user_email = data.get('user_email')
        if not plan or not user_email:
            return jsonify({"error": "Plan y email requeridos"}), 400
        if plan not in MP_PLAN_IDS:
            return jsonify({"error": "Plan no válido"}), 400
        # Configurar Mercado Pago
        mp = mercadopago.SDK(os.environ.get('MP_ACCESS_TOKEN'))
        # Crear preferencia de suscripción
        preference_data = {
            "items": [
                {
                    "title": f"Plan {plan}",
                    "quantity": 1,
                    "unit_price": 10.0  # Precio de ejemplo
                }
            ],
            "payer": {
                "email": user_email
            },
            "back_urls": {
                "success": "https://tu-frontend.com/success",
                "failure": "https://tu-frontend.com/failure",
                "pending": "https://tu-frontend.com/pending"
            },
            "auto_return": "approved",
            "external_reference": f"plan_{plan}_{user_email}",
            "notification_url": "https://tu-backend.com/mercado-pago-webhook"
        }
        preference = mp.preference().create(preference_data)
        if preference["status"] == "created":
            return jsonify({
                "success": True,
                "init_point": preference["response"]["init_point"],
                "preference_id": preference["response"]["id"]
            })
        else:
            return jsonify({"error": "Error creando preferencia"}), 500
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/mercado-pago-webhook', methods=['POST'])
def mercado_pago_webhook():
    try:
        data = request.get_json()
        
        # Verificar que es una notificación válida de MP
        if data.get("type") == "payment":
            payment_id = data.get("data", {}).get("id")
            
            if payment_id:
                # Obtener información del pago
                mp = mercadopago.SDK(os.environ.get('MP_ACCESS_TOKEN'))
                payment_info = mp.payment().get(payment_id)
                
                if payment_info["status"] == 200:
                    payment_data = payment_info["response"]
                    
                    # Procesar según el estado del pago
                    if payment_data["status"] == "approved":
                        # Pago aprobado - actualizar plan del usuario
                        external_reference = payment_data.get("external_reference", "")
                        
                        # Extraer información del external_reference
                        # Formato esperado: "plan_{plan}_{email}"
                        if external_reference.startswith("plan_"):
                            parts = external_reference.split("_")
                            if len(parts) >= 3:
                                plan = parts[1]
                                email = "_".join(parts[2:])  # En caso de que el email tenga _
                                
                                # Buscar usuario por email
                                users_ref = db.collection('users')
                                users = users_ref.where('email', '==', email).stream()
                                
                                for user in users:
                                    user_ref = db.collection('users').document(user.id)
                                    user_ref.update({
                                        'plan': plan,
                                        'plan_updated_at': datetime.now()
                                    })
                                    
                                    # Enviar email de confirmación
                                    try:
                                        from mailersend import emails
                                        mailer = emails.NewEmail(os.environ.get('MAILERSEND_API_KEY'))
                                        
                                        mail_body = {
                                            "from": {
                                                "email": "noreply@tuapp.com",
                                                "name": "Tu App"
                                            },
                                            "to": [
                                                {
                                                    "email": email,
                                                    "name": "Usuario"
                                                }
                                            ],
                                            "subject": "Plan actualizado exitosamente",
                                            "html": f"""
                                            <h2>¡Plan actualizado!</h2>
                                            <p>Tu plan ha sido actualizado a <strong>{plan}</strong>.</p>
                                            <p>Gracias por tu compra.</p>
                                            """
                                        }
                                        
                                        mailer.send(mail_body)
                                        
                                    except Exception as e:
                                        logger.error(f"Error enviando email: {e}")
                                    
                                    break
                
                    elif payment_data["status"] == "rejected":
                        # Pago rechazado - enviar email de notificación
                        external_reference = payment_data.get("external_reference", "")
                        if external_reference.startswith("plan_"):
                            parts = external_reference.split("_")
                            if len(parts) >= 3:
                                email = "_".join(parts[2:])
                                
                                try:
                                    from mailersend import emails
                                    mailer = emails.NewEmail(os.environ.get('MAILERSEND_API_KEY'))
                                    
                                    mail_body = {
                                        "from": {
                                            "email": "noreply@tuapp.com",
                                            "name": "Tu App"
                                        },
                                        "to": [
                                            {
                                                "email": email,
                                                "name": "Usuario"
                                            }
                                        ],
                                        "subject": "Problema con el pago",
                                        "html": """
                                        <h2>Problema con el pago</h2>
                                        <p>Tu pago fue rechazado. Por favor, intenta nuevamente.</p>
                                        """
                                    }
                                    
                                    mailer.send(mail_body)
                                    
                                except Exception as e:
                                    logger.error(f"Error enviando email: {e}")
        
        return jsonify({"success": True}), 200
        
    except Exception as e:
        logger.error(f"Error en webhook de Mercado Pago: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/debug', methods=['POST'])
def debug_endpoint():
    try:
        data = request.get_json()
        uid = data.get('uid')
        
        if not uid:
            return jsonify({"error": "UID requerido"}), 400
        
        # Obtener información del usuario
        user_ref = db.collection('users').document(uid)
        user_doc = user_ref.get()
        
        if not user_doc.exists:
            return jsonify({"error": "Usuario no encontrado"}), 404
        
        user_data = user_doc.to_dict()
        
        # Obtener grupos del usuario
        grupos_ref = db.collection('users').document(uid).collection('grupos')
        grupos = []
        for grupo in grupos_ref.stream():
            grupos.append({
                'id': grupo.id,
                'data': grupo.to_dict()
            })
        
        return jsonify({
            "user": user_data,
            "grupos": grupos,
            "scraper_status": scraper_status
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/test-metricas', methods=['GET'])
def test_metricas():
    try:
        # Datos de ejemplo para probar las métricas
        result = [
            {
                "Hotel Name": "Hotel Principal",
                "URL": "https://example.com",
                "2024-01-01": 100.0,
                "2024-01-02": 110.0,
                "2024-01-03": 105.0
            },
            {
                "Hotel Name": "Competidor 1",
                "URL": "https://example.com",
                "2024-01-01": 95.0,
                "2024-01-02": 105.0,
                "2024-01-03": 100.0
            },
            {
                "Hotel Name": "Competidor 2",
                "URL": "https://example.com",
                "2024-01-01": 105.0,
                "2024-01-02": 115.0,
                "2024-01-03": 110.0
            }
        ]
        
        # Calcular métricas
        hotel_principal = "Hotel Principal"
        competidores = ["Competidor 1", "Competidor 2"]
        
        promedio_competidores_row = {"Hotel Name": "Tarifa promedio de competidores", "URL": ""}
        disponibilidad_row = {"Hotel Name": "Disponibilidad de la oferta (%)", "URL": ""}
        diferencia_row = {"Hotel Name": "Diferencia de mi tarifa vs. la tarifa promedio de los competidores (%)", "URL": ""}
        
        all_dates = ["2024-01-01", "2024-01-02", "2024-01-03"]
        
        for date in all_dates:
            precios_validos = {}
            for hotel in result:
                name = hotel["Hotel Name"]
                price = hotel.get(date, None)
                if price is not None:
                    try:
                        precios_validos[name] = float(price)
                    except:
                        pass
            # Calcular promedio de competidores
            if competidores and hotel_principal:
                precios_competidores = [precios_validos.get(comp, 0) for comp in competidores if precios_validos.get(comp, 0) > 0]
                if precios_competidores:
                    promedio = sum(precios_competidores) / len(precios_competidores)
                    promedio_competidores_row[date] = str(round(promedio, 2))
                else:
                    promedio_competidores_row[date] = ''
                if hotel_principal in precios_validos:
                    disponibilidad_row[date] = "100"
                else:
                    disponibilidad_row[date] = "0"
                if hotel_principal in precios_validos and promedio_competidores_row[date] not in (None, ""):
                    mi_precio = precios_validos[hotel_principal]
                    diff_percent = ((mi_precio - float(promedio_competidores_row[date])) / float(promedio_competidores_row[date])) * 100
                    diferencia_row[date] = str(round(diff_percent, 0))
                else:
                    diferencia_row[date] = ''
            else:
                promedio_competidores_row[date] = ''
                disponibilidad_row[date] = ''
                diferencia_row[date] = ''
        
        result.append(promedio_competidores_row)
        result.append(disponibilidad_row)
        result.append(diferencia_row)
        
        return jsonify({
            "success": True,
            "result": result
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Lanzar el procesador de la cola SIEMPRE, no solo en modo script
import threading
threading.Thread(target=cola_procesadora_scraping, daemon=True).start()

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000) 