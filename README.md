# Taller: Green Code en la practica

**Optimizacion energetica · ISO/IEC 21031:2024 · 5 modulos · 55 tests**

---

## Metricas del taller

| Modulos | Tests totales | Metrica objetivo | Duracion estimada |
|---------|--------------|-------------------|-------------------|
| 5       | 55           | SCI              | ~6h               |

---

## La metrica: SCI

```
SCI = ((E x I) + M) / R
```

- **E** = Energia consumida (kWh)
- **I** = Intensidad de carbono de la red electrica (gCO2/kWh)
- **M** = Emisiones embebidas del hardware
- **R** = Unidad funcional (requests procesados, operaciones, etc.)

El **SCI** (_Software Carbon Intensity_) es el estandar de la Green Software Foundation para medir la huella de carbono del software.

---

## Estructura del taller

```
taller sostenibilidad/
├── README.md
├── pyproject.toml
├── Dockerfile
├── .dockerignore
├── src/
│   └── taller_green_code/
│       ├── __init__.py
│       ├── modulo1_algoritmos.py    # Complejidad algoritmica
│       ├── modulo2_cache.py         # Cache y memorizacion
│       ├── modulo3_estructuras.py   # Estructuras de datos
│       ├── modulo4_carbon.py        # Carbon awareness
│       └── modulo5_sci.py           # Medicion SCI real
└── tests/
    ├── conftest.py
    ├── test_modulo1.py
    ├── test_modulo2.py
    ├── test_modulo3.py
    ├── test_modulo4.py
    └── test_modulo5.py
```

---

## Modulo 1: Complejidad algoritmica y consumo energetico

**Contexto**: sistema de analisis de logs que procesa 10 millones de entradas por noche. Version actual: 47 min, 2.3 kWh. Objetivo: reducir SCI al menos 60%.

### Ejercicio 1.1 — Busqueda en logs

Reemplazar busqueda lineal O(n) por busqueda binaria O(log n) sin usar `bisect`.

```python
from taller_green_code.modulo1_algoritmos import buscar_log_verde

logs = [{'id': '1', 'ts': 100}, {'id': '2', 'ts': 200}]
resultado = buscar_log_verde(logs, 100)  # O(log n)
```

| Version contaminante | Version verde | Mejora |
|---------------------|---------------|--------|
| O(n) por busqueda   | O(log n)      | Exponencial para n grande |

### Ejercicio 1.2 — Deduplicacion eficiente

Reemplazar busqueda lineal oculta O(n^2) por tracking con set O(n).

```python
from taller_green_code.modulo1_algoritmos import dedup_verde

resultado = dedup_verde(logs_duplicados)  # O(n) tiempo, O(n) espacio
```

### Ejercicio 1.3 — Top-K logs por severidad

Reemplazar sort completo O(n log n) por heap de tamano k O(n log k).

```python
from taller_green_code.modulo1_algoritmos import top_k_verde

top_10 = top_k_verde(logs, 10)  # Heap implementado manualmente
```

---

## Modulo 2: Cache, memorizacion y computacion lazy

**Contexto**: motor de recomendaciones con 50k usuarios activos, 18 kWh/hora. El 73% de calculos son repetidos.

### Ejercicio 2.1 — Fibonacci energetico

Tres implementaciones con distinto perfil energetico:

```python
from taller_green_code.modulo2_cache import fib_memo, fib_iterativo, fib_matrix

fib_memo(30)       # O(n) tiempo y espacio, memoizacion con dict
fib_iterativo(30)  # O(n) tiempo, O(1) espacio
fib_matrix(30)     # O(log n) tiempo, O(1) espacio — exponenciacion de matrices
```

**Recomendacion para produccion**: `fib_iterativo` para la mayoria de casos; `fib_matrix` si n > 10^5.

### Ejercicio 2.2 — Cache LRU desde cero

Cache LRU con lista doblemente enlazada + hash map, O(1) en get y set, thread-safe.

```python
from taller_green_code.modulo2_cache import LRUCache

cache = LRUCache(1000)
cache.set('user_123', score)
score = cache.get('user_123')
print(cache.stats())  # {'hits': 45, 'misses': 12, 'hit_rate': 0.79}
```

### Ejercicio 2.3 — Generadores lazy vs listas

Pipeline de recomendaciones que nunca carga mas de ~200 usuarios en memoria.

```python
from taller_green_code.modulo2_cache import pipeline_verde, pipeline_paralelo

top_scores = pipeline_verde(user_ids)              # Generadores lazy
top_scores = pipeline_paralelo(user_ids, workers=4) # Con ThreadPoolExecutor
```

---

## Modulo 3: Estructuras de datos y acceso a disco

**Contexto**: pipeline ETL de 8GB. Cada byte de I/O innecesario tiene un costo real de carbono.

### Ejercicio 3.1 — Patricia Trie para URLs

Trie comprimido que reduce uso de RAM a <=30% del dict equivalente.

