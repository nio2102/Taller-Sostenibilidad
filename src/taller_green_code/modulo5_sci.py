# ==============================
# MODULO 5: Medicion real del SCI
# ==============================
#
# INSTRUCCIONES:
# Implementa el harness de medicion y el benchmark integrado.
# Este modulo orquesta todos los anteriores.

import time
import json
import csv
from typing import Callable


# ============================================================
# CLASE DE APOYO: SCI_Result
# ============================================================

class SCI_Result:
    def __init__(self, funcion: str, emisiones: float, duracion: float,
                 unidad_funcional: int, energia: float, reduccion: float = None):
        self.funcion = funcion
        self.emisiones_kg_co2 = emisiones
        self.duracion_segundos = duracion
        self.unidad_funcional = unidad_funcional
        self.sci = emisiones / unidad_funcional if unidad_funcional > 0 else 0.0
        self.energia_kwh = energia
        self.reduccion_vs_baseline = reduccion

    def to_dict(self) -> dict:
        return {
            'funcion': self.funcion,
            'emisiones_kg_co2': self.emisiones_kg_co2,
            'duracion_segundos': self.duracion_segundos,
            'unidad_funcional': self.unidad_funcional,
            'sci': self.sci,
            'energia_kwh': self.energia_kwh,
            'reduccion_vs_baseline': self.reduccion_vs_baseline,
        }


class CompareResult:
    def __init__(self, verde: SCI_Result, contaminante: SCI_Result):
        self.verde = verde
        self.contaminante = contaminante
        self.reduccion_pct = (
            ((contaminante.sci - verde.sci) / contaminante.sci * 100)
            if contaminante.sci > 0
            else 0.0
        )


# ============================================================
# TAREA: SCI_Harness
# ============================================================
# Instrumenta cualquier funcion y calcula su contribucion al SCI.
#
# Requisitos:
# - measure(fn: Callable, args: tuple, functional_unit: int) -> SCI_Result
#   Mide tiempo de ejecucion y estima emisiones basado en CPU time.
#   Formula: emisiones_kg = duracion_segundos * 0.00003 * 400.0
#
# - compare(fn_verde, fn_contaminante, args, fu) -> CompareResult
#   retorna la comparacion con reduccion porcentual de SCI
#
# - export_csv(resultados: list, path: str) -> None
#   exporta los resultados a un archivo CSV con headers correctos
#
# PISTA: usa time.perf_counter() para medir con precision.
# La constante 0.00003 representa kWh por segundo de CPU (~108W).
# La constante 400.0 es la intensidad de carbono promedio (gCO2/kWh).


