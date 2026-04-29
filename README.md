## Entrega Parcial 2 — Caso D

### Rama de entrega

`lopez-munoz-cascavita`

### Correcciones implementadas

- Corrección de SQL Injection en backend mediante consultas parametrizadas.
- Autenticación segura con bcrypt, JWT con `sub`, `role`, `exp`, `iat` y `jti`.
- Logout con blacklist de tokens.
- Bloqueo por intentos fallidos.
- RBAC en endpoints del CMS.
- Interceptor HTTP Angular con `Authorization: Bearer {token}`.
- Manejo global de errores 401 y 403.
- Sanitización XSS con DOMPurify.
- Headers de seguridad HTTP en Nginx.
- Análisis SAST con Bearer y SonarQube antes/después.

### Evidencias

Las evidencias se encuentran en `security-reports/`:

- `bearer-antes.html`
- `bearer-antes-summary.png`
- `bearer-despues.html`
- `bearer-despues-summary.png`
- `bearer-frontend-antes.html`
- `bearer-frontend-antes-summary.png`
- `bearer-frontend-despues.html`
- `bearer-frontend-despues-summary.png`
- `sonarqube-antes.png`
- `sonarqube-despues.png`
- `nginx-headers-local.png`
- `analisis-riesgos.md`

### Verificación de headers

```powershell
curl.exe -I http://localhost:8080