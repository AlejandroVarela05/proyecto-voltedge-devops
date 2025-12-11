# ⚡ VoltEdge - Sistema de Gestión de Estaciones de Carga

**Autores:** **Alejandro Varela, Yésica Ramirez y Yago Alonso**

**API REST completa con autenticación JWT para gestión de estaciones de carga de vehículos eléctricos.**

---

## 📋 Características

✅ **Autenticación JWT** - Sistema completo de registro, login y tokens seguros  
✅ **Hash de Contraseñas con Argon2** - Seguridad superior a bcrypt  
✅ **Gestión de Usuarios** - Tipos: Individual, Empresa y Admin con roles diferenciados  
✅ **Estaciones de Carga** - CRUD completo con disponibilidad en tiempo real  
✅ **Cargadores** - Gestión de cargadores rápidos y normales  
✅ **Sesiones de Carga** - Inicio/fin automático con facturación y descuento de saldo  
✅ **Mantenimientos** - Preventivos y correctivos con seguimiento completo  
✅ **Reportes** - Consumo, disponibilidad e historial detallado  
✅ **Tarifas Diferenciadas** - Individual (0.30€/kWh) vs Empresa (0.25€/kWh)  
✅ **Documentación Automática** - Swagger UI y ReDoc interactivos  
✅ **Contenerización Docker** - Despliegue fácil y portable  

---

## 🏗️ Estructura del Proyecto

```
VoltEdge/
├── models/                 # Modelos de dominio
│   ├── __init__.py
│   ├── user.py           # Usuario (con password_hash, saldo y tarifas)
│   ├── station.py        # Estaciones de carga
│   ├── charger.py        # Cargadores individuales
│   ├── session.py        # Sesiones de carga
│   └── maintenance.py    # Registros de mantenimiento
├── services/              # Lógica de negocio
│   ├── __init__.py
│   ├── service.py        # Servicio principal (diccionarios + métodos)
│   └── auth_service.py   # Autenticación JWT y Argon2
├── schemas/               # Esquemas Pydantic para validación
│   ├── __init__.py
│   ├── auth_schemas.py
│   ├── user_schemas.py
│   ├── station_schemas.py
│   ├── charger_schemas.py
│   ├── session_schemas.py
│   └── maintenance_schemas.py
├── main.py                # API REST con FastAPI
├── main_demo.py           # Demo CLI original (sin API)
├── requirements.txt       # Dependencias Python con versiones fijadas
├── Dockerfile             # Configuración Docker profesional
├── .dockerignore          # Archivos excluidos de la imagen Docker
├── .gitignore             # Archivos excluidos del repositorio Git
└── README.md              # Este archivo
```

---

## 🚀 Instalación Local

### Prerrequisitos

- Python 3.12 o superior
- pip (gestor de paquetes de Python)

### 1. Clonar el repositorio

```bash
git clone https://github.com/AlejandroVarela05/proyecto-voltedge-devops.git
cd proyecto-voltedge-devops
```

### 2. Crear entorno virtual (recomendado)

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

### 3. Instalar dependencias

```bash
pip install -r requirements.txt
```

---

## 🎯 Ejecución

### Opción 1: Ejecutar la API REST (recomendado)

```bash
python main.py
```

O con uvicorn directamente:

```bash
uvicorn main:app --reload
```

La API estará disponible en:
- **Swagger UI (interactiva):** http://localhost:8000/docs
- **ReDoc (documentación):** http://localhost:8000/redoc
- **API Root:** http://localhost:8000

### Opción 2: Ejecutar demo CLI original (sin API)

```bash
python main_demo.py
```

---

## 🐳 Docker

### Construcción de la Imagen

```bash
# Construir la imagen con tag latest
docker build -t voltedge:latest .

# Construir con versión específica
docker build -t voltedge:1.0.0 .

# Ver la imagen creada
docker images | grep voltedge
```

### Ejecución del Contenedor

#### Modo básico (background)

```bash
# Ejecutar en segundo plano
docker run -d --name voltedge -p 8000:8000 voltedge:latest

# Ver logs en tiempo real
docker logs -f voltedge

# Detener el contenedor
docker stop voltedge

# Eliminar el contenedor
docker rm voltedge
```

#### Modo interactivo (foreground)

```bash
# Útil para ver logs inmediatos durante desarrollo
docker run --rm --name voltedge-test -p 8000:8000 voltedge:latest
# Presiona Ctrl+C para detener (se elimina automáticamente con --rm)
```

