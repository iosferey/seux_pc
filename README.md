# SEUX-PC: Evaluación UX de Alineación Cultural

Sistema para evaluar sitios web combinando:

- Heurísticas UX.
- Dimensiones culturales de Hofstede.
- Análisis visual automatizado con Playwright.
- Evaluación asistida con OpenAI.

## Requisitos

Instalar dependencias:

```bash
pip install -r requirements.txt
playwright install chromium
```

Configurar la API key:

```bash
export OPENAI_API_KEY="tu_api_key"
```

También puede cargarse desde un archivo `.env` en la raíz del proyecto.

## Análisis De Una URL

Ejecutar:

```bash
python3 scripts/run_single.py --url https://example.com
```

Opcionalmente se puede forzar el país objetivo:

```bash
python3 scripts/run_single.py --url https://example.com --country MEX
python3 scripts/run_single.py --url https://example.com --country Mexico
```

Si `--country` se omite, el sistema intenta inferir el país objetivo desde la URL, metadatos HTML, contenido del sitio y, si hay API key disponible, OpenAI.

El análisis individual incluye recomendaciones en el JSON final.

## Análisis Batch

Ejecutar el lote por default:

```bash
python3 scripts/run_batch.py
```

Ejecutar desde CSV:

```bash
python3 scripts/run_batch.py --csv lote.csv
```

Por default, el batch usa `MEX` como país objetivo para todos los sitios.

Para elegir otro país objetivo:

```bash
python3 scripts/run_batch.py --csv lote.csv --country USA
python3 scripts/run_batch.py --csv lote.csv --country Spain
```

Para inferir el país objetivo por sitio:

```bash
python3 scripts/run_batch.py --csv lote.csv --country auto
```

El batch no genera recomendaciones por sitio, para reducir costo y tiempo de ejecución.

## Formato Del CSV Batch

Formato mínimo:

```csv
url
https://stripe.com
https://airbnb.com
https://apple.com
```

Se permiten columnas adicionales para organización interna:

```csv
url,grupo,notas
# SaaS / fintech,,
stripe.com,SaaS / fintech,Referencia global
https://airbnb.com,Turismo,Marketplace internacional
,
# Gobierno,,
https://www.gob.mx,Gobierno,Sitio público mexicano
```

Reglas:

- La columna `url` es obligatoria.
- Filas con `url` vacío se ignoran.
- Filas donde `url` empieza con `#` se ignoran.
- URLs sin protocolo se normalizan a `https://`.
- Columnas adicionales como `grupo` o `notas` no afectan el análisis.

## Salidas

Cada sitio genera un JSON independiente en `outputs/`:

```text
outputs/{dominio}_{YYYYMMDD_HHMMSS}.json
```

El batch también genera un resumen con timestamp:

```text
outputs/summary_{YYYYMMDD_HHMMSS}.csv
```

Campos principales del JSON:

```json
{
  "ICH": 0.72,
  "IAC": 0.68,
  "IVS": 0.59,
  "Brecha": -0.03,
  "transferencia_cultural": 0.70,
  "pais_origen": "USA",
  "pais_origen_nombre": "U.S.A.",
  "pais_objetivo": "MEX",
  "pais_objetivo_nombre": "Mexico",
  "visual_analysis": {},
  "heuristics": {}
}
```

En análisis individual puede incluir además:

```json
{
  "recomendaciones": {}
}
```

## Matriz Hofstede

La matriz cultural está en:

```text
seuxpc/config/hofstede.py
```

Incluye 111 perfiles del CSV de Hofstede, con:

- `country_code`: código canónico del dataset, por ejemplo `MEX`, `USA`, `SPA`.
- `country`: nombre completo del país o región.
- `DP`, `IND`, `EI`, `OLP`, `LCS`, `OGI`: dimensiones normalizadas.

Los valores `#NULL!` del CSV se conservan como `None`. El sistema evita romper cálculos cuando faltan dimensiones.

También existen alias para aceptar entradas comunes como:

- `MX`, `Mexico`, `México` -> `MEX`
- `US`, `United States`, `U.S.A.` -> `USA`
- `ES`, `Spain`, `España` -> `SPA`
- `UK`, `United Kingdom`, `Great Britain` -> `GBR`

## Índices Calculados

- `ICH`: índice de calidad heurística.
- `IAC`: índice de alineación cultural.
- `IVS`: índice visual.
- `Brecha`: diferencia entre UX base y UX ajustada culturalmente.
- `transferencia_cultural`: similitud cultural entre país origen y país objetivo.