class SCI_Harness:
    def measure(self, fn: Callable, args: tuple, functional_unit: int,
                name: str = None) -> SCI_Result:
        """Mide tiempo y estima emisiones de una función"""
        nombre = name or fn.__name__
        
        # Medir tiempo de ejecución
        start = time.perf_counter()
        resultado = fn(*args)
        elapsed = time.perf_counter() - start
        
        # Estimar emisiones basado en CPU time
        # Constante: 0.00003 kWh por segundo (~108W) * 400 gCO2/kWh
        energia_kwh = elapsed * 0.00003
        emisiones_kg = energia_kwh * 400.0 / 1000  # convertir a kg
        
        return SCI_Result(nombre, emisiones_kg, elapsed, functional_unit, energia_kwh)
    
    def compare(self, fn_verde: Callable, fn_contaminante: Callable,
                args: tuple, fu: int) -> CompareResult:
        """Compara dos funciones y calcula reducción de SCI"""
        result_verde = self.measure(fn_verde, args, fu, "verde")
        result_contaminante = self.measure(fn_contaminante, args, fu, "contaminante")
        
        return CompareResult(result_verde, result_contaminante)
    
    def export_csv(self, resultados: list, path: str) -> None:
        """Exporta resultados a CSV"""
        if not resultados:
            return
        
        fieldnames = ['funcion', 'emisiones_kg_co2', 'duracion_segundos', 
                      'unidad_funcional', 'sci', 'energia_kwh', 'reduccion_vs_baseline']
        
        with open(path, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            for resultado in resultados:
                writer.writerow(resultado.to_dict())


# ============================================================
# TAREA: ejecutar_benchmark_completo()
# ============================================================
# Ejecuta todos los algoritmos de modulos 1-4 instrumentados
# y genera el SCI final del taller.
#
# Retorna un dict con:
# {
#   'sci_total': float,         # SCI promedio de todas las implementaciones verdes
#   'resultados': list[dict],    # Lista de resultados individuales
# }
#
# Debes importar y ejecutar:
# - buscar_log_verde (con datos de prueba)
# - dedup_verde
# - top_k_verde
# - fib_iterativo
# - LRUCache (test de hits/misses)
# - BloomFilter (test de insercion/consulta)
# - procesar_csv_verde (crea un CSV temporal de prueba)
# - CarbonScheduler.schedule
#
# PISTA: crea datos sinteticos pequenos para cada benchmark
# (ej. 10000 logs en vez de 10M). El SCI_Harness se encarga
# de estimar las emisiones proporcionalmente.


def ejecutar_benchmark_completo() -> dict:
    """Ejecuta benchmark de todos los módulos y retorna SCI total"""
    from taller_green_code.modulo1_algoritmos import buscar_log_verde, dedup_verde, top_k_verde
    from taller_green_code.modulo2_cache import fib_iterativo, LRUCache, pipeline_verde
    from taller_green_code.modulo3_estructuras import BloomFilter, procesar_csv_verde
    from taller_green_code.modulo4_carbon import CarbonScheduler, Job, VentanaCarbon
    import tempfile
    import random as _random
    
    harness = SCI_Harness()
    resultados = []
    
    # M1: Búsqueda binaria
    logs = sorted([{'id': str(i), 'ts': i * 10, 'severity': i % 100} 
                   for i in range(1000)], key=lambda x: x['ts'])
    result = harness.measure(lambda: buscar_log_verde(logs, 5000), (), 1000, "M1_busqueda")
    resultados.append(result)
    
    # M1: Deduplicación
    logs_dup = [{'id': str(i % 500), 'ts': i, 'severity': i % 100} for i in range(1000)]
    result = harness.measure(lambda: dedup_verde(logs_dup), (), 500, "M1_dedup")
    resultados.append(result)
    
    # M1: Top-K
    logs_topk = [{'id': str(i), 'ts': i, 'severity': i % 1000} for i in range(1000)]
    result = harness.measure(lambda: top_k_verde(logs_topk, 10), (), 1000, "M1_topk")
    resultados.append(result)
    
    # M2: Fibonacci
    result = harness.measure(lambda: fib_iterativo(35), (), 1, "M2_fib_iterativo")
    resultados.append(result)
    
    # M2: LRU Cache
    def test_lru():
        cache = LRUCache(100)
        for i in range(500):
            cache.set(f"key_{i % 100}", i)
            cache.get(f"key_{i % 100}")
        return cache.stats()
    
    result = harness.measure(test_lru, (), 500, "M2_lru_cache")
    resultados.append(result)
    
    # M2: Pipeline
    user_ids = list(range(100))
    result = harness.measure(lambda: pipeline_verde(user_ids), (), 100, "M2_pipeline")
    resultados.append(result)
    
    # M3: Bloom Filter
    def test_bloom():
        bf = BloomFilter(10000, 0.01)
        for i in range(10000):
            bf.add(f"event_{i}")
        count = 0
        for i in range(10000):
            if f"event_{i}" in bf:
                count += 1
        return count
    
    result = harness.measure(test_bloom, (), 10000, "M3_bloom_filter")
    resultados.append(result)
    
    # M3: CSV processing
    with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False, newline='') as f:
        import csv as csv_module
        writer = csv_module.writer(f)
        writer.writerow(['id', 'latency_ms', 'status'])
        for i in range(1000):
            writer.writerow([i, _random.gauss(50, 10), 200])
        csv_path = f.name
    
    result = harness.measure(lambda: procesar_csv_verde(csv_path), (), 1000, "M3_csv_processing")
    resultados.append(result)
    
    # M4: Carbon Scheduler
    def test_scheduler():
        jobs = [Job(id=f"j{i}", duracion_horas=_random.uniform(0.5, 2.0),
                   deadline=_random.randint(6, 23), puede_pausar=bool(_random.randint(0, 1)),
                   prioridad=_random.randint(1, 3))
               for i in range(20)]
        ventanas = [VentanaCarbon(hora=h, intensidad=max(10, 50 + (h - 4) * 30 if h < 12 else 300 - (h - 12) * 20))
                   for h in range(24)]
        scheduler = CarbonScheduler()
        return scheduler.schedule(jobs, ventanas)
    
    result = harness.measure(test_scheduler, (), 20, "M4_carbon_scheduler")
    resultados.append(result)
    
    # Calcular SCI total
    sci_total = sum(r.sci for r in resultados) / len(resultados) if resultados else 0.0
    
    # Limpiar archivo temporal
    import os
    os.unlink(csv_path)
    
    return {
        'sci_total': sci_total,
        'resultados': [r.to_dict() for r in resultados],
    }


# ============================================================
# CONFIGURACION DE REFERENCIA (no modificar)
# ============================================================

BENCHMARK_CONFIG = {
    "m1_busqueda":      {"n": 1_000_000, "fu": 10_000},
    "m1_dedup":         {"n": 500_000,   "fu": 500_000},
    "m1_topk":          {"n": 1_000_000, "fu": 1_000_000, "k": 10},
    "m2_pipeline":      {"n": 1_000_000, "fu": 1_000_000},
    "m2_lru":           {"ops": 100_000, "fu": 100_000},
    "m3_bloom":         {"n": 1_000_000, "fu": 1_000_000},
    "m3_csv":           {"filas": 5_000_000, "fu": 5_000_000},
    "m4_scheduler":     {"jobs": 100,    "fu": 100},
}
