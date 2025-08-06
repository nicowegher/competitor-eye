#!/usr/bin/env python3
"""
Script para generar un token seguro para el scheduler de tareas programadas.
Este token debe ser configurado en Render como variable de entorno SCHEDULER_TOKEN.
"""

import secrets
import string

def generate_secure_token(length=32):
    """Genera un token seguro de la longitud especificada."""
    alphabet = string.ascii_letters + string.digits
    return ''.join(secrets.choice(alphabet) for _ in range(length))

if __name__ == "__main__":
    # Generar token seguro
    token = generate_secure_token(32)
    
    print("=" * 50)
    print("🔐 GENERADOR DE TOKEN PARA SCHEDULER")
    print("=" * 50)
    print(f"Token generado: {token}")
    print()
    print("📋 INSTRUCCIONES:")
    print("1. Copia este token")
    print("2. Ve a tu dashboard de Render")
    print("3. En tu servicio, ve a 'Environment'")
    print("4. Agrega la variable: SCHEDULER_TOKEN")
    print("5. Pega el token como valor")
    print("6. Guarda los cambios")
    print()
    print("🔗 URL para configurar en cron-job.org:")
    print(f"https://competitor-eye.onrender.com/execute-scheduled-tasks?token={token}")
    print()
    print("⚠️  IMPORTANTE: Guarda este token en un lugar seguro!")
    print("=" * 50) 