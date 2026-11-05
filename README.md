# MercaDemo

Aplicación web para administrar un catálogo de productos y demostrar el patrón
**Write-through Cache** utilizando DynamoDB como base de datos principal y Redis
como sistema de caché.

## ¿Para qué sirve?

MercaDemo permite:

- Crear productos.
- Consultar productos por código.
- Actualizar productos existentes.
- Persistir información en DynamoDB.
- Mantener Redis sincronizado después de cada escritura.
- Medir el tiempo de respuesta de las peticiones.
- Visualizar si una consulta provino de Redis o DynamoDB.
- Observar los estados `CACHE HIT`, `CACHE MISS` y `BYPASS`.

El proyecto sirve como demostración práctica de una arquitectura web con
frontend, API REST, persistencia y caché distribuida.

## Tecnologías utilizadas

### Backend

- Python
- FastAPI
- Uvicorn
- Pydantic Settings
- Boto3
- DynamoDB Local
- Redis
- python-dotenv

### Frontend

- React 19
- React DOM
- Vite
- JavaScript
- Oxlint
- HTML5
- CSS3

### Infraestructura

- Docker
- Docker Compose
- Amazon DynamoDB Local
- Redis 7 Alpine

## Arquitectura

```text
Frontend React
      |
      v
API REST con FastAPI
      |
      v
ProductService
      |
      +--> Repositorio DynamoDB
      |
      +--> Repositorio Redis
```

### Flujo de escritura

Para crear o actualizar un producto:

1. El producto se guarda primero en DynamoDB.
2. Redis se actualiza con la información más reciente.
3. Si Redis no puede sincronizarse, se informa que el producto sí fue
   persistido en DynamoDB.
4. Si existe una copia anterior en Redis, se intenta invalidar.

### Flujo de lectura

Para consultar un producto:

1. Se busca primero en Redis.
2. Si existe, se devuelve desde la caché y se marca como `HIT`.
3. Si no existe, se consulta DynamoDB y se marca como `MISS`.
4. El resultado obtenido desde DynamoDB se guarda nuevamente en Redis.
5. Si Redis no está disponible, la consulta continúa directamente contra
   DynamoDB y se marca como `BYPASS`.

## Estructura del proyecto

```text
demo_market/
├── app/
│   ├── main.py
│   ├── core/
│   │   ├── config.py
│   │   ├── dynamodb.py
│   │   ├── redis.py
│   │   └── request_context.py
│   └── modules/
│       └── products/
│           ├── controller/
│           ├── models/
│           ├── repositories/
│           └── services/
├── docker/
│   └── dynamodb/
├── frontend/
│   ├── src/
│   ├── public/
│   ├── package.json
│   └── vite.config.js
├── scripts/
│   └── create_table.py
├── docker-compose.yml
├── requirements.txt
└── READ.ME
```

## Requisitos previos

- Python 3.10 o superior.
- Node.js 18 o superior.
- npm.
- Docker Desktop.
- Git.

## Configuración del backend

Crear un archivo `.env` en la raíz del proyecto:

```env
AWS_ACCESS_KEY_ID=local
AWS_SECRET_ACCESS_KEY=local
AWS_DEFAULT_REGION=us-east-1

DYNAMODB_ENDPOINT_URL=http://localhost:8000
DYNAMODB_TABLE_NAME=Products

REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0

CACHE_TTL_SECONDS=300
```

Las credenciales `local` son suficientes para trabajar con DynamoDB Local.

## Instalación

### 1. Crear el entorno virtual

En Windows:

```powershell
python -m venv .venv
.venv\Scripts\activate
```

En Linux o macOS:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 2. Instalar dependencias del backend

Desde la raíz del proyecto:

```bash
pip install -r requirements.txt
```

### 3. Instalar dependencias del frontend

```bash
cd frontend
npm install
cd ..
```

## Iniciar los servicios

Desde la raíz del proyecto:

```bash
docker compose up -d
```

Esto inicia:

| Servicio | Dirección | Puerto |
|---|---|---:|
| DynamoDB Local | `http://localhost:8000` | 8000 |
| Redis | `localhost` | 6379 |

Verificar el estado de los contenedores:

```bash
docker compose ps
```

Detener los servicios:

```bash
docker compose down
```

