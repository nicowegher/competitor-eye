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

# --- VARIABLE GLOBAL PARA EL ESTADO DEL SCRAPER ---
scraper_status = {
    "is_running": False,
    "progress": 0,
    "total_tasks": 0,
    "completed_tasks": 0,
    "error": None,
    "result": None
}

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
    user_ref = db.collection('users').document(uid)
    user_doc = user_ref.get()
    if user_doc and user_doc.exists:
        return user_doc.to_dict().get('plan', 'free_trial')
    return 'free_trial'

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
def run_scraper_async(hotel_base_urls, days, taskId, userEmail=None, setName=None, nights=1, currency="USD"):
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
            "days": days,
            "nights": nights,
            "currency": currency
        })
        
        # Ejecutar scraper
        logger.info(f"Ejecutando scraper para {len(hotel_base_urls)} hoteles por {days} días, {nights} noches, moneda {currency}")
        result = scrape_booking_data(hotel_base_urls, days, nights, currency)
        
        if not result:
            raise Exception("No se obtuvieron datos del scraper")
        
        # --- ENRIQUECER DATOS PARA GRÁFICOS ---
        # 1. Extraer nombres de hoteles en orden
        hotelNames = [hotel["Hotel Name"] for hotel in result]
        # 2. Extraer todas las fechas únicas y ordenarlas cronológicamente
        all_dates = set()
        for hotel in result:
            for k in hotel.keys():
                if k not in ("Hotel Name", "URL"):
                    all_dates.add(k)
        # Ordenar fechas cronológicamente
        from datetime import datetime as dt
        all_dates = sorted(all_dates, key=lambda x: dt.strptime(x, "%Y-%m-%d"))
        # 3. Construir chartData
        chartData = []
        for date in all_dates:
            day_obj = {"date": date}
            for hotel in result:
                name = hotel["Hotel Name"]
                price = hotel.get(date, None)
                # Convertir "N/A" a None/null, y string numérico a float
                if price == "N/A":
                    day_obj[name] = None
                elif price is None:
                    day_obj[name] = None
                else:
                    try:
                        day_obj[name] = float(price)
                    except:
                        day_obj[name] = None
            chartData.append(day_obj)
        # --- CALCULAR MÉTRICAS ADICIONALES ---
        hotel_principal = hotelNames[0] if hotelNames else None
        competidores = hotelNames[1:] if len(hotelNames) > 1 else []
        promedio_competidores_row = {"Hotel Name": "Tarifa promedio de competidores", "URL": ""}
        disponibilidad_row = {"Hotel Name": "Disponibilidad de la oferta (%)", "URL": ""}
        diferencia_row = {"Hotel Name": "Diferencia de mi tarifa vs. la tarifa promedio de los competidores (%)", "URL": ""}
        for date in all_dates:
            precios_validos = {}
            for hotel in result:
                name = hotel["Hotel Name"]
                price = hotel.get(date, None)
                if price and price != "N/A":
                    try:
                        precios_validos[name] = float(price)
                    except:
                        continue
            precios_competidores = []
            for name in competidores:
                precio = precios_validos.get(name)
                if precio is not None and isinstance(precio, (int, float)):
                    precios_competidores.append(precio)
            promedio_competidores = None
            if precios_competidores:
                promedio_competidores = sum(precios_competidores) / len(precios_competidores)
            # Redondear a 2 decimales y usar coma como separador decimal
            if promedio_competidores is not None:
                promedio_competidores_str = f"{promedio_competidores:.2f}".replace('.', ',')
            else:
                promedio_competidores_str = ""
            total_hoteles = len(hotelNames)
            hoteles_con_precio = len([name for name in hotelNames if precios_validos.get(name) is not None])
            disponibilidad_porcentaje = round((hoteles_con_precio / total_hoteles) * 100) if total_hoteles > 0 else 0
            # Mostrar como entero entre 0 y 100
            disponibilidad = str(int(disponibilidad_porcentaje))
            diferencia_porcentual = None
            precio_principal = precios_validos.get(hotel_principal)
            if precio_principal is not None and promedio_competidores is not None and promedio_competidores > 0:
                diferencia = ((precio_principal - promedio_competidores) / promedio_competidores) * 100
                # Mostrar como entero entre 0 y 100 (sin signo)
                diferencia_porcentual = str(int(round(abs(diferencia))))
            else:
                diferencia_porcentual = ""
            promedio_competidores_row[date] = promedio_competidores_str
            disponibilidad_row[date] = disponibilidad
            diferencia_row[date] = diferencia_porcentual
            # Agregar métricas al chartData (para frontend)
            chartData.append({
                "date": date,
                "Tarifa promedio de competidores": promedio_competidores,
                "Disponibilidad de la oferta (%)": disponibilidad,
                "Diferencia de mi tarifa vs. la tarifa promedio de los competidores (%)": diferencia_porcentual
            })
        result.append(promedio_competidores_row)
        result.append(disponibilidad_row)
        result.append(diferencia_row)
        # --- FORMATO DE NOMBRE DE ARCHIVO ---
        import re
        def limpiar_nombre(nombre):
            if not nombre:
                return "SIN_NOMBRE"
            nombre = nombre.upper()
            nombre = re.sub(r"[ÁÀÂÄ]", "A", nombre)
            nombre = re.sub(r"[ÉÈÊË]", "E", nombre)
            nombre = re.sub(r"[ÍÌÎÏ]", "I", nombre)
            nombre = re.sub(r"[ÓÒÔÖ]", "O", nombre)
            nombre = re.sub(r"[ÚÙÛÜ]", "U", nombre)
            nombre = re.sub(r"[^A-Z0-9]", "_", nombre)
            nombre = re.sub(r"_+", "_", nombre)
            return nombre.strip("_")
        set_name_limpio = limpiar_nombre(setName) if setName else "SIN_NOMBRE"
        timestamp = datetime.now().strftime("%Y%m%d_%H%M")
        base_filename = f"HotelRateShopper_{set_name_limpio}_{timestamp}"
        csv_filename = f"{base_filename}.csv"
        xlsx_filename = f"{base_filename}.xlsx"
        # Generar archivos CON las métricas incluidas
        df = pd.DataFrame(result)
        # Ordenar columnas: Hotel Name, URL, fechas ordenadas
        columnas_ordenadas = ["Hotel Name", "URL"] + all_dates
        df = df[columnas_ordenadas]
        # Convertir todos los valores flotantes a string con coma como separador decimal
        for col in all_dates:
            df[col] = pd.Series(df[col]).apply(lambda x: f"{x:.2f}".replace('.', ',') if isinstance(x, float) else x)
        df.to_csv(csv_filename, index=False, encoding='utf-8', sep=';')
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
        

        
        # Actualizar Firestore con éxito usando taskId
        doc_ref.update({
            "status": "completed",
            "completedAt": datetime.now(),
            "csvFileUrl": csv_url,
            "xlsxFileUrl": xlsx_url,
            "totalRecords": len(result),
            "hotelNames": hotelNames,
            "chartData": chartData
        })
        
        # Enviar email de notificación si hay userEmail
        if userEmail:
            try:
                mailer = emails.NewEmail(os.environ.get("MAILERSEND_API_KEY"))
                mail_from = {"name": os.environ.get("MAILERSEND_SENDER_NAME", "Hotel Rate Shopper"), "email": os.environ.get("MAILERSEND_SENDER_EMAIL", "no-reply@hotelrateshopper.com")}
                recipients = [{"email": userEmail}]
                subject = f"¡Tu informe para '{setName or 'Hoteles'}' está listo!"
                html_content = f'''
                <h1>¡Tu informe está listo!</h1>
                <p>Hola,</p>
                <p>Tu informe de precios para el grupo competitivo "<strong>{setName or 'Hoteles'}"</strong> ya está disponible.</p>
                <p style="font-size: 1.1em; font-weight: bold;">
                  <a href="https://www.hotelrateshopper.com" style="padding: 12px 20px; background-color: #28a745; color: white; text-decoration: none; border-radius: 5px; font-size: 1.1em;">
                    Ver mi informe en la plataforma
                  </a>
                </p>
                <p>También puedes descargar el informe directamente desde este correo:</p>
                <p>
                  <a href="{xlsx_url}" style="padding: 10px 15px; background-color: #007BFF; color: white; text-decoration: none; border-radius: 5px;">
                    Descargar Informe (Excel)
                  </a>
                </p>
                <p>
                  <a href="{csv_url}">
                    Descargar en formato .CSV
                  </a>
                </p>
                <p>Gracias por usar <a href="https://www.hotelrateshopper.com">HotelRateShopper.com</a></p>
                '''
                mail_body = {}
                mailer.set_mail_from(mail_from, mail_body)
                mailer.set_reply_to({"email": "nicolas.wegher@gmail.com", "name": "Nicolás Wegher"}, mail_body)
                mailer.set_mail_to(recipients, mail_body)
                mailer.set_subject(subject, mail_body)
                mailer.set_html_content(html_content, mail_body)
                mailer.set_plaintext_content(f"Tu informe para '{setName or 'Hoteles'}' está listo. Descarga Excel: {xlsx_url} | CSV: {csv_url}", mail_body)
                response = mailer.send(mail_body)
                logger.info(f"Respuesta de MailerSend: {getattr(response, 'status_code', 'N/A')} - {getattr(response, 'text', str(response))}")
                logger.info(f"Email de notificación enviado a {userEmail}")
            except Exception as e:
                logger.error(f"Error al enviar el email de notificación: {e}")
        
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
            "completedAt": datetime.utcnow(),
            "error": str(e)
        })

