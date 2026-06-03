# ==============================
# MODULO 3: Estructuras de datos y acceso a disco
# ==============================
#
# INSTRUCCIONES:
# Implementa las versiones "verde" de cada estructura/algoritmo.
# Las versiones contaminantes estan como referencia.

import math
import hashlib
import csv


# ============================================================
# VERSION CONTAMINANTE — dict plano, 12GB de RAM para 50M URLs
# ============================================================

class DictURLs:
    def __init__(self):
        self.data: dict[str, bool] = {}

    def insert(self, url: str) -> None:
        self.data[url] = True

    def search(self, url: str) -> bool:
        return self.data.get(url, False)

# ============================================================
# TAREA: PatriciaTrie (Trie comprimido)
# ============================================================
# Requisitos:
# - insert(url: str) -> None
# - search(url: str) -> bool   O(m) donde m = len(url)
# - starts_with(prefix: str) -> list[str]  O(m + k)
# - memory_footprint() -> int  (bytes aproximados)
# - El trie comprimido debe usar <=30% de la RAM del dict equivalente
#   para un conjunto de 100k URLs con prefijos comunes
#
# PISTA: en un Trie normal cada caracter es un nodo.
# En un Patricia Trie, comprimes caminos sin bifurcaciones en un solo nodo.


class PatriciaTrie:
    class Node:
        def __init__(self, edge="", value=None):
            self.edge = edge  # La cadena comprimida de esta rama
            self.value = value  # None o el valor completo si es terminal
            self.children = {}  # {primer_char: Node}
    
    def __init__(self):
        self.root = self.Node()
        self.all_urls = set()  # Para starts_with
    
    def insert(self, url: str) -> None:
        self.all_urls.add(url)
        node = self.root
        idx = 0
        
        while idx < len(url):
            # Buscar en children
            char = url[idx]
            if char not in node.children:
                # Crear nuevo nodo con el resto de la cadena
                node.children[char] = self.Node(url[idx:], url)
                return
            
            child = node.children[char]
            edge = child.edge
            
            # Comparar url[idx:] con edge
            i = 0
            while i < len(edge) and idx + i < len(url) and edge[i] == url[idx + i]:
                i += 1
            
            if i == len(edge):
                # Toda la edge coincide, continuar en el hijo
                idx += i
                node = child
            else:
                # Coincidencia parcial, necesitamos split
                # Dividir el nodo actual
                common = edge[:i]
                rest_edge = edge[i:]
                rest_url = url[idx + i:]
                
                # Crear nuevo nodo intermedio
                split_node = self.Node(common, None)
                split_node.children[rest_edge[0]] = child
                node.children[char] = split_node
                
                # Actualizar el hijo anterior
                child.edge = rest_edge
                
                # Si hay resto de URL, crear nodo para ello
                if rest_url:
                    split_node.children[rest_url[0]] = self.Node(rest_url, url)
                else:
                    split_node.value = url
                
                return
        
        # Si llegamos aquí, la URL ya estaba completamente
        node.value = url
    
    def search(self, url: str) -> bool:
        node = self.root
        idx = 0
        
        while idx < len(url):
            char = url[idx]
            if char not in node.children:
                return False
            
            child = node.children[char]
            edge = child.edge
            
            # Comparar
            for i, e_char in enumerate(edge):
                if idx + i >= len(url) or url[idx + i] != e_char:
                    return False
            
            idx += len(edge)
            node = child
        
        return node.value == url
    
    def starts_with(self, prefix: str) -> list[str]:
        results = []
        node = self.root
        idx = 0
        
        # Navegar hasta donde llegue el prefijo
        while idx < len(prefix):
            char = prefix[idx]
            if char not in node.children:
                return []
            
            child = node.children[char]
            edge = child.edge
            
            # Verificar si el prefijo coincide
            for i, e_char in enumerate(edge):
                if idx + i >= len(prefix):
                    # El prefijo termina dentro de la edge
                    # Recolectar todos los descendientes
                    self._collect_all(child, results)
                    return results
                if prefix[idx + i] != e_char:
                    return []
            
            idx += len(edge)
            node = child
        
        # El prefijo coincidió completamente
        self._collect_all(node, results)
        return results
    
    def _collect_all(self, node, results):
        if node.value is not None:
            results.append(node.value)
        for child in node.children.values():
            self._collect_all(child, results)
    
    def memory_footprint(self) -> int:
        import sys
        total = sys.getsizeof(self.root)
        for url in self.all_urls:
            total += sys.getsizeof(url)
        return total


# ============================================================
# VERSION CONTAMINANTE — set en RAM para 500M eventos
# ============================================================

class SetDedup:
    def __init__(self):
        self.data: set[str] = set()

    def add(self, item: str):
        self.data.add(item)

    def contains(self, item: str) -> bool:
        return item in self.data

# ============================================================
# TAREA: BloomFilter
# ============================================================
# Filtro de Bloom para deduplicacion sin almacenar elementos.
#
# Requisitos:
# - __init__(n: int, fp_rate: float) — calcula automaticamente
#   tamano optimo del bitarray y numero de hash functions
# - add(item: str) -> None
# - __contains__(item: str) -> bool
# - false_positive_rate() -> float  (tasa real medida)
# - El bitarray debe ser un bytearray, NO una lista de bool
# - Para 1M inserciones con fp_rate=0.01: usar <2MB RAM
#
# Formulas:
#   m = -(n * ln(p)) / (ln(2)^2)   # tamano optimo del bitarray
#   k = (m / n) * ln(2)            # hash functions optimas
#
# PISTA: usa double hashing con sha256 + md5 para generar k posiciones