#### Con variables de entorno

```bash
docker run -d --name voltedge \
  -p 8000:8000 \
  -e JWT_SECRET_KEY="tu-clave-secreta-super-segura-cambiar-en-produccion" \
  -e JWT_ALGORITHM="HS256" \
  -e ACCESS_TOKEN_EXPIRE_MINUTES="30" \
  voltedge:latest
```

### Variables de Entorno Soportadas

| Variable | Descripción | Valor por Defecto |
|----------|-------------|-------------------|
| `JWT_SECRET_KEY` | Clave secreta para firmar tokens JWT | Generada aleatoriamente |
| `JWT_ALGORITHM` | Algoritmo de encriptación JWT | `HS256` |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Tiempo de expiración del token (minutos) | `30` |

> ⚠️ **IMPORTANTE**: En producción, SIEMPRE usa variables de entorno para `JWT_SECRET_KEY` y NUNCA la incluyas en el código fuente.

### Salida Esperada

Al ejecutar el contenedor correctamente, deberías ver:

```
INFO:     Started server process [1]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
```

### Comandos Útiles de Docker

```bash
# Ver contenedores en ejecución
docker ps

# Ver TODOS los contenedores (incluso detenidos)
docker ps -a

# Ver logs de un contenedor
docker logs voltedge

# Acceder al contenedor (shell interactivo)
docker exec -it voltedge /bin/bash

# Eliminar contenedores detenidos
docker container prune

# Eliminar imágenes sin usar
docker image prune

# Limpiar todo el sistema Docker (cuidado)
docker system prune -a
```

---

## 📚 Uso de la API

### 1️⃣ Registrar un Usuario

**Endpoint:** `POST /auth/registro`

```json
{
  "name": "María López",
  "email": "maria@voltedge.com",
  "password": "password123",
  "user_type": "individual",
  "saldo_inicial": 100.0
}
```

**Tipos de usuario:**
- `individual` - Tarifa: 0.30€/kWh
- `empresa` - Tarifa: 0.25€/kWh
- `admin` - Permisos completos de gestión

### 2️⃣ Hacer Login

**Endpoint:** `POST /auth/token`

**Form Data:**
- `username`: maria@voltedge.com (email)
- `password`: password123

**Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

### 3️⃣ Autenticarse en Swagger

1. Abre http://localhost:8000/docs
2. Haz clic en el botón **"Authorize"** 🔓 (arriba a la derecha)
3. Introduce:
   - `username`: tu email
   - `password`: tu contraseña
4. Haz clic en **"Authorize"**
5. ¡Listo! Ahora puedes usar endpoints protegidos

### 4️⃣ Crear una Estación (Admin)

**Endpoint:** `POST /stations`  
**Requiere:** Autenticación + Admin

```json
{
  "id": 1,
  "name": "Estación Centro Vigo",
  "location": "Calle Príncipe 25, Vigo"
}
```

### 5️⃣ Añadir Cargadores (Admin)

**Endpoint:** `POST /stations/{station_id}/chargers`  
**Requiere:** Autenticación + Admin

```json
{
  "charger_id": 101,
  "charger_type": "rápido"
}
```

### 6️⃣ Iniciar Sesión de Carga

**Endpoint:** `POST /sessions`  
**Requiere:** Autenticación

```json
{
  "user_id": "123e4567-e89b-12d3-a456-426614174000",
  "station_id": 1
}
```

### 7️⃣ Finalizar Sesión

**Endpoint:** `POST /sessions/cerrar`  
**Requiere:** Autenticación

```json
{
  "user_id": "123e4567-e89b-12d3-a456-426614174000"
}
```

Al finalizar, se calcula automáticamente:
- ⚡ kWh consumidos (0.5 kWh/min)
- 💰 Coste según tarifa del usuario
- 💳 Descuento automático del saldo

### 8️⃣ Recargar Saldo

**Endpoint:** `POST /users/{user_id}/recargar-saldo`  
**Requiere:** Autenticación (solo propio usuario)

```json
{
  "cantidad": 50.0
}
```

### 9️⃣ Ver Historial de Sesiones

**Endpoint:** `GET /users/{user_id}/historial`  
**Requiere:** Autenticación (solo propio usuario o admin)

**Response:**
```json
[
  {
    "session_id": "abc123",
    "station_name": "Estación Centro Vigo",
    "start_time": "2024-12-11T10:30:00",
    "end_time": "2024-12-11T11:00:00",
    "energy_consumed_kwh": 15.0,
    "cost": 4.50
  }
]
```