## Crear la tabla de productos

Con Docker ejecutándose y el entorno virtual activado:

```bash
python scripts/create_table.py
```

El script crea la tabla `Products` con la siguiente clave primaria:

```text
productId: String
```

Si la tabla ya existe, el script lo informa y no realiza cambios.

## Ejecutar el backend

Desde la raíz del proyecto:

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8090
```

El backend estará disponible en:

```text
http://localhost:8090
```

Documentación interactiva:

```text
http://localhost:8090/docs
```

Documentación alternativa:

```text
http://localhost:8090/redoc
```

## Ejecutar el frontend

En otra terminal:

```bash
cd frontend
npm run dev
```

La aplicación estará disponible normalmente en:

```text
http://localhost:5173
```

El frontend utiliza por defecto la API:

```text
http://localhost:8090/api
```

Para cambiar la URL de la API, crear `frontend/.env`:

```env
VITE_API_URL=http://localhost:8090/api
```

## API REST

### Crear producto

```http
POST /api/products
Content-Type: application/json
```

Ejemplo:

```json
{
  "product_id": "LEC-001",
  "name": "Leche entera",
  "category": "Lácteos",
  "price": 4500,
  "stock": 25
}
```

Respuesta exitosa: `201 Created`.

### Consultar producto

```http
GET /api/products/{product_id}
```

Ejemplo:

```bash
curl http://localhost:8090/api/products/LEC-001
```

La API incluye estos encabezados:

```text
X-Cache: HIT
X-Process-Time-Ms: 1.25
```

Valores posibles de `X-Cache`:

- `HIT`: producto encontrado en Redis.
- `MISS`: producto consultado en DynamoDB porque no estaba en Redis.
- `BYPASS`: Redis no estaba disponible y se consultó DynamoDB.
- `-`: operación sin consulta de caché.

### Actualizar producto

```http
PUT /api/products/{product_id}
Content-Type: application/json
```

Ejemplo:

```json
{
  "name": "Leche entera premium",
  "category": "Productos lácteos",
  "price": 5000,
  "stock": 30
}
```

Respuesta exitosa: `200 OK`.

## Validaciones

- `product_id`: entre 3 y 64 caracteres.
- `product_id`: solo letras, números, guion y guion bajo.
- `name`: entre 2 y 120 caracteres.
- `category`: entre 5 y 120 caracteres.
- `price`: número entero mayor o igual a cero.
- `stock`: número entero mayor o igual a cero.

## Manejo de errores

| Situación | Código HTTP |
|---|---:|
| Producto creado correctamente | 201 |
| Consulta o actualización exitosa | 200 |
| Producto no encontrado | 404 |
| Producto duplicado | 409 |
| Error de DynamoDB | 503 |
| Error de sincronización con Redis | 503 |
| Error de validación | 422 |

## Funcionalidades del frontend

La interfaz permite:

- Buscar productos por código.
- Crear nuevos productos.
- Editar productos existentes.
- Visualizar precio, categoría y stock.
- Identificar productos con stock bajo.
- Consultar estadísticas de peticiones.
- Visualizar cantidad de `Cache HIT` y `Cache MISS`.
- Consultar el tiempo promedio de respuesta del servidor.
- Revisar un registro de peticiones realizadas.

## Comandos disponibles

### Backend

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8090
python scripts/create_table.py
```

### Frontend

```bash
npm run dev
npm run build
npm run lint
npm run preview
```

## Construir el frontend para producción

```bash
cd frontend
npm run build
```

Los archivos generados estarán en `frontend/dist/`.

Para previsualizar la compilación:

```bash
npm run preview
```

## Verificación rápida

1. Iniciar Docker:

   ```bash
   docker compose up -d
   ```

2. Crear la tabla:

   ```bash
   python scripts/create_table.py
   ```

3. Iniciar el backend:

   ```bash
   uvicorn app.main:app --reload --port 8090
   ```

4. Iniciar el frontend:

   ```bash
   cd frontend
   npm run dev
   ```

5. Abrir `http://localhost:5173`.

6. Crear un producto y consultarlo dos veces:

   ```text
   Primera consulta: CACHE MISS
   Segunda consulta: CACHE HIT
   ```

## Licencia

Este proyecto se distribuye con fines educativos y demostrativos. 