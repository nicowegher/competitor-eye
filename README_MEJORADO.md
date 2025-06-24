# Scraper de Tarifas de Hoteles en Booking.com - Versión Mejorada

## 🚀 Descripción

Backend en Python para hacer scraping de tarifas de hoteles en Booking.com usando Apify. Esta versión incluye mejoras significativas para resolver problemas de timeout y memoria en Render.com.

## ✨ Mejoras Implementadas

- ✅ **Ejecución asíncrona**: No más timeouts de HTTP
- ✅ **Configuración optimizada**: Gunicorn configurado para Render
- ✅ **Logging detallado**: Mejor visibilidad del progreso
- ✅ **Manejo de errores robusto**: Recuperación automática de fallos
- ✅ **Estado en tiempo real**: Endpoint para monitorear progreso

## 🛠️ Tecnologías

- **Backend**: Flask + Gunicorn
- **Scraping**: Apify Client
- **Base de datos**: Firebase Firestore
- **Almacenamiento**: Google Cloud Storage
- **Deploy**: Render.com

## 📋 Requisitos

- Python 3.8+
- Cuenta de Apify con token API
- Proyecto Firebase configurado
- Bucket de Google Cloud Storage

## 🔧 Instalación

1. **Clonar el repositorio**
```bash
git clone <tu-repositorio>
cd scraper-hotel-tarifas
```

2. **Instalar dependencias**
```bash
pip install -r requirements.txt
```

3. **Configurar variables de entorno**
```bash
# Crear archivo .env
FIREBASE_SERVICE_ACCOUNT={"tu-json-de-firebase"}
GCS_BUCKET_NAME=tu-bucket-name
APIFY_API_TOKEN=tu-token-de-apify
```

4. **Configurar Firebase**
- Crear proyecto en Firebase Console
- Descargar archivo de credenciales
- Configurar Firestore y Storage

## 🚀 Uso

### Endpoints Disponibles

#### 1. Health Check
```bash
GET /
```
Verifica que el backend esté funcionando.

#### 2. Iniciar Scraper (NUEVO - Asíncrono)
```bash
POST /run-scraper
Content-Type: application/json

{
  "ownHotelUrl": "https://www.booking.com/hotel/ar/tu-hotel.es.html",
  "competitorHotelUrls": [
    "https://www.booking.com/hotel/ar/competidor1.es.html",
    "https://www.booking.com/hotel/ar/competidor2.es.html"
  ],
  "daysToScrape": 2
}
```

**Respuesta inmediata:**
```json
{
  "status": "started",
  "message": "Scraper iniciado correctamente",
  "hotels": 3,
  "days": 2
}
```

#### 3. Verificar Estado del Scraper (NUEVO)
```bash
GET /scraper-status
```

**Respuesta:**
```json
{
  "is_running": true,
  "progress": 45,
  "total_tasks": 6,
  "completed_tasks": 3,
  "error": null,
  "result": null
}
```

#### 4. Descargar Datos
```bash
GET /datos
GET /descargar-csv
GET /descargar-excel
```

## 🔄 Flujo de Uso Mejorado

1. **Iniciar scraper**
   ```bash
   curl -X POST https://tu-app.onrender.com/run-scraper \
     -H "Content-Type: application/json" \
     -d '{"ownHotelUrl": "...", "competitorHotelUrls": [...], "daysToScrape": 2}'
   ```

2. **Monitorear progreso**
   ```bash
   curl https://tu-app.onrender.com/scraper-status
   ```

3. **Verificar resultados en Firebase**
   - Los archivos se guardan automáticamente en GCS
   - Las URLs se actualizan en Firestore
   - El estado se actualiza cuando completa

## 🧪 Pruebas

Ejecutar el script de pruebas:
```bash
python test_scraper.py
```

**Nota**: Cambiar `BASE_URL` en el script por tu URL de Render.

## 📊 Configuración de Render

### Variables de Entorno Requeridas
- `FIREBASE_SERVICE_ACCOUNT`: JSON de credenciales de Firebase
- `GCS_BUCKET_NAME`: Nombre del bucket de Google Cloud Storage
- `APIFY_API_TOKEN`: Token de API de Apify

### Configuración Automática
El `Procfile` usa la configuración optimizada:
```
web: gunicorn app:app --config gunicorn.conf.py
```

## 🔍 Monitoreo y Logs

### Logs de Aplicación
- Logs detallados en Render Dashboard
- Información de progreso del scraper
- Errores y excepciones capturadas

### Estado del Scraper
- Endpoint `/scraper-status` para monitoreo
- Estado en tiempo real en Firebase
- URLs de archivos generados automáticamente

## 🚨 Solución de Problemas

### Error: Worker Timeout
- ✅ **Resuelto**: Configuración de Gunicorn con timeout de 5 minutos
- ✅ **Resuelto**: Ejecución asíncrona del scraper

### Error: Out of Memory
- ✅ **Resuelto**: Configuración optimizada de workers
- ✅ **Resuelto**: Limpieza automática de archivos temporales

### Error: Scraper no responde
- ✅ **Resuelto**: Endpoint de status para monitoreo
- ✅ **Resuelto**: Logging detallado del progreso

## 📈 Próximas Mejoras

1. **Sistema de colas**: Para múltiples scrapers simultáneos
2. **Webhooks**: Notificaciones automáticas al frontend
3. **Rate limiting**: Protección contra spam
4. **Caching**: Cachear resultados repetidos
5. **Dashboard**: Interfaz web para monitoreo

## 📝 Notas Importantes

- El scraper de Apify funciona correctamente (según los logs)
- Los problemas eran de configuración del backend
- La nueva versión es compatible con el frontend existente
- Los archivos se guardan automáticamente en GCS y Firebase

## 🤝 Contribución

1. Fork el proyecto
2. Crear rama para feature (`git checkout -b feature/AmazingFeature`)
3. Commit cambios (`git commit -m 'Add AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abrir Pull Request

## 📄 Licencia

Este proyecto está bajo la Licencia MIT. Ver `LICENSE` para más detalles. 