# --- COLA DE TRABAJOS PERSISTENTE EN FIRESTORE ---
# Cada trabajo es un documento en la colección 'scraper_jobs'

# Estado de trabajos individuales (por taskId)
jobs_status = {}

# --- ENDPOINT MEJORADO DE SCRAPER ---
@app.route('/run-scraper', methods=['POST'])
def run_scraper():
    global scraper_status
    try:
        data = request.get_json()
        if data is None:
            return jsonify({"error": "Invalid JSON data"}), 400
        taskId = data.get("taskId")
        uid = data.get("userId")
        days = data.get("daysToScrape", 2)
        nights = data.get("nights", 1)
        currency = data.get("currency", "USD")
        set_id = data.get("setId") or data.get("taskId")
        plan = get_user_plan(uid)
        logger.info(f"Plan detectado para el usuario {uid}: {plan}")
        limits = PLAN_LIMITS.get(plan, PLAN_LIMITS['free_trial'])
        if days > limits['max_days']:
            return jsonify({"error": f"Tu plan solo permite hasta {limits['max_days']} días de análisis.", "code": "LIMIT_DAYS"}), 403
        if not taskId:
            return jsonify({"error": "taskId is required"}), 400
        hotel_base_urls = [data["ownHotelUrl"]] + data["competitorHotelUrls"]
        userEmail = data.get("userEmail")
        setName = data.get("setName")
        # --- LIMITACIÓN: 1 investigación cada 15 minutos por set competitivo ---
        quince_minutos_atras = datetime.utcnow() - timedelta(minutes=15)
        query = db.collection("scraping_reports").where("setId", "==", set_id).where("startedAt", ">=", quince_minutos_atras)
        docs = list(query.stream())
        if docs:
            return jsonify({
                "status": "rate_limited",
                "message": "Solo puedes enviar una investigación cada 15 minutos para este set competitivo."
            }), 429
        # --- ENCOLAR TRABAJO EN FIRESTORE ---
        job_doc = {
            'taskId': taskId,
            'setId': set_id,
            'userId': uid,
            'hotel_base_urls': hotel_base_urls,
            'days': days,
            'nights': nights,
            'currency': currency,
            'userEmail': userEmail,
            'setName': setName,
            'status': 'queued',
            'createdAt': datetime.utcnow(),
            'enqueuedAt': datetime.utcnow().isoformat()
        }
        db.collection('scraper_jobs').document(taskId).set(job_doc)
        jobs_status[taskId] = {'status': 'queued', 'enqueuedAt': job_doc['enqueuedAt']}
        return jsonify({
            "status": "queued",
            "message": "Tu investigación fue encolada y se procesará en orden. Recibirás un email al finalizar.",
            "taskId": taskId
        })
    except Exception as e:
        logger.error(f"Error al encolar scraper: {str(e)}")
        return jsonify({"error": str(e)}), 500