```python
from taller_green_code.modulo3_estructuras import PatriciaTrie

trie = PatriciaTrie()
trie.insert('/api/v2/users/123')
trie.search('/api/v2/users/123')         # True
trie.starts_with('/api/v2/')             # ['/api/v2/users/123']
print(trie.memory_footprint())           # bytes aproximados
```

### Ejercicio 3.2 — Bloom Filter

Filtro probabilistico para deduplicacion sin almacenar elementos. Para 1M elementos con fp_rate=0.01 usa <2MB.

```python
from taller_green_code.modulo3_estructuras import BloomFilter

bf = BloomFilter(n=1_000_000, fp_rate=0.01)
bf.add('event_id_12345')
'event_id_12345' in bf  # True
'nuevo_evento' in bf     # Probablemente False (garantia: sin falsos negativos)
```

### Ejercicio 3.3 — Procesamiento CSV por chunks

Algoritmo de Welford para media/varianza en streaming + reservoir sampling para percentiles.

```python
from taller_green_code.modulo3_estructuras import procesar_csv_verde

stats = procesar_csv_verde('datos_8gb.csv', chunk_size=50000)
# {'count': 5000000, 'mean': 52.3, 'std_dev': 10.1, 'p95': 67.8, 'p99': 75.2}
```

---

## Modulo 4: Carbon awareness y time/demand shifting

**Contexto**: entrenamiento ML nocturno. Intensidad de carbono varia entre 45 y 380 gCO2/kWh. El scheduler decide cuando ejecutar.

### Ejercicio 4.1 — Scheduler carbon-aware

Clasifica ventanas en verde (<100), amarilla (100-250), roja (>250). Asigna jobs diferibles a ventanas verdes con greedy + backtracking.

```python
from taller_green_code.modulo4_carbon import CarbonScheduler, Job, VentanaCarbon

jobs = [Job(id='train_model', duracion_horas=2.0, deadline=23,
            puede_pausar=True, prioridad=3)]
ventanas = [VentanaCarbon(hora=h, intensidad=50 + h*15) for h in range(24)]

scheduler = CarbonScheduler()
asignaciones = scheduler.schedule(jobs, ventanas)
sci = scheduler.sci_estimado(asignaciones, jobs, ventanas)
evitado = scheduler.carbon_evitado_vs_naive(asignaciones, jobs, ventanas)
```

### Ejercicio 4.2 — Predictor de intensidad de carbono

Predice intensidad con promedio movil ponderado + patron diario (estacionalidad 24h) usando autocorrelacion manual.

```python
from taller_green_code.modulo4_carbon import CarbonPredictor

predictor = CarbonPredictor()
predictor.fit(datos_historicos)     # 30 dias de (timestamp, gCO2)
prediccion = predictor.predict(24)  # Proximas 24 horas
print(predictor.error_mae())        # Error absoluto medio
```

### Ejercicio 4.3 — Circuit breaker energetico

Patron Circuit Breaker aplicado a consumo energetico. Estados: VERDE -> AMARILLO -> ROJO -> VERDE (cooldown).

```python
from taller_green_code.modulo4_carbon import EnergyCircuitBreaker, Job

cb = EnergyCircuitBreaker()
job = Job(id='batch', duracion_horas=1.0, deadline=23,
          puede_pausar=True, prioridad=3)

puede, motivo = cb.check_and_act(intensidad=290, job=job)
print(cb.get_state())          # 'ROJO'
print(cb.carbon_saved_log())   # [{...}]
```

---

## Modulo 5: Medicion real del SCI con CodeCarbon

Instrumenta todos los algoritmos anteriores con medicion real de emisiones.

### Ejercicio 5.1 — SCI Harness

```python
from taller_green_code.modulo5_sci import SCI_Harness
from taller_green_code.modulo2_cache import fib_iterativo

harness = SCI_Harness()
resultado = harness.measure(fib_iterativo, (35,), functional_unit=1)
print(resultado.to_dict())
# {'funcion': 'fib_iterativo', 'emisiones_kg_co2': ..., 'sci': ..., ...}

harness.export_csv([resultado], 'reporte.csv')
```

### Ejercicio 5.2 — Benchmark integrado

Ejecuta todos los algoritmos instrumentados y genera el reporte SCI final.

```python
from taller_green_code.modulo5_sci import ejecutar_benchmark_completo

reporte = ejecutar_benchmark_completo()
print(f"SCI Total: {reporte['sci_total']}")
print(f"Resultados: {len(reporte['resultados'])} algoritmos medidos")
```

---

## Tests por modulo

| Modulo | Tests | Tema | Estado |
|--------|-------|------|--------|
| 1 | 13 | Algoritmos O(n) -> O(log n) | ✅ 13/13 PASS |
| 2 | 14 | Cache, memoizacion, generadores lazy | ✅ 14/14 PASS |
| 3 | 11 | Patricia Trie, Bloom Filter, Welford | ✅ 11/11 PASS |
| 4 | 10 | Carbon scheduler, predictor, circuit breaker | ✅ 10/10 PASS |
| 5 | 7 | SCI harness, benchmark integrado | ✅ 7/7 PASS |

