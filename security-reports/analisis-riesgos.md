# Análisis de Riesgos de Seguridad — Noticias 360

## Riesgo 1: SQL Injection en backend

**Amenaza:** atacante externo o usuario autenticado malicioso que intenta manipular consultas SQL.  
**Vulnerabilidad:** consultas SQL construidas dinámicamente en autenticación y CMS.  
**Vector de ataque:** envío de valores manipulados en email, contraseña o identificadores de artículos.

| Dimensión | Valor | Justificación |
|---|---|---|
| Probabilidad | Alta | Bearer lo detectó inicialmente como hallazgo crítico. |
| Impacto CIA | C: Alta · I: Alta · D: Media | Puede exponer datos, alterar artículos o afectar consultas. |
| Nivel de riesgo | Alto | Alta probabilidad y alto impacto. |

**Control propuesto:**  
- Tipo: Preventivo  
- Control: consultas parametrizadas  
- Capa: aplicación / base de datos  
- Estado: Implementado  
- Evidencia: `backend/src/auth/router.py`, `backend/src/cms/router.py`

---

## Riesgo 2: XSS en editor CMS

**Amenaza:** usuario con acceso al CMS que intenta insertar HTML o JavaScript malicioso.  
**Vulnerabilidad:** renderizado de HTML enriquecido mediante `[innerHTML]`.  
**Vector de ataque:** contenido con scripts, iframes o eventos como `onclick`, `onerror` u `onload`.

| Dimensión | Valor | Justificación |
|---|---|---|
| Probabilidad | Media | El CMS permite editar contenido HTML. |
| Impacto CIA | C: Alta · I: Alta · D: Baja | Puede robar tokens o alterar contenido visualizado. |
| Nivel de riesgo | Alto | Alto impacto sobre confidencialidad e integridad. |

**Control propuesto:**  
- Tipo: Preventivo  
- Control: sanitización con DOMPurify y CSP  
- Capa: frontend / navegador / servidor web  
- Estado: Implementado  
- Evidencia: `frontend/src/app/cms/cms-editor.component.ts`, `infra/nginx.conf`

---

## Riesgo 3: Uso indebido o robo de JWT

**Amenaza:** atacante que obtiene o manipula un token JWT.  
**Vulnerabilidad:** tokens sin expiración corta, sin `jti`, sin blacklist o enviados incorrectamente.  
**Vector de ataque:** uso de token robado, token manipulado o token no invalidado después del logout.

| Dimensión | Valor | Justificación |
|---|---|---|
| Probabilidad | Media | El sistema usa JWT para autenticación. |
| Impacto CIA | C: Alta · I: Alta · D: Media | Permitiría acceso indebido y acciones no autorizadas. |
| Nivel de riesgo | Alto | Compromete autenticación y autorización. |

**Control propuesto:**  
- Tipo: Preventivo y correctivo  
- Control: JWT con `sub`, `role`, `exp`, `iat`, `jti`, blacklist y logout  
- Capa: autenticación backend  
- Estado: Implementado  
- Evidencia: `backend/src/auth/auth_service.py`, `backend/src/auth/rbac.py`, `frontend/src/app/shared/interceptors/auth.interceptor.ts`

---

## Riesgo 4: Elevación de privilegios en publicación de artículos

**Amenaza:** usuario con rol bajo que intenta publicar artículos.  
**Vulnerabilidad:** ausencia de control de roles en endpoints privilegiados.  
**Vector de ataque:** petición directa a `POST /api/cms/articulo/{id}/publicar`.

| Dimensión | Valor | Justificación |
|---|---|---|
| Probabilidad | Media | Un usuario autenticado podría intentar acceder a endpoints privilegiados. |
| Impacto CIA | C: Media · I: Alta · D: Baja | Afecta la integridad editorial del sistema. |
| Nivel de riesgo | Alto | Publicar sin autorización compromete el flujo editorial. |

**Control propuesto:**  
- Tipo: Preventivo  
- Control: RBAC con `verify_role()`  
- Capa: backend / frontend  
- Estado: Implementado  
- Evidencia: `backend/src/auth/rbac.py`, `backend/src/cms/router.py`, `frontend/src/app/cms/cms-editor.component.ts`

---

## Riesgo 5: Exposición de fuentes confidenciales

**Amenaza:** usuario no autorizado que intenta consultar fuentes periodísticas.  
**Vulnerabilidad:** carga masiva o filtrado manipulable de fuentes.  
**Vector de ataque:** solicitud manual o botón de carga total de fuentes.

| Dimensión | Valor | Justificación |
|---|---|---|
| Probabilidad | Media | El caso maneja fuentes confidenciales. |
| Impacto CIA | C: Alta · I: Media · D: Baja | La exposición de fuentes afecta gravemente la confidencialidad. |
| Nivel de riesgo | Alto | El activo protegido es altamente sensible. |

**Control propuesto:**  
- Tipo: Preventivo  
- Control: eliminación de carga masiva en frontend y autorización estricta en backend  
- Capa: frontend / backend / datos  
- Estado: Parcialmente implementado  
- Evidencia: `frontend/src/app/cms/cms-editor.component.ts`

---

# Matriz de riesgos 3x3

| Probabilidad \ Impacto | Bajo | Medio | Alto |
|---|---|---|---|
| Alta | — | — | Riesgo 1 |
| Media | — | — | Riesgos 2, 3, 4 y 5 |
| Baja | — | — | — |