---

## 📊 Endpoints Disponibles

### 🔐 Autenticación
- `POST /auth/registro` - Registrar usuario nuevo
- `POST /auth/token` - Login (obtener JWT)
- `GET /auth/me` - Obtener información del usuario actual

### 👥 Usuarios
- `GET /users` - Listar todos los usuarios (admin)
- `GET /users/{id}` - Obtener usuario específico
- `POST /users/{id}/recargar-saldo` - Recargar saldo
- `GET /users/{id}/historial` - Historial de sesiones del usuario

### 🏢 Estaciones
- `POST /stations` - Crear estación (admin)
- `GET /stations` - Listar todas las estaciones
- `GET /stations/{id}` - Obtener estación específica
- `DELETE /stations/{id}` - Eliminar estación (admin)
- `GET /stations/{id}/disponibilidad` - Ver disponibilidad en tiempo real
- `GET /stations/{id}/reporte-consumo` - Reporte de consumo (admin)

### ⚡ Cargadores
- `POST /stations/{id}/chargers` - Añadir cargador a estación (admin)
- `GET /chargers` - Listar todos los cargadores
- `GET /chargers/{id}` - Obtener cargador específico

### 🔌 Sesiones de Carga
- `POST /sessions` - Iniciar sesión de carga
- `POST /sessions/cerrar` - Finalizar sesión y facturar

### 🔧 Mantenimiento
- `POST /maintenance` - Programar mantenimiento (admin)
- `GET /maintenance` - Listar todos los mantenimientos (admin)
- `POST /maintenance/{id}/iniciar` - Iniciar mantenimiento programado (admin)
- `POST /maintenance/{id}/completar` - Completar mantenimiento (admin)

---

## 🔒 Autenticación y Permisos

| Endpoint | Público | Usuario | Admin |
|----------|---------|---------|-------|
| `POST /auth/registro` | ✅ | ✅ | ✅ |
| `POST /auth/token` | ✅ | ✅ | ✅ |
| `GET /auth/me` | ❌ | ✅ | ✅ |
| `GET /stations` | ✅ | ✅ | ✅ |
| `POST /stations` | ❌ | ❌ | ✅ |
| `DELETE /stations/{id}` | ❌ | ❌ | ✅ |
| `GET /users` | ❌ | ❌ | ✅ |
| `POST /sessions` | ❌ | ✅ | ✅ |
| `POST /maintenance` | ❌ | ❌ | ✅ |
| `GET /users/{id}/historial` | ❌ | ✅ (propio) | ✅ (todos) |

---

## 🧪 Pruebas Completas

### Ejemplo con curl

```bash
# 1. Registrar usuario individual
curl -X POST "http://localhost:8000/auth/registro" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Test User",
    "email": "test@example.com",
    "password": "Test123!",
    "user_type": "individual",
    "saldo_inicial": 100.0
  }'

# 2. Login
curl -X POST "http://localhost:8000/auth/token" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=test@example.com&password=Test123!"

# 3. Usar el token en peticiones protegidas
curl -X GET "http://localhost:8000/auth/me" \
  -H "Authorization: Bearer <tu-token-aqui>"

# 4. Ver estaciones disponibles
curl http://localhost:8000/stations
```

### Secuencia de prueba completa:

1. ✅ **Registrar usuarios:**
   - Usuario individual
   - Usuario empresa
   - Usuario admin

2. ✅ **Login y obtener tokens JWT**

3. ✅ **Crear infraestructura (como admin):**
   - Crear estaciones
   - Añadir cargadores a las estaciones

4. ✅ **Iniciar sesión de carga (como usuario)**

5. ✅ **Finalizar sesión y verificar:**
   - Cálculo de kWh
   - Facturación correcta según tarifa
   - Descuento de saldo

6. ✅ **Recargar saldo**

7. ✅ **Programar y gestionar mantenimiento (como admin)**

8. ✅ **Ver reportes y historial**

---

## 🛠️ Tecnologías Utilizadas

- **Python 3.12** - Lenguaje de programación
- **FastAPI** - Framework web moderno y de alto rendimiento
- **Pydantic** - Validación de datos con type hints
- **python-jose[cryptography]** - Manejo de tokens JWT
- **passlib[argon2]** - Hashing seguro de contraseñas (superior a bcrypt)
- **Uvicorn** - Servidor ASGI de alto rendimiento
- **Docker** - Contenerización y despliegue

