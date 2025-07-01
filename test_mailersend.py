from mailersend import emails
import os

# Asegúrate de tener estas variables de entorno configuradas
api_key = os.environ.get("MAILERSEND_API_KEY")
sender = "no-reply@test-65qngkdx5xolwr12.mlsender.net"
destino = "nicolas.wegher@gmail.com"  # Cambia esto por tu email real

mailer = emails.NewEmail(api_key)
mail_body = {}
mailer.set_mail_from({"email": sender, "name": "Scraper Tarifas Hoteles"}, mail_body)
mailer.set_mail_to([{"email": destino}], mail_body)
mailer.set_subject("Prueba manual de MailerSend", mail_body)
mailer.set_html_content("<h1>¡Funciona!</h1><p>Este es un correo de prueba desde MailerSend.</p>", mail_body)
mailer.set_plaintext_content("Este es un correo de prueba desde MailerSend.", mail_body)
response = mailer.send(mail_body)
print(f"Status code: {getattr(response, 'status_code', 'N/A')}")
print(f"Response: {getattr(response, 'text', str(response))}")