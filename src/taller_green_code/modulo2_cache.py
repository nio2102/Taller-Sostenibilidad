# ==============================
# MODULO 2: Cache, memoizacion y computacion lazy
# ==============================
#
# INSTRUCCIONES:
# Implementa las versiones "verde" de cada funcion.
# Las versiones contaminantes estan como referencia.

import threading
from concurrent.futures import ThreadPoolExecutor, as_completed


# ============================================================
# VERSION CONTAMINANTE — O(2^n)
# ============================================================

def fib_contaminante(n: int) -> int:
    if n <= 1:
        return n
    return fib_contaminante(n - 1) + fib_contaminante(n - 2)

# ============================================================
# TAREA 1: fib_memo(n) — memoizacion manual con dict, sin lru_cache
# TAREA 2: fib_iterativo(n) — O(n) tiempo, O(1) espacio
# TAREA 3: fib_matrix(n) — O(log n) con exponenciacion de matrices 2x2
# ============================================================


def fib_memo(n: int) -> int:
    """Fibonacci con memoización manual O(n) tiempo, O(n) espacio"""
    memo = {}
    
    def fib_aux(n):
        if n in memo:
            return memo[n]
        if n <= 1:
            return n
        result = fib_aux(n - 1) + fib_aux(n - 2)
        memo[n] = result
        return result
    
    return fib_aux(n)


def fib_iterativo(n: int) -> int:
    """Fibonacci iterativo O(n) tiempo, O(1) espacio"""
    if n <= 1:
        return n
    a, b = 0, 1
    for _ in range(2, n + 1):
        a, b = b, a + b
    return b


def fib_matrix(n: int) -> int:
    """Fibonacci con exponenciación de matrices O(log n)"""
    def matrix_mult(A, B):
        return [
            [A[0][0] * B[0][0] + A[0][1] * B[1][0], A[0][0] * B[0][1] + A[0][1] * B[1][1]],
            [A[1][0] * B[0][0] + A[1][1] * B[1][0], A[1][0] * B[0][1] + A[1][1] * B[1][1]]
        ]
    
    def matrix_pow(M, exp):
        if exp == 1:
            return M
        if exp % 2 == 0:
            half = matrix_pow(M, exp // 2)
            return matrix_mult(half, half)
        else:
            return matrix_mult(M, matrix_pow(M, exp - 1))
    
    if n <= 1:
        return n
    
    M = [[1, 1], [1, 0]]
    result = matrix_pow(M, n)
    return result[0][1]


# ============================================================
# VERSION CONTAMINANTE — recalcula cada score sin cache
# ============================================================

def calcular_sin_cache(user_id: str) -> float:
    import random
    return random.random() * 100

# ============================================================
# TAREA: LRUCache desde cero
# ============================================================
# Requisitos:
# - get(key) -> valor o None, O(1)
# - set(key, value) -> None, O(1)
# - evict al insertar cuando capacity alcanzada
# - thread-safe (usa threading.Lock)
# - metodo stats() -> {'hits': int, 'misses': int, 'hit_rate': float}
#
# PISTA: usa un dict + lista doblemente enlazada


class LRUCache:
    class Node:
        def __init__(self, key, value):
            self.key = key
            self.value = value
            self.prev = None
            self.next = None
    
    def __init__(self, capacity: int):
        self.capacity = capacity
        self.cache = {}  # key -> Node
        self.head = self.Node(None, None)  # sentinel
        self.tail = self.Node(None, None)  # sentinel
        self.head.next = self.tail
        self.tail.prev = self.head
        self.lock = threading.Lock()
        self.hits = 0
        self.misses = 0
    
    def _remove_node(self, node):
        """Remueve nodo de la lista doblemente enlazada"""
        prev_node = node.prev
        next_node = node.next
        prev_node.next = next_node
        next_node.prev = prev_node
    
    def _add_to_head(self, node):
        """Añade nodo inmediatamente después del head (más reciente)"""
        node.prev = self.head
        node.next = self.head.next
        self.head.next.prev = node
        self.head.next = node
    
    def get(self, key):
        with self.lock:
            if key not in self.cache:
                self.misses += 1
                return None
            node = self.cache[key]
            self._remove_node(node)
            self._add_to_head(node)
            self.hits += 1
            return node.value
    
    def set(self, key, value):
        with self.lock:
            if key in self.cache:
                # Actualizar valor y mover a head
                node = self.cache[key]
                node.value = value
                self._remove_node(node)
                self._add_to_head(node)
            else:
                # Crear nuevo nodo
                if self.capacity <= 0:
                    return
                node = self.Node(key, value)
                self.cache[key] = node
                self._add_to_head(node)
                
                # Si excedimos capacidad, eliminar el más antiguo (antes del tail)
                if len(self.cache) > self.capacity:
                    lru_node = self.tail.prev
                    self._remove_node(lru_node)
                    del self.cache[lru_node.key]
    
    def stats(self) -> dict:
        with self.lock:
            total = self.hits + self.misses
            hit_rate = self.hits / total if total > 0 else 0.0
            return {
                'hits': self.hits,
                'misses': self.misses,
                'hit_rate': hit_rate
            }


# ============================================================
# VERSION CONTAMINANTE — carga todos los usuarios en RAM
# ============================================================

import random as _random


def _cargar_usuario(uid):
    return {'id': uid, 'activo': _random.random() > 0.05, 'score_base': _random.random()}


def _calcular_score(u):
    return u['score_base'] * (1 + _random.random())


def pipeline_contaminante(user_ids: list) -> list:
    usuarios = [_cargar_usuario(uid) for uid in user_ids]
    activos = [u for u in usuarios if u['activo']]
    scores = [_calcular_score(u) for u in activos]
    top = sorted(scores, reverse=True)[:100]
    return top

# ============================================================
# TAREA: pipeline_verde(user_ids) usando generadores
# Nunca debe tener mas de ~200 usuarios en memoria simultaneamente
# Retorna el top-100 de scores (lista de floats)


def pipeline_verde(user_ids):
    """Pipeline con generadores lazy - O(n) tiempo, O(1) espacio"""
    def generar_usuarios():
        for uid in user_ids:
            usuario = _cargar_usuario(uid)
            if usuario['activo']:
                yield usuario
    
    def generar_scores():
        for usuario in generar_usuarios():
            score = _calcular_score(usuario)
            yield score
    
    # Consumir todo el generador y retornar top-100
    scores = list(generar_scores())
    return sorted(scores, reverse=True)[:100]


# ============================================================
# TAREA BONUS: pipeline_paralelo(user_ids, workers=4)
# ============================================================
# Usa concurrent.futures para procesar en paralelo
# Retorna el top-100 de scores


def pipeline_paralelo(user_ids, workers=4):
    """Pipeline paralelo usando ThreadPoolExecutor"""
    scores = []
    
    with ThreadPoolExecutor(max_workers=workers) as executor:
        # Submit todas las tareas de carga de usuario
        futures_carga = {executor.submit(_cargar_usuario, uid): uid 
                        for uid in user_ids}
        
        # Procesar resultados de carga
        usuarios_activos = []
        for future in as_completed(futures_carga):
            usuario = future.result()
            if usuario['activo']:
                usuarios_activos.append(usuario)
        
        # Calcular scores en paralelo
        futures_scores = {executor.submit(_calcular_score, u): u 
                         for u in usuarios_activos}
        
        for future in as_completed(futures_scores):
            score = future.result()
            scores.append(score)
    
    return sorted(scores, reverse=True)[:100]