**Total: 55 tests | ✅ 55/55 PASS en 1.27s**

---

## Resultados de Implementacion

### Modulo 1: Complejidad Algoritmica

**Implementaciones completadas:**
- ✅ `buscar_log_verde()` - Búsqueda binaria O(log n)
- ✅ `dedup_verde()` - Deduplicación O(n) con preservación de orden
- ✅ `top_k_verde()` - Top-K con heap mínimo manual O(n log k)

**Mejoras alcanzadas:**
- Busqueda: O(n) → O(log n) = ~99.9% reducción para n=10M
- Deduplicación: O(n²) → O(n) = 99% mejora de tiempo
- Top-K: O(n log n) → O(n log k) = 6.6x más eficiente (k=10, n=10M)

### Modulo 2: Cache y Memoizacion

**Implementaciones completadas:**
- ✅ `fib_memo()` - Memoización manual O(n)
- ✅ `fib_iterativo()` - Fibonacci iterativo O(n) con O(1) espacio
- ✅ `fib_matrix()` - Exponenciación de matrices O(log n)
- ✅ `LRUCache` - Cache LRU thread-safe con O(1) get/set
- ✅ `pipeline_verde()` - Generadores lazy
- ✅ `pipeline_paralelo()` - Pipeline paralelo con ThreadPoolExecutor

**Perfil energético:**
- fib_matrix(10000): <10ms, O(log n) tiempo
- LRUCache: Hit rate >79%, thread-safe con Lock
- Pipeline: Never >200 usuarios en memoria simultáneamente

### Modulo 3: Estructuras de Datos

**Implementaciones completadas:**
- ✅ `PatriciaTrie` - Trie comprimido para URLs
  - Memory: ≤30% del dict equivalente (verificado)
  - Búsqueda de prefijos O(m + k)
- ✅ `BloomFilter` - Filtro probabilístico
  - Para 1M elementos: <2MB RAM
  - fp_rate real ≤1.5% (objetivo 1%)
  - Double hashing: SHA256 + MD5
- ✅ `procesar_csv_verde()` - Streaming CSV
  - Welford: O(1) espacio para media/varianza
  - Reservoir sampling: O(1000) muestras para percentiles

### Modulo 4: Carbon Awareness

**Implementaciones completadas:**
- ✅ `CarbonScheduler` - Scheduler carbon-aware
  - Clasifica: Verde (<100), Amarilla (100-250), Roja (>250) gCO2/kWh
  - Greedy assignment a ventanas verdes
  - Carbon evitado: ≥0 gCO2 vs naive
- ✅ `CarbonPredictor` - Predictor de intensidad
  - Patrón diario 24h + promedio móvil
  - MAE calculado en holdout set
  - Caché: 30min TTL
- ✅ `EnergyCircuitBreaker` - Circuit breaker energético
  - Estados: VERDE → AMARILLO → ROJO → VERDE (cooldown 1800s)
  - En ROJO: rechaza prioridad 3, acepta 1-2 con degradación
  - Log de carbono ahorrado

### Modulo 5: Medicion SCI

**Implementaciones completadas:**
- ✅ `SCI_Harness` - Instrumentación de funciones
  - Medición de tiempo con perf_counter()
  - Estimación: 0.00003 kWh/s * 400 gCO2/kWh
  - SCI = emisiones_kg / unidad_funcional
- ✅ `ejecutar_benchmark_completo()` - Benchmark integrado
  - 8 benchmarks: M1 (busqueda, dedup, topk), M2 (fib, lru, pipeline), M3 (bloom, csv), M4 (scheduler)
  - SCI_total calculado como promedio de todos los módulos

---

## Ambiente y Dependencias

**Python:** 3.14.0
**Test Framework:** pytest 9.0.3
**Tests ejecutados:** `pytest tests/ -q`
**Tiempo total:** 1.27s
**Status:** ✅ Todos los tests pasan

**Requisitos:**
- Python >=3.10
- pytest >=7.4.0 (para tests)

---

## Como Ejecutar

```bash
# Instalar dependencias de test
pip install pytest

# Ejecutar todos los tests
pytest tests/ -v

# Ejecutar módulo específico
pytest tests/test_modulo1.py -v

# Benchmark integrado
python -c "from taller_green_code.modulo5_sci import ejecutar_benchmark_completo; print(ejecutar_benchmark_completo())"
```

---

## Referencias

- [Green Software Foundation - SCI Specification](https://github.com/Green-Software-Foundation/sci)
- [ISO/IEC 21031:2024](https://www.iso.org/standard/86663.html)
- [Principles of Green Software Engineering](https://principles.green/)
- [CodeCarbon](https://codecarbon.io/)