# --- WORKER QUE PROCESA LA COLA PERSISTENTE (FIFO) ---
def scraper_worker():
    global worker_running
    logger.info("[WORKER] Worker de scraper iniciado y corriendo.")
    while True:
        try:
            # Buscar el trabajo 'queued' más antiguo (FIFO)
            jobs_ref = db.collection('scraper_jobs').where('status', '==', 'queued').order_by('createdAt').limit(1)
            jobs = list(jobs_ref.stream())
            if jobs:
                job_doc = jobs[0]
                job = job_doc.to_dict()
                if job is not None:
                    taskId = job['taskId']
                    logger.info(f"[WORKER] Trabajo tomado de Firestore: taskId={taskId}, setId={job.get('setId')}, userId={job.get('userId')}")
                    # Marcar como 'running'
                    db.collection('scraper_jobs').document(taskId).update({
                        'status': 'running',
                        'startedAt': datetime.utcnow()
                    })
                    jobs_status[taskId] = {'status': 'running', 'startedAt': datetime.now().isoformat()}
                    try:
                        run_scraper_async(
                            job['hotel_base_urls'],
                            job['days'],
                            job['taskId'],
                            job.get('userEmail'),
                            job.get('setName'),
                            job.get('nights', 1),
                            job.get('currency', 'USD')
                        )
                        # Marcar como 'completed'
                        db.collection('scraper_jobs').document(taskId).update({
                            'status': 'completed',
                            'completedAt': datetime.utcnow()
                        })
                        jobs_status[taskId]['status'] = 'completed'
                        jobs_status[taskId]['completedAt'] = datetime.now().isoformat()
                    except Exception as e:
                        db.collection('scraper_jobs').document(taskId).update({
                            'status': 'failed',
                            'completedAt': datetime.utcnow(),
                            'error': str(e)
                        })
                        jobs_status[taskId]['status'] = 'failed'
                        jobs_status[taskId]['error'] = str(e)
                        jobs_status[taskId]['completedAt'] = datetime.now().isoformat()
            else:
                logger.info("[WORKER] Cola Firestore vacía, esperando trabajos...")
            time.sleep(2)
        except Exception as e:
            logger.error(f"[WORKER] Error en el worker de la cola persistente: {e}")
            time.sleep(5)