---

## 📦 Dependencias

Las dependencias están especificadas en `requirements.txt` con versiones fijadas:

```
fastapi==0.115.5
uvicorn==0.32.1
pydantic==2.10.3
python-jose[cryptography]==3.3.0
passlib[argon2]==1.7.4
python-multipart==0.0.20
```

Para actualizar dependencias:

```bash
pip install --upgrade -r requirements.txt
pip freeze > requirements.txt
```

---

## 📝 Notas de Desarrollo

### Diferencias entre tipos de usuario:

| Característica | Individual | Empresa | Admin |
|----------------|-----------|---------|-------|
| Tarifa por kWh | 0.30€ | 0.25€ | N/A |
| Gestión de estaciones | ❌ | ❌ | ✅ |
| Programar mantenimiento | ❌ | ❌ | ✅ |
| Ver reportes completos | ❌ | ❌ | ✅ |
| Ver todos los usuarios | ❌ | ❌ | ✅ |

### Seguridad Implementada:

- ✅ **Contraseñas hasheadas con Argon2** (ganador de la competición Password Hashing Competition 2015)
- ✅ **Tokens JWT** con expiración configurable (default: 30 minutos)
- ✅ **Verificación de emails duplicados** en registro
- ✅ **Control de acceso basado en roles** (RBAC)
- ✅ **Usuario no-root en Docker** para mayor seguridad
- ✅ **Variables de entorno** para secretos (no hardcoded)
- ✅ **Validación exhaustiva** con Pydantic schemas
- ✅ **Health check** en contenedor Docker

---

## 👨‍💻 Desarrollo y Git

### Commits Convencionales

Este proyecto sigue la especificación de [Conventional Commits](https://www.conventionalcommits.org/):

- `feat:` Nueva funcionalidad
- `fix:` Corrección de bug
- `docs:` Cambios en documentación
- `chore:` Tareas de mantenimiento
- `refactor:` Refactorización de código
- `test:` Añadir o modificar tests

### Flujo de Trabajo con Git

```bash
# Crear rama para nueva feature
git checkout -b feature/nombre-feature

# Hacer commits pequeños y descriptivos
git add .
git commit -m "feat(api): add new endpoint for charging stations"

# Subir rama
git push origin feature/nombre-feature

# Crear Pull Request en GitHub
# Revisar código
# Mergear a main
```

### Buenas Prácticas:

- ✅ Commits pequeños y descriptivos
- ✅ Una rama por feature con vida corta
- ✅ Pull Requests con descripción clara
- ✅ Revisión de código antes de mergear
- ✅ Protección de rama `main` (requiere PR aprobado)

---

## 🔒 Consideraciones de Seguridad

### En Producción:

1. **NUNCA uses valores por defecto** para `JWT_SECRET_KEY`
2. **Genera claves aleatorias fuertes:**
   ```bash
   openssl rand -hex 32
   ```
3. **Usa HTTPS** siempre en producción
4. **Configura CORS** apropiadamente
5. **Limita rate limiting** para prevenir ataques
6. **Mantén dependencias actualizadas** regularmente
7. **Usa variables de entorno** para todos los secretos
8. **Habilita logs** de seguridad y auditoría

---

## 📄 Licencia

Este proyecto es parte de un trabajo académico para la asignatura de Arquitectura del Software en UIE (Universidad Intercontinental de la Empresa).

---

## 👤 Autores

**Alejandro Varela, Yesica Ramirez y Yago Alonso**
- Email: alejandro.varela.01@uie.edu
- Email: yesica.ramirez.01@uie.edu
- Email: yago.alonso_fueyo.01@uie.edu
- GitHub: [@AlejandroVarela05](https://github.com/AlejandroVarela05)
- Repositorio: https://github.com/AlejandroVarela05/proyecto-voltedge-devops

---

## 🙏 Agradecimientos

Proyecto desarrollado como parte del curso de Arquitectura del Software en la UIE.

Agradecimientos especiales al equipo de desarrollo y a el profesor por su guía en la implementación de prácticas DevOps modernas.

---

## 📞 Soporte

Para dudas, problemas o sugerencias:
1. Abre un **Issue** en GitHub
2. Revisa la **documentación Swagger** en `/docs`
3. Consulta los logs del contenedor Docker

---

**⭐ Si este proyecto te ha sido útil, considera darle una estrella en GitHub!**

**⚡🚗 ¡Gracias por usar VoltEdge!**
