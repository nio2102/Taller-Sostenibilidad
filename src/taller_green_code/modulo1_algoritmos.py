# ==============================
# MODULO 1: Complejidad algoritmica y consumo energetico
# ==============================
#
# INSTRUCCIONES:
# Cada funcion tiene una version "contaminante" que NO debes modificar.
# Implementa la version "verde" debajo de cada una.
# Los tests verificaran que tu implementacion:
#   - Produce el mismo resultado que la version contaminante
#   - Usa menos tiempo de CPU (menor complejidad algoritmica)
#
# PISTA: Antes de escribir codigo, identifica la complejidad de la version
# contaminante y piensa en una estructura de datos/algoritmo que la reduzca.

# ============================================================
# VERSION CONTAMINANTE (referencia, NO modificar)
# ============================================================

# VERSION CONTAMINANTE — O(n) por busqueda
def buscar_log_lineal(logs: list[dict], timestamp: int) -> dict | None:
    for entry in logs:
        if entry['ts'] == timestamp:
            return entry
    return None

# ============================================================
# TU TAREA: implementar buscar_log_verde(logs, timestamp)
# ============================================================
# Requisitos:
#  - O(log n) tiempo
#  - Sin imports de bisect (implementa tu la busqueda binaria)
#  - Maneja lista vacia y timestamp inexistente
#  - Asume que logs esta ordenado por 'ts' ascendentemente
#
# Ejemplo:
#   logs = [{'id':'1','ts':100},{'id':'2','ts':200}]
#   buscar_log_verde(logs, 100) -> {'id':'1','ts':100}


def buscar_log_verde(logs: list[dict], timestamp: int) -> dict | None:
    """Búsqueda binaria O(log n) en logs ordenados por 'ts'"""
    left, right = 0, len(logs) - 1
    while left <= right:
        mid = (left + right) // 2
        mid_ts = logs[mid]['ts']
        if mid_ts == timestamp:
            return logs[mid]
        elif mid_ts < timestamp:
            left = mid + 1
        else:
            right = mid - 1
    return None


# ============================================================
# VERSION CONTAMINANTE — O(n^2)
# ============================================================

def dedup_contaminante(logs: list[dict]) -> list[dict]:
    resultado = []
    for log in logs:
        if log not in resultado:
            resultado.append(log)
    return resultado

# ============================================================
# TU TAREA: dedup_verde(logs) en O(n) tiempo y O(n) espacio
# ============================================================
# El campo unico es log['id'] (str)
# Debes preservar el orden de primera aparicion


def dedup_verde(logs: list[dict]) -> list[dict]:
    """Deduplicación O(n) usando set para tracking, preserva orden"""
    seen = set()
    resultado = []
    for log in logs:
        log_id = log['id']
        if log_id not in seen:
            seen.add(log_id)
            resultado.append(log)
    return resultado


# ============================================================
# VERSION CONTAMINANTE — O(n log n)
# ============================================================

def top_k_contaminante(logs: list[dict], k: int) -> list[dict]:
    return sorted(logs, key=lambda x: x['severity'], reverse=True)[:k]

# ============================================================
# TU TAREA: top_k_verde(logs, k) en O(n log k)
# ============================================================
# Usa un heap manual de tamano maximo k (sin heapq, implementalo tu)
# Los elementos deben ordenarse por 'severity' descendente
# Si k >= len(logs), retorna todos ordenados
# Si k <= 0, retorna lista vacia


def top_k_verde(logs: list[dict], k: int) -> list[dict]:
    """Top-K usando min-heap manual O(n log k) con orden estable"""
    if k <= 0:
        return []
    if k >= len(logs):
        return sorted(logs, key=lambda x: x['severity'], reverse=True)
    
    # Construir heap mínimo de tamaño k usando (severity, index, element)
    # para garantizar orden estable
    heap = []
    for idx, log in enumerate(logs):
        severity = log['severity']
        item = (severity, idx, log)
        
        if len(heap) < k:
            heap.append(item)
            # Sift up
            i = len(heap) - 1
            while i > 0:
                parent = (i - 1) // 2
                if heap[i][0] < heap[parent][0]:  # Comparar severity
                    heap[i], heap[parent] = heap[parent], heap[i]
                    i = parent
                else:
                    break
        elif severity > heap[0][0]:
            heap[0] = item
            # Sift down
            i = 0
            while True:
                left = 2 * i + 1
                right = 2 * i + 2
                smallest = i
                if left < len(heap) and heap[left][0] < heap[smallest][0]:
                    smallest = left
                if right < len(heap) and heap[right][0] < heap[smallest][0]:
                    smallest = right
                if smallest != i:
                    heap[i], heap[smallest] = heap[smallest], heap[i]
                    i = smallest
                else:
                    break
    
    # Retornar ordenados descendentemente por severity, luego por index (orden original)
    # Extraer solo los elementos
    resultado = [item[2] for item in sorted(heap, key=lambda x: (-x[0], x[1]))]
    return resultado