# Lanzar el worker en background al iniciar la app
worker_running = False
worker_thread = threading.Thread(target=scraper_worker, daemon=True)
worker_thread.start()
worker_running = True

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

# --- ENDPOINT PARA VERIFICAR ESTADO DEL SCRAPER ---
@app.route('/scraper-status', methods=['GET'])
def get_scraper_status():
    task_id = request.args.get('taskId')
    if task_id:
        return jsonify(jobs_status.get(task_id, {"status": "not_found"}))
    global scraper_status
    return jsonify(scraper_status)

# --- ENDPOINT PARA EJECUCIÓN PROGRAMADA DE SCRAPERS ---
@app.route('/execute-scheduled-tasks', methods=['POST'])
def execute_scheduled_tasks():
    SECRET_TOKEN = os.environ.get('SCHEDULE_SECRET_TOKEN', 'supersecreto')
    token = request.args.get('token')
    if token != SECRET_TOKEN:
        return jsonify({"error": "Token inválido"}), 403

    try:
        hoy = datetime.utcnow()
        dia_semana = hoy.weekday()  # 0=Lunes, 6=Domingo
        # Firestore: obtener todos los competitive_sets con schedule no nulo
        sets_ref = db.collection('competitive_sets')
        sets = sets_ref.stream()
        sets_a_ejecutar = []
        for doc in sets:
            data = doc.to_dict()
            schedule = data.get('schedule')
            if not schedule:
                continue
            freq = schedule.get('frequency')
            day_of_week = schedule.get('dayOfWeek')
            if freq == 'daily':
                ejecutar = True
            elif freq == 'weekly' and day_of_week is not None and int(day_of_week) == dia_semana:
                ejecutar = True
            else:
                ejecutar = False
            if ejecutar:
                sets_a_ejecutar.append({
                    'setId': doc.id,
                    'userId': data.get('userId'),
                    'userEmail': data.get('userEmail'),
                    'ownHotelUrl': data.get('ownHotelUrl'),
                    'competitorHotelUrls': data.get('competitorHotelUrls', []),
                    'daysToScrape': schedule.get('daysToScrape', 2),
                    'setName': data.get('name', '')
                })
        resultados = []
        for s in sets_a_ejecutar:
            payload = {
                'taskId': s['setId'],
                'ownHotelUrl': s['ownHotelUrl'],
                'competitorHotelUrls': s['competitorHotelUrls'],
                'daysToScrape': s['daysToScrape'],
                'userEmail': s['userEmail'],
                'setName': s['setName']
            }
            try:
                # Llamada interna al endpoint /run-scraper
                url = request.host_url.rstrip('/') + '/run-scraper'
                resp = requests.post(url, json=payload, timeout=60)
                resultados.append({
                    'setId': s['setId'],
                    'status': resp.status_code,
                    'response': resp.json()
                })
                sleep(2)  # Pausa de 2 segundos entre ejecuciones para evitar sobrecarga
            except Exception as e:
                resultados.append({
                    'setId': s['setId'],
                    'status': 'error',
                    'error': str(e)
                })
        return jsonify({
            'total_sets': len(sets_a_ejecutar),
            'resultados': resultados
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# --- ENDPOINT PARA INICIAR USUARIO ---
@app.route('/init-user', methods=['POST'])
def init_user():
    data = request.get_json()
    if data is None:
        return {"error": "Invalid JSON data"}, 400
    
    uid = data.get('uid')
    email = data.get('email')
    if not uid or not email:
        return {"error": "Faltan datos"}, 400

    user_ref = db.collection('users').document(uid)
    user_ref.set({
        "email": email,
        "plan": "free_trial"
    }, merge=True)
    return {"success": True}

# --- ENDPOINT CREAR GRUPO COMPETITIVO (ejemplo) ---
@app.route('/crear-grupo', methods=['POST'])
def crear_grupo():
    data = request.get_json()
    if data is None:
        return {"error": "Invalid JSON data"}, 400
    
    uid = data.get('uid')
    plan = get_user_plan(uid)
    limits = PLAN_LIMITS.get(plan, PLAN_LIMITS['free_trial'])
    # Contar grupos existentes
    grupos = db.collection('competitive_sets').where('userId', '==', uid).stream()
    num_grupos = len(list(grupos))
    if num_grupos >= limits['max_groups']:
        return {"error": "Límite de grupos alcanzado para tu plan.", "code": "LIMIT_GROUPS"}, 403
    # ... lógica para crear el grupo ...
    return {"success": True}

# --- ENDPOINT AGREGAR COMPETIDOR (ejemplo) ---
@app.route('/agregar-competidor', methods=['POST'])
def agregar_competidor():
    data = request.get_json()
    if data is None:
        return {"error": "Invalid JSON data"}, 400
    
    uid = data.get('uid')
    set_id = data.get('setId')
    plan = get_user_plan(uid)
    limits = PLAN_LIMITS.get(plan, PLAN_LIMITS['free_trial'])
    set_ref = db.collection('competitive_sets').document(set_id)
    set_doc = set_ref.get()
    if not set_doc or not set_doc.exists:
        return {"error": "Grupo no encontrado.", "code": "NOT_FOUND"}, 404
    competidores = set_doc.to_dict().get('competitorHotelUrls', [])
    if len(competidores) >= limits['max_competitors']:
        return {"error": "Límite de competidores alcanzado para tu plan.", "code": "LIMIT_COMPETITORS"}, 403
    # ... lógica para agregar competidor ...
    return {"success": True}

# --- ENDPOINT CONFIGURAR DÍAS DE ANÁLISIS (ejemplo) ---
@app.route('/configurar-dias', methods=['POST'])
def configurar_dias():
    data = request.get_json()
    if data is None:
        return {"error": "Invalid JSON data"}, 400
    
    uid = data.get('uid')
    days = data.get('daysToScrape')
    plan = get_user_plan(uid)
    limits = PLAN_LIMITS.get(plan, PLAN_LIMITS['free_trial'])
    if days > limits['max_days']:
        return {"error": f"Tu plan solo permite hasta {limits['max_days']} días de análisis.", "code": "LIMIT_DAYS"}, 403
    # ... lógica para guardar la configuración ...
    return {"success": True}

# --- ENDPOINT CONFIGURAR PROGRAMACIÓN (ejemplo) ---
@app.route('/configurar-schedule', methods=['POST'])
def configurar_schedule():
    data = request.get_json()
    if data is None:
        return {"error": "Invalid JSON data"}, 400
    
    uid = data.get('uid')
    schedule = data.get('schedule')
    plan = get_user_plan(uid)
    limits = PLAN_LIMITS.get(plan, PLAN_LIMITS['free_trial'])
    if not limits['scheduling']:
        return {"error": "Tu plan no permite programar investigaciones automáticas.", "code": "LIMIT_SCHEDULING"}, 403
    if limits['scheduling'] == 'weekly' and (schedule is not None and schedule.get('frequency') == 'daily'):
        return {"error": "Tu plan solo permite programación semanal.", "code": "LIMIT_SCHEDULING_FREQ"}, 403
    # ... lógica para guardar la programación ...
    return {"success": True}

# --- Endpoint para crear suscripción de Mercado Pago ---
@app.route('/create-subscription-checkout', methods=['POST'])
def create_subscription_checkout():
    data = request.get_json()
    if data is None:
        return {"error": "Invalid JSON data"}, 400
    
    plan_id = data.get('planId')
    token = request.headers.get('Authorization', '').replace('Bearer ', '')
    if not plan_id or plan_id not in MP_PLAN_IDS:
        return {"error": "Plan inválido."}, 400
    if not token:
        return {"error": "Token de autenticación requerido."}, 401
    try:
        decoded_token = firebase_auth.verify_id_token(token)
        user_id = decoded_token['uid']
        user_email = decoded_token.get('email')
    except Exception as e:
        import traceback
        print("ERROR VERIFICANDO TOKEN FIREBASE:", e)
        traceback.print_exc()
        return {"error": f"Token inválido o expirado. Detalle: {str(e)}"}, 401
    sdk = mercadopago.SDK(os.environ['MERCADOPAGO_ACCESS_TOKEN'])
    preference = {
        "preapproval_plan_id": MP_PLAN_IDS[plan_id],
        "payer_email": user_email,
        "external_reference": user_id,
        "back_url": "https://hotelrateshopper.com/dashboard"
    }
    try:
        result = sdk.preapproval().create(preference)
        print("RESULTADO MERCADO PAGO:", result)
        init_point = result['response'].get('init_point')
        if not init_point:
            return {"error": f"No se pudo crear el checkout. Detalle: {result['response']}"}, 500
        return {"checkoutUrl": init_point}
    except Exception as e:
        import traceback
        print("ERROR MERCADO PAGO:", e)
        traceback.print_exc()
        return {"error": f"Error al crear suscripción: {str(e)}"}, 500

# --- Webhook de Mercado Pago para actualizar plan del usuario ---
@app.route('/mercado-pago-webhook', methods=['POST'])
def mercado_pago_webhook():
    try:
        logger.info("=== WEBHOOK MERCADO PAGO RECIBIDO ===")
        logger.info(f"Headers: {dict(request.headers)}")
        logger.info(f"Body: {request.get_json()}")
        
        # Validación de clave secreta
        mp_secret = os.environ.get('MP_WEBHOOK_SECRET')
        received_secret = request.headers.get('x-signature')
        if mp_secret:
            if not received_secret:
                logger.error("❌ Falta la cabecera x-signature en el webhook")
                return "Forbidden: missing signature", 403
            if received_secret != mp_secret:
                logger.error(f"❌ Clave secreta inválida. Recibida: {received_secret}")
                return "Forbidden: invalid signature", 403
            logger.info("✅ Clave secreta validada correctamente")
        else:
            logger.warning("⚠️ No hay clave secreta configurada en MP_WEBHOOK_SECRET")
        
        body = request.get_json()
        
        if body is None:
            logger.error("Body vacío en webhook")
            return "Bad Request", 400
            
        # Manejar diferentes tipos de notificaciones
        notification_type = body.get('type')
        logger.info(f"Tipo de notificación: {notification_type}")
        
        if notification_type == 'preapproval':
            # Notificación de suscripción
            preapproval_id = body['data']['id']
            logger.info(f"Preapproval ID: {preapproval_id}")
            
            # Verificar si es un test (ID que empiece con 'test_')
            is_test = preapproval_id.startswith('test_')
            
            if is_test:
                logger.info("🔄 Procesando TEST de webhook")
                # Para tests, usar datos hardcodeados o del body
                test_user_id = body.get('test_user_id', 'test_user_123')
                test_plan = body.get('test_plan', 'esencial')
                
                logger.info(f"Test User ID: {test_user_id}")
                logger.info(f"Test Plan: {test_plan}")
                
                try:
                    # Actualizar el plan del usuario en Firestore
                    user_ref = db.collection('users').document(test_user_id)
                    user_ref.update({
                        "plan": test_plan,
                        "subscription_updated_at": datetime.now(),
                        "mp_subscription_id": preapproval_id,
                        "is_test": True
                    })
                    logger.info(f"✅ Plan actualizado para test - Usuario {test_user_id}: {test_plan}")
                except Exception as firestore_error:
                    logger.error(f"Error actualizando Firestore: {firestore_error}")
                    return "Error actualizando Firestore", 500
                
            else:
                # Solo inicializar SDK para suscripciones reales
                try:
                    sdk = mercadopago.SDK(os.environ['MERCADOPAGO_ACCESS_TOKEN'])
                    # Obtener detalles de la suscripción real
                    preapproval = sdk.preapproval().get(preapproval_id)
                    logger.info(f"Preapproval response: {preapproval}")
                    
                    if preapproval['response']:
                        status = preapproval['response'].get('status')
                        user_id = preapproval['response'].get('external_reference')
                        mp_plan_id = preapproval['response'].get('preapproval_plan_id')
                        
                        logger.info(f"Status: {status}")
                        logger.info(f"User ID: {user_id}")
                        logger.info(f"MP Plan ID: {mp_plan_id}")
                        
                        if status == 'authorized' and user_id and mp_plan_id:
                            # Encontrar el plan correspondiente
                            plan = next((k for k, v in MP_PLAN_IDS.items() if v == mp_plan_id), None)
                            logger.info(f"Plan encontrado: {plan}")
                            
                            if plan:
                                # Actualizar el plan del usuario en Firestore
                                user_ref = db.collection('users').document(user_id)
                                user_ref.update({
                                    "plan": plan,
                                    "subscription_updated_at": datetime.now(),
                                    "mp_subscription_id": preapproval_id
                                })
                                logger.info(f"✅ Plan actualizado para usuario {user_id}: {plan}")
                                
                                # Log del usuario actualizado
                                user_doc = user_ref.get()
                                if user_doc.exists:
                                    logger.info(f"Usuario actualizado: {user_doc.to_dict()}")
                            else:
                                logger.error(f"No se encontró plan para MP Plan ID: {mp_plan_id}")
                        else:
                            logger.info(f"Suscripción no autorizada o datos incompletos. Status: {status}")
                    else:
                        logger.error("No se pudo obtener información de la suscripción")
                except Exception as mp_error:
                    logger.error(f"Error con Mercado Pago: {mp_error}")
                    return "Error con Mercado Pago", 500
                
        elif notification_type == 'subscription_preapproval':
            # Notificación específica de suscripción
            logger.info("Notificación de suscripción recibida")
            # Procesar igual que preapproval
            preapproval_id = body['data']['id']
            try:
                sdk = mercadopago.SDK(os.environ['MERCADOPAGO_ACCESS_TOKEN'])
                preapproval = sdk.preapproval().get(preapproval_id)
                
                if preapproval['response']:
                    status = preapproval['response'].get('status')
                    user_id = preapproval['response'].get('external_reference')
                    mp_plan_id = preapproval['response'].get('preapproval_plan_id')
                    
                    if status == 'authorized' and user_id and mp_plan_id:
                        plan = next((k for k, v in MP_PLAN_IDS.items() if v == mp_plan_id), None)
                        if plan:
                            user_ref = db.collection('users').document(user_id)
                            user_ref.update({
                                "plan": plan,
                                "subscription_updated_at": datetime.now(),
                                "mp_subscription_id": preapproval_id
                            })
                            logger.info(f"Plan actualizado vía subscription_preapproval: {plan}")
            except Exception as mp_error:
                logger.error(f"Error con Mercado Pago en subscription_preapproval: {mp_error}")
                return "Error con Mercado Pago", 500
        else:
            logger.info(f"Tipo de notificación no manejado: {notification_type}")
            
        logger.info("=== WEBHOOK PROCESADO EXITOSAMENTE ===")
        return "OK", 200
        
    except Exception as e:
        logger.error(f"Error en webhook Mercado Pago: {e}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        return "Error", 500

# --- ENDPOINT DE DEBUG ---
@app.route('/debug', methods=['POST'])
def debug_endpoint():
    try:
        logger.info("=== DEBUG ENDPOINT ===")
        body = request.get_json()
        logger.info(f"Body recibido: {body}")
        
        # Test de Firestore
        try:
            test_ref = db.collection('users').document('test_user_123')
            test_ref.set({
                "email": "test@example.com",
                "plan": "free_trial",
                "debug_test": True,
                "timestamp": datetime.now()
            }, merge=True)
            logger.info("✅ Firestore funcionando")
        except Exception as firestore_error:
            logger.error(f"❌ Error en Firestore: {firestore_error}")
            return {"error": f"Firestore error: {str(firestore_error)}"}, 500
        
        # Test de variables de entorno
        mp_token = os.environ.get('MERCADOPAGO_ACCESS_TOKEN')
        if mp_token:
            logger.info("✅ MERCADOPAGO_ACCESS_TOKEN configurado")
        else:
            logger.error("❌ MERCADOPAGO_ACCESS_TOKEN no configurado")
        
        return {"status": "debug successful", "body": body}, 200
        
    except Exception as e:
        logger.error(f"Error en debug endpoint: {e}")
        return {"error": str(e)}, 500

# --- ENDPOINT DE PRUEBA PARA MÉTRICAS ---
@app.route('/test-metricas', methods=['GET'])
def test_metricas():
    try:
        # Datos de prueba simulados
        datos_prueba = [
            {
                "Hotel Name": "Hotel Principal",
                "URL": "https://example.com/hotel1",
                "2024-01-15": 150.0,
                "2024-01-16": 160.0,
                "2024-01-17": 155.0
            },
            {
                "Hotel Name": "Competidor 1",
                "URL": "https://example.com/hotel2",
                "2024-01-15": 140.0,
                "2024-01-16": 150.0,
                "2024-01-17": "N/A"
            },
            {
                "Hotel Name": "Competidor 2",
                "URL": "https://example.com/hotel3",
                "2024-01-15": 145.0,
                "2024-01-16": "N/A",
                "2024-01-17": 150.0
            }
        ]
        
        # Extraer nombres de hoteles
        hotelNames = [hotel["Hotel Name"] for hotel in datos_prueba]
        hotel_principal = hotelNames[0]
        competidores = hotelNames[1:]
        
        # Extraer fechas únicas
        all_dates = set()
        for hotel in datos_prueba:
            for k in hotel.keys():
                if k not in ("Hotel Name", "URL"):
                    all_dates.add(k)
        all_dates = sorted(all_dates)
        
        # Calcular métricas
        metricas_resultado = []
        chartData = []
        
        for date in all_dates:
            # Obtener precios válidos para esta fecha
            precios_validos = {}
            for hotel in datos_prueba:
                name = hotel["Hotel Name"]
                price = hotel.get(date, None)
                if price and price != "N/A":
                    try:
                        precios_validos[name] = float(price)
                    except:
                        continue
            
            # 1. Calcular tarifa promedio de competidores
            precios_competidores = []
            for name in competidores:
                precio = precios_validos.get(name)
                if precio is not None and isinstance(precio, (int, float)):
                    precios_competidores.append(precio)
            
            promedio_competidores = None
            if precios_competidores:
                promedio_competidores = sum(precios_competidores) / len(precios_competidores)
            
            # 2. Calcular disponibilidad de la oferta (%)
            total_hoteles = len(hotelNames)
            hoteles_con_precio = len([name for name in hotelNames if precios_validos.get(name) is not None])
            disponibilidad_porcentaje = round((hoteles_con_precio / total_hoteles) * 100) if total_hoteles > 0 else 0
            disponibilidad = f"{disponibilidad_porcentaje}%"
            
            # 3. Calcular diferencia porcentual del hotel principal vs promedio de competidores
            diferencia_porcentual = None
            precio_principal = precios_validos.get(hotel_principal)
            if precio_principal is not None and promedio_competidores is not None and promedio_competidores > 0:
                diferencia = ((precio_principal - promedio_competidores) / promedio_competidores) * 100
                diferencia_porcentual = f"{diferencia:+.1f}%" if diferencia != 0 else "0.0%"
            
            # Agregar métricas al resultado
            metricas_resultado.append({
                "fecha": date,
                "tarifa_promedio_competidores": promedio_competidores,
                "disponibilidad_oferta": disponibilidad,
                "diferencia_porcentual": diferencia_porcentual,
                "precios_competidores": precios_competidores,
                "precio_principal": precio_principal
            })
            
            # Agregar al chartData
            chartData.append({
                "date": date,
                "Tarifa promedio de competidores": promedio_competidores,
                "Disponibilidad de la oferta (%)": disponibilidad,
                "Diferencia de mi tarifa vs. la tarifa promedio de los competidores (%)": diferencia_porcentual
            })
        
        # Crear DataFrame con métricas para Excel
        datos_con_metricas = datos_prueba.copy()
        for date in all_dates:
            metricas_fecha = next(m for m in metricas_resultado if m["fecha"] == date)
            
            datos_con_metricas.append({
                "Hotel Name": "Tarifa promedio de competidores",
                "URL": "",
                date: metricas_fecha["tarifa_promedio_competidores"]
            })
            datos_con_metricas.append({
                "Hotel Name": "Disponibilidad de la oferta (%)",
                "URL": "",
                date: metricas_fecha["disponibilidad_oferta"]
            })
            datos_con_metricas.append({
                "Hotel Name": "Diferencia de mi tarifa vs. la tarifa promedio de los competidores (%)",
                "URL": "",
                date: metricas_fecha["diferencia_porcentual"]
            })
        
        return {
            "success": True,
            "datos_originales": datos_prueba,
            "metricas_calculadas": metricas_resultado,
            "datos_con_metricas": datos_con_metricas,
            "chartData": chartData,
            "hotel_principal": hotel_principal,
            "competidores": competidores,
            "fechas": all_dates
        }
        
    except Exception as e:
        logger.error(f"Error en test_metricas: {e}")
        return {"error": str(e)}, 500

# --- CONFIGURACIÓN PARA RENDER.COM ---
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port) 