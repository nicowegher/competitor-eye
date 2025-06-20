## Plan de Pruebas

1.  **Verificación de configuración inicial:**
    *   Confirmar que `APIFY_API_TOKEN` ha sido reemplazado con un token válido.
    *   Confirmar que la lista `hotel_urls` contiene URLs de hoteles válidas de Booking.com.

2.  **Ejecución manual del script:**
    *   Ejecutar `python3 apify_scraper.py` en la terminal.
    *   Verificar que el script se ejecuta sin errores.
    *   Verificar que se generan dos archivos de salida: `tarifas_hoteles_YYYYMMDD.xlsx` y `tarifas_hoteles_YYYYMMDD.csv`.
    *   Abrir los archivos generados y verificar que contienen los datos esperados (nombre del hotel, URL, y precios para los próximos 60 días).
    *   Asegurarse de que los precios son razonables y que la lógica de la tarifa más baja por día funciona correctamente.

3.  **Verificación de la lógica de fechas:**
    *   Confirmar que las fechas de `checkIn` y `checkOut` en el script se calculan correctamente para los próximos 60 días a partir de la fecha actual.

4.  **Prueba de automatización (simulada):**
    *   Aunque no podemos esperar 24 horas, podemos verificar la configuración del `crontab` y la sintaxis del comando para asegurar que se ejecutará correctamente.
    *   Verificar que el archivo `scraper_log.log` se crea y se actualiza con la salida del script.

## Creación de Documentación

Se creará un archivo `README.md` que incluirá:

*   Descripción del proyecto.
*   Requisitos previos (Python, pip, apify-client).
*   Instalación y configuración (Apify API Token, URLs de hoteles).
*   Uso del script.
*   Configuración de la automatización diaria con `cron`.
*   Estructura de los archivos de salida.
*   Solución de problemas comunes.


