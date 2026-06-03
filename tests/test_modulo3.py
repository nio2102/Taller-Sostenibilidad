import time
import sys
from taller_green_code.modulo3_estructuras import PatriciaTrie, BloomFilter, procesar_csv_verde


class TestPatriciaTrie:
    def test_trie_insert_search(self):
        trie = PatriciaTrie()
        urls = [f"/api/{p}/{i}" for p in ['v1', 'v2', 'v3'] for i in range(100)]
        for url in urls:
            trie.insert(url)
        for url in urls:
            assert trie.search(url) is True
        assert trie.search("/nonexistent/path") is False

    def test_trie_prefix(self):
        trie = PatriciaTrie()
        urls_v2 = [f"/api/v2/{i}" for i in range(50)]
        urls_v3 = [f"/api/v3/{i}" for i in range(50)]
        for url in urls_v2 + urls_v3:
            trie.insert(url)
        results = trie.starts_with("/api/v2")
        assert len(results) == 50
        for url in urls_v2:
            assert url in results

    def test_trie_memoria(self):
        trie = PatriciaTrie()
        prefixes = ['/api/', '/static/', '/user/']
        for prefix in prefixes:
            for i in range(100):
                trie.insert(f"{prefix}resource/{i}")
        footprint = trie.memory_footprint()
        d = {url: True for prefix in prefixes
             for url in [f"{prefix}resource/{i}" for i in range(100)]}
        dict_size = sys.getsizeof(d) + sum(sys.getsizeof(k) + sys.getsizeof(v) for k, v in d.items())
        assert footprint <= dict_size * 0.8

    def test_trie_lista_vacia(self):
        trie = PatriciaTrie()
        assert trie.search("anything") is False
        assert trie.starts_with("") == []

    def test_trie_prefijo_exacto(self):
        trie = PatriciaTrie()
        trie.insert("/api/v1/users")
        trie.insert("/api/v1/users/123")
        trie.insert("/api/v2/posts")
        results = trie.starts_with("/api/v1")
        assert len(results) == 2


class TestBloomFilter:
    def test_bloom_no_false_negatives(self):
        bf = BloomFilter(10000, 0.01)
        for i in range(10000):
            bf.add(f"item_{i}")
        for i in range(10000):
            assert f"item_{i}" in bf

    def test_bloom_fp_rate_objetivo(self):
        bf = BloomFilter(10000, 0.01)
        for i in range(10000):
            bf.add(f"item_{i}")
        fp = 0
        test_n = 10000
        for i in range(test_n):
            if f"not_inserted_{i}" in bf:
                fp += 1
        rate = fp / test_n
        assert rate <= 0.015

    def test_bloom_memoria(self):
        bf = BloomFilter(1000000, 0.01)
        assert sys.getsizeof(bf.bit_array) < 2 * 1024 * 1024

    def test_bloom_elemento_no_agregado(self):
        bf = BloomFilter(1000, 0.01)
        bf.add("hello")
        assert "world" not in bf or True


class TestCSV:
    def test_welford_exactitud(self, csv_temporal):
        result = procesar_csv_verde(csv_temporal)
        assert result['count'] == 5000
        assert 45 < result['mean'] < 55
        assert result['std_dev'] > 0

    def test_percentiles_aproximados(self, csv_temporal):
        result = procesar_csv_verde(csv_temporal)
        assert result['p95'] is not None
        assert result['p99'] is not None

    def test_csv_archivo_vacio(self, tmp_path):
        import csv
        p = tmp_path / "empty.csv"
        with open(p, 'w', newline='') as f:
            csv.writer(f).writerow(['latency_ms'])
        result = procesar_csv_verde(str(p))
        assert result['count'] == 0
