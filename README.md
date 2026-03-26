# Bookstore Inventory API

API REST para gestionar el inventario de libros de una librería: altas, consultas, búsquedas, alertas de stock bajo y cálculo de precio de venta en moneda local usando tasas de cambio.

**Stack:** Python 3.11+, Django, Django REST Framework, PostgreSQL (Docker) o SQLite (desarrollo local sin Docker).

---

## Reglas de negocio

### Modelo `Book`

| Campo | Regla |
|--------|--------|
| **ISBN** | Se genera automáticamente al crear el libro (10–13 dígitos numéricos). No es enviable ni editable por el cliente. |
| **cost_usd** | Costo en USD, con 2 decimales. |
| **selling_price_local** | Precio de venta en moneda local; opcional al crear. Se recalcula y persiste al ejecutar el cálculo de precio (ver más abajo). Solo lectura en el API de creación/actualización. |
| **supplier_country** | País del proveedor. Valores permitidos: `US`, `ES`, `VE`, `CO`, `MX`, `AR`. En la API se acepta cualquier combinación de mayúsculas/minúsculas; **se guarda siempre en mayúsculas**. Si el valor no es válido, la respuesta de error incluye la lista de opciones permitidas. |
| **category** | Texto libre. |
| **stock_quantity** | Entero ≥ 0. |

### Listado de libros (`GET /books/`)

- **Paginación opcional:** si no se envía `?page=`, la respuesta es un array con todos los registros. Si se envía `?page=`, la respuesta sigue el formato paginado de DRF (`count`, `next`, `previous`, `results`). Tamaño de página por defecto: 20; se puede ajustar con `page_size` (máximo 100).

### Búsqueda por categoría (`GET /books/search/`)

- **Query:** `category` (obligatorio para filtrar). Si no se envía, se devuelve una lista vacía.

### Stock bajo (`GET /books/low-stock/`)

- **Query:** `threshold` (entero; por defecto `10`).
- Se listan los libros cuyo **`stock_quantity` es menor o igual** al umbral.

### Cálculo de precio (`POST /books/{id}/calculate-price/`)

- **Body JSON:** debe incluir `currency` (código ISO de moneda, p. ej. `EUR`, `VES`). Se normaliza a mayúsculas.
- **Tasa de cambio:** se obtiene de la API externa [ExchangeRate API](https://www.exchangerate-api.com/) (USD como base). Si la llamada **tiene éxito**, la tasa se **guarda o actualiza** en la tabla `ExchangeRate` para esa moneda.
- **Si la API falla:** se usa la tasa almacenada en `ExchangeRate` para esa moneda, si existe; si no, una **tasa por defecto** configurada en código (`3.45`).
- **Cálculo:**  
  - `local_cost = cost_usd × tasa` (redondeo a 2 decimales).  
  - `selling_price_local = local_cost × 1.40` (margen del **40%** sobre el costo local; el multiplicador es 1,40).  
- El resultado se **persiste** en `selling_price_local` del libro. La respuesta incluye desglose (costo USD, moneda, tasa usada, costo local, margen, precio de venta).

### Actualización (`PUT` / `PATCH`)

- **`PUT`** se comporta como **actualización parcial** (equivalente a `PATCH`): no es obligatorio enviar todos los campos.

### Autenticación

- El API está configurado como **público** (sin autenticación), acorde a un entorno de prueba técnica.

---

## Decisiones de implementación (resumen)

- **Proyecto Django mínimo:** sin `django.contrib.admin`, auth ni sesiones en `INSTALLED_APPS`, para reducir tablas y dependencias; DRF configurado con `UNAUTHENTICATED_USER = None` para no requerir `auth`/`contenttypes`.
- **App principal:** `bookstore_inventory` con paquetes `models`, `serializers`, `views` y `utils` (tasas de cambio y paginación).
- **Docker:** servicio `web` (Django) + `db` (PostgreSQL 16), migraciones al arrancar, API expuesta en el puerto **8080** del host.
- **Paginación:** clase `OptionalPageNumberPagination` (solo activa si se envía `page`).
- **Integración externa:** función `fetch_exchange_rate` con SSL (`certifi`) para evitar errores de verificación de certificados.
- **Persistencia de tasas:** modelo `ExchangeRate` como respaldo cuando la API externa no está disponible.

---

## Requisitos previos

- [Docker](https://docs.docker.com/get-docker/) y Docker Compose (o el plugin `docker compose`).
- Opcional: Python 3.11+ y `pip` si ejecutas sin contenedores.

---

## Cómo ejecutar el proyecto (recomendado: Docker)

En la raíz del repositorio:

```bash
docker compose up --build
```

- La API queda en **`http://localhost:8080`**.
- PostgreSQL en el host: **`localhost:5433`** (usuario, contraseña y base definidos en `docker-compose.yml`).

La primera vez (y en cada arranque del contenedor `web`) se ejecutan las migraciones automáticamente.

Para detener:

```bash
docker compose down
```

*(Si usas la CLI antigua: `docker-compose` en lugar de `docker compose`.)*

---

## Ejecución local sin Docker (SQLite)

1. Crear un entorno virtual e instalar dependencias:

   ```bash
   python -m venv venv
   source venv/bin/activate   # Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

2. **No** definir variables `POSTGRES_*` en el entorno; Django usará SQLite (`db.sqlite3` en la raíz del proyecto).

3. Aplicar migraciones y ejecutar el servidor:

   ```bash
   python manage.py migrate
   python manage.py runserver 8080
   ```

La base URL será **`http://localhost:8080`** (ajusta el puerto si usas otro).

---

## Convenciones de URL

El enrutador de DRF usa **barra final** en las rutas. Por ejemplo:

- `POST http://localhost:8080/books/`
- `POST http://localhost:8080/books/1/calculate-price/` (cuerpo JSON con `currency`)

---

## Referencia rápida de endpoints

| Método | Ruta | Descripción |
|--------|------|-------------|
| `GET` | `/books/` | Lista todos los libros o paginada con `?page=` |
| `POST` | `/books/` | Crea un libro |
| `GET` | `/books/{id}/` | Detalle |
| `PUT` / `PATCH` | `/books/{id}/` | Actualización (PUT parcial) |
| `DELETE` | `/books/{id}/` | Elimina |
| `GET` | `/books/search/?category=` | Por categoría |
| `GET` | `/books/low-stock/?threshold=` | Stock ≤ umbral |
| `POST` | `/books/{id}/calculate-price/` | Body: `{"currency": "EUR"}` |

---

## Colección de Postman

En el repositorio está el archivo exportado:

**[`bookstore_inventory_api.postman_collection.json`](./bookstore_inventory_api.postman_collection.json)**

**Cómo importarla en Postman**

1. Abre Postman → **Import**.
2. Arrastra el archivo o elige **Upload Files** y selecciona `bookstore_inventory_api.postman_collection.json` en la raíz del clon.
3. Ajusta la variable de entorno o la URL base si hace falta (por defecto la API en Docker: `http://localhost:8080`).
