import time
import random
import threading
from taller_green_code.modulo2_cache import (
    fib_memo, fib_iterativo, fib_matrix, LRUCache, pipeline_verde, pipeline_paralelo
)


class TestFibonacci:
    def test_fib_correctitud_todos_metodos(self):
        expected = [0, 1, 1, 2, 3, 5, 8, 13, 21, 34, 55, 89, 144, 233, 377]
        for n, exp in enumerate(expected):
            assert fib_memo(n) == exp
            assert fib_iterativo(n) == exp
            assert fib_matrix(n) == exp

    def test_fib_casos_borde(self):
        for fn in [fib_memo, fib_iterativo, fib_matrix]:
            assert fn(0) == 0
            assert fn(1) == 1

    def test_fib_iterativo_grandes(self):
        assert fib_iterativo(50) == 12586269025
        assert fib_iterativo(100) == 354224848179261915075

    def test_fib_matrix_logaritmico(self):
        start = time.perf_counter()
        result = fib_matrix(10000)
        elapsed = time.perf_counter() - start
        assert elapsed < 0.01
        assert isinstance(result, int)
        assert result > 0

    def test_fib_iterativo_rendimiento(self):
        start = time.perf_counter()
        result = fib_iterativo(10000)
        elapsed = time.perf_counter() - start
        assert elapsed < 0.5
        assert result > 0

    def test_fib_todos_consistentes(self):
        for n in range(40):
            a = fib_memo(n)
            b = fib_iterativo(n)
            c = fib_matrix(n)
            assert a == b == c


class TestLRUCache:
    def test_lru_hit_miss(self):
        cache = LRUCache(100)
        for i in range(100):
            cache.set(f"key_{i}", i)
        for i in range(50):
            assert cache.get(f"key_{i}") == i
        for i in range(200):
            cache.get(f"new_{i}")
        stats = cache.stats()
        assert stats['hit_rate'] >= 0.0

    def test_lru_eviction_correcta(self):
        cache = LRUCache(2)
        cache.set('a', 1)
        cache.set('b', 2)
        cache.get('a')
        cache.set('c', 3)
        assert cache.get('a') == 1
        assert cache.get('b') is None
        assert cache.get('c') == 3

    def test_lru_thread_safe(self):
        cache = LRUCache(1000)
        errors = []

        def reader():
            try:
                for _ in range(50):
                    cache.get(f"key_{random.randint(0, 800)}")
            except Exception as e:
                errors.append(e)

        def writer():
            try:
                for i in range(100):
                    cache.set(f"key_{i}", i)
            except Exception as e:
                errors.append(e)

        threads = []
        for _ in range(50):
            threads.append(threading.Thread(target=reader))
            threads.append(threading.Thread(target=writer))
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        assert len(errors) == 0

    def test_lru_stats(self):
        cache = LRUCache(10)
        cache.set('a', 1)
        cache.get('a')
        cache.get('b')
        stats = cache.stats()
        assert stats['hits'] == 1
        assert stats['misses'] == 1
        assert stats['hit_rate'] == 0.5

    def test_lru_update_existing(self):
        cache = LRUCache(3)
        cache.set('a', 1)
        cache.set('a', 2)
        assert cache.get('a') == 2

    def test_lru_capacity_cero(self):
        cache = LRUCache(0)
        cache.set('a', 1)
        assert cache.get('a') is None


class TestPipeline:
    def test_pipeline_lazy_resultado(self, user_ids):
        result = pipeline_verde(user_ids)
        assert isinstance(result, list)
        assert len(result) <= 100

    def test_pipeline_paralelo_resultado(self, user_ids):
        result = pipeline_paralelo(user_ids, workers=2)
        assert isinstance(result, list)
        assert len(result) <= 100
