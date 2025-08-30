# Sistema de Soporte - Implementación con Formspree

## 🎯 Opción Recomendada: Formspree

### Ventajas:
- ✅ **Gratis** (hasta 50 submissions/mes)
- ✅ **Fácil implementación** (solo HTML)
- ✅ **No requiere backend**
- ✅ **Spam protection** incluido
- ✅ **Notificaciones automáticas** a tu email

## 📋 Implementación Paso a Paso

### 1. Crear cuenta en Formspree
1. Ve a [formspree.io](https://formspree.io)
2. Regístrate con tu email
3. Crea un nuevo formulario
4. Obtén el endpoint (ejemplo: `https://formspree.io/f/xaybzwkd`)

### 2. Implementar en el Frontend

```html
<!-- Formulario de Soporte -->
<form 
  action="https://formspree.io/f/TU_ENDPOINT_AQUI" 
  method="POST"
  class="support-form"
>
  <div class="form-group">
    <label for="name">Nombre completo *</label>
    <input 
      type="text" 
      id="name" 
      name="name" 
      required 
      class="form-control"
    >
  </div>

  <div class="form-group">
    <label for="email">Email *</label>
    <input 
      type="email" 
      id="email" 
      name="email" 
      required 
      class="form-control"
    >
  </div>

  <div class="form-group">
    <label for="subject">Asunto *</label>
    <select id="subject" name="subject" required class="form-control">
      <option value="">Selecciona un tema</option>
      <option value="Problema técnico">Problema técnico</option>
      <option value="Consulta sobre precios">Consulta sobre precios</option>
      <option value="Soporte de cuenta">Soporte de cuenta</option>
      <option value="Sugerencia">Sugerencia</option>
      <option value="Otro">Otro</option>
    </select>
  </div>

  <div class="form-group">
    <label for="message">Mensaje *</label>
    <textarea 
      id="message" 
      name="message" 
      rows="5" 
      required 
      class="form-control"
      placeholder="Describe tu problema o consulta..."
    ></textarea>
  </div>

  <div class="form-group">
    <label for="priority">Prioridad</label>
    <select id="priority" name="priority" class="form-control">
      <option value="Baja">Baja</option>
      <option value="Media" selected>Media</option>
      <option value="Alta">Alta</option>
      <option value="Urgente">Urgente</option>
    </select>
  </div>

  <button type="submit" class="btn btn-primary">
    Enviar solicitud de soporte
  </button>
</form>
```

### 3. JavaScript para mejor UX

```javascript
// Manejo del formulario con feedback visual
document.querySelector('.support-form').addEventListener('submit', function(e) {
  const submitBtn = this.querySelector('button[type="submit"]');
  const originalText = submitBtn.textContent;
  
  // Mostrar loading
  submitBtn.textContent = 'Enviando...';
  submitBtn.disabled = true;
  
  // Reset después de 3 segundos (simular envío)
  setTimeout(() => {
    submitBtn.textContent = originalText;
    submitBtn.disabled = false;
    
    // Mostrar mensaje de éxito
    showNotification('Solicitud enviada correctamente. Te responderemos pronto.', 'success');
  }, 3000);
});

function showNotification(message, type) {
  const notification = document.createElement('div');
  notification.className = `alert alert-${type === 'success' ? 'success' : 'danger'}`;
  notification.textContent = message;
  
  document.body.appendChild(notification);
  
  setTimeout(() => {
    notification.remove();
  }, 5000);
}
```

### 4. CSS para estilos

```css
.support-form {
  max-width: 600px;
  margin: 0 auto;
  padding: 20px;
}

.form-group {
  margin-bottom: 20px;
}

.form-control {
  width: 100%;
  padding: 10px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 16px;
}

.btn-primary {
  background-color: #007bff;
  color: white;
  padding: 12px 24px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 16px;
}

.btn-primary:hover {
  background-color: #0056b3;
}

.alert {
  padding: 15px;
  margin: 10px 0;
  border-radius: 4px;
  position: fixed;
  top: 20px;
  right: 20px;
  z-index: 1000;
}

.alert-success {
  background-color: #d4edda;
  color: #155724;
  border: 1px solid #c3e6cb;
}

.alert-danger {
  background-color: #f8d7da;
  color: #721c24;
  border: 1px solid #f5c6cb;
}
```

## 🔄 Alternativa: Backend con MailerSend

Si prefieres más control, puedes crear un endpoint en tu backend:

```python
@app.route('/support-request', methods=['POST'])
def support_request():
    try:
        data = request.get_json()
        
        # Validar datos requeridos
        required_fields = ['name', 'email', 'subject', 'message']
        for field in required_fields:
            if not data.get(field):
                return jsonify({"error": f"Campo requerido: {field}"}), 400
        
        # Crear email de soporte
        from mailersend import Email
        mailer = Email(os.environ.get('MAILERSEND_API_KEY'))
        
        support_email = {
            "from": {
                "email": "noreply@hotelrateshopper.com",
                "name": "Sistema de Soporte"
            },
            "to": [
                {
                    "email": "tu-email@dominio.com",  # Tu email de soporte
                    "name": "Soporte HotelRateShopper"
                }
            ],
            "subject": f"[SOPORTE] {data['subject']} - {data['name']}",
            "html": f"""
            <h2>Nueva solicitud de soporte</h2>
            <p><strong>Nombre:</strong> {data['name']}</p>
            <p><strong>Email:</strong> {data['email']}</p>
            <p><strong>Asunto:</strong> {data['subject']}</p>
            <p><strong>Prioridad:</strong> {data.get('priority', 'Media')}</p>
            <p><strong>Mensaje:</strong></p>
            <p>{data['message']}</p>
            """
        }
        
        response = mailer.send(support_email)
        
        return jsonify({
            "success": True,
            "message": "Solicitud de soporte enviada correctamente"
        })
        
    except Exception as e:
        logger.error(f"Error enviando solicitud de soporte: {e}")
        return jsonify({"error": "Error interno del servidor"}), 500
```

## 📊 Comparación de Opciones

| Servicio | Facilidad | Costo | Control | Spam Protection |
|----------|-----------|-------|---------|-----------------|
| **Formspree** | ⭐⭐⭐⭐⭐ | Gratis | Medio | ✅ |
| **EmailJS** | ⭐⭐⭐⭐ | Gratis | Alto | ⚠️ |
| **Netlify Forms** | ⭐⭐⭐⭐ | Gratis | Medio | ✅ |
| **Backend propio** | ⭐⭐ | Incluido | Máximo | ✅ |

## 🎯 Recomendación Final

**Usa Formspree** para empezar rápido y sin complicaciones. Es la opción más simple y efectiva para tu caso de uso.

¿Te gustaría que te ayude a implementar alguna de estas opciones? 