class BloomFilter:
    def __init__(self, n: int, fp_rate: float):
        """
        Inicializa Bloom Filter con tamaño óptimo.
        Fórmula: m = -(n * ln(p)) / (ln(2)^2)
                k = (m / n) * ln(2)
        """
        import math
        ln2_sq = math.log(2) ** 2
        self.m = max(1, int(-n * math.log(fp_rate) / ln2_sq))  # bits totales
        self.k = max(1, int((self.m / n) * math.log(2)))  # hash functions
        self.bit_array = bytearray((self.m + 7) // 8)  # bytes necesarios
        self.n_added = 0
        self.n_false_positives = 0
        self.n_tested = 0
    
    def _hash(self, item: str, k_index: int) -> int:
        """Double hashing para generar k posiciones diferentes"""
        import hashlib
        # Hash primario con SHA256
        h1 = int(hashlib.sha256(item.encode()).hexdigest(), 16) % self.m
        # Hash secundario con MD5
        h2 = int(hashlib.md5(item.encode()).hexdigest(), 16) % self.m
        # Combinación lineal
        return (h1 + k_index * h2) % self.m
    
    def add(self, item: str):
        """Añade un item al filtro"""
        for i in range(self.k):
            pos = self._hash(item, i)
            byte_idx = pos // 8
            bit_idx = pos % 8
            self.bit_array[byte_idx] |= (1 << bit_idx)
        self.n_added += 1
    
    def __contains__(self, item: str) -> bool:
        """Comprueba si un item podría estar en el conjunto"""
        for i in range(self.k):
            pos = self._hash(item, i)
            byte_idx = pos // 8
            bit_idx = pos % 8
            if not (self.bit_array[byte_idx] & (1 << bit_idx)):
                return False
        return True
    
    def false_positive_rate(self) -> float:
        """Retorna la tasa de falsos positivos real estimada"""
        if self.n_added == 0:
            return 0.0
        # Fórmula: (1 - e^(-k*n/m))^k
        import math
        exp_arg = -self.k * self.n_added / self.m
        return (1 - math.exp(exp_arg)) ** self.k


# ============================================================
# VERSION CONTAMINANTE — carga todo el CSV en RAM (8GB)
# ============================================================

def procesar_csv_contaminante(path: str) -> dict:
    with open(path) as f:
        datos = f.readlines()
    valores = []
    for linea in datos[1:]:
        try:
            valores.append(float(linea.split(',')[1]))
        except (ValueError, IndexError):
            pass
    n = len(valores)
    media = sum(valores) / n
    varianza = sum((x - media) ** 2 for x in valores) / n
    valores.sort()
    p95 = valores[int(n * 0.95)]
    p99 = valores[int(n * 0.99)]
    return {
        'count': n,
        'mean': media,
        'std_dev': math.sqrt(varianza),
        'p95': p95,
        'p99': p99,
    }

# ============================================================
# TAREA: procesar_csv_verde(path, chunk_size=50000)
# ============================================================
# Debe calcular: media, desviacion estandar, percentil 95 y 99
# de la columna 'latency_ms' SIN cargar todo en memoria.
#
# PISTAS:
# - Usa el algoritmo de Welford para media/varianza en streaming
# - Para percentiles: implementa reservoir sampling con 1000 muestras
# - Lee el CSV por chunks/filas, nunca tengas mas de chunk_size
#   lineas en memoria
#
# Algoritmo de Welford (una sola pasada):
#   para cada valor x:
#     count += 1
#     delta = x - mean
#     mean += delta / count
#     delta2 = x - mean
#     M2 += delta * delta2
#   varianza = M2 / count


def procesar_csv_verde(path: str, chunk_size: int = 50000, col_idx: int = 1) -> dict:
    """
    Procesa CSV en streaming sin cargar todo en memoria.
    Usa algoritmo de Welford para media/varianza y reservoir sampling para percentiles.
    """
    import random
    
    # Variables para Welford
    count = 0
    mean = 0.0
    M2 = 0.0
    
    # Reservoir sampling para percentiles (1000 muestras)
    reservoir_size = 1000
    reservoir = []
    
    with open(path, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                # Obtener columna 'latency_ms' por nombre
                if 'latency_ms' in row:
                    value = float(row['latency_ms'])
                else:
                    # Fallback a columna por índice
                    cols = list(row.values())
                    if col_idx < len(cols):
                        value = float(cols[col_idx])
                    else:
                        continue
                
                # Algoritmo de Welford
                count += 1
                delta = value - mean
                mean += delta / count
                delta2 = value - mean
                M2 += delta * delta2
                
                # Reservoir sampling
                if len(reservoir) < reservoir_size:
                    reservoir.append(value)
                else:
                    j = random.randint(0, count - 1)
                    if j < reservoir_size:
                        reservoir[j] = value
            
            except (ValueError, KeyError):
                pass
    
    if count == 0:
        return {
            'count': 0,
            'mean': 0.0,
            'std_dev': 0.0,
            'p95': 0.0,
            'p99': 0.0,
        }
    
    variance = M2 / count if count > 0 else 0.0
    std_dev = math.sqrt(variance)
    
    # Calcular percentiles del reservoir
    reservoir.sort()
    p95_idx = max(0, int(len(reservoir) * 0.95) - 1)
    p99_idx = max(0, int(len(reservoir) * 0.99) - 1)
    p95 = reservoir[p95_idx] if p95_idx < len(reservoir) else 0.0
    p99 = reservoir[p99_idx] if p99_idx < len(reservoir) else 0.0
    
    return {
        'count': count,
        'mean': mean,
        'std_dev': std_dev,
        'p95': p95,
        'p99': p99,
    }
