import time
from taller_green_code.modulo1_algoritmos import buscar_log_verde, dedup_verde, top_k_verde


def buscar_log_lineal(logs, timestamp):
    for entry in logs:
        if entry['ts'] == timestamp:
            return entry
    return None


class TestBusqueda:
    def test_busqueda_binaria_correcta(self, logs_ordenados):
        timestamps = [e['ts'] for e in logs_ordenados[:100]]
        for ts in timestamps:
            expected = buscar_log_lineal(logs_ordenados, ts)
            result = buscar_log_verde(logs_ordenados, ts)
            assert result == expected
        start = time.perf_counter()
        for _ in range(1000):
            buscar_log_verde(logs_ordenados, 50000)
        elapsed = time.perf_counter() - start
        assert elapsed < 1.0

    def test_busqueda_borde_vacio(self):
        assert buscar_log_verde([], 10) is None

    def test_busqueda_no_encontrado(self, logs_ordenados):
        assert buscar_log_verde(logs_ordenados, -1) is None
        assert buscar_log_verde(logs_ordenados, 9999999) is None

    def test_busqueda_primer_y_ultimo_elemento(self, logs_ordenados_pequeno):
        first = logs_ordenados_pequeno[0]
        last = logs_ordenados_pequeno[-1]
        assert buscar_log_verde(logs_ordenados_pequeno, first['ts']) == first
        assert buscar_log_verde(logs_ordenados_pequeno, last['ts']) == last


class TestDedup:
    def test_dedup_orden_preservado(self):
        logs = [
            {'id': 'a', 'data': 1},
            {'id': 'b', 'data': 2},
            {'id': 'a', 'data': 3},
            {'id': 'c', 'data': 4},
            {'id': 'b', 'data': 5},
        ]
        result = dedup_verde(logs)
        assert len(result) == 3
        assert result[0]['data'] == 1
        assert result[1]['data'] == 2
        assert result[2]['data'] == 4

    def test_dedup_todos_unicos(self):
        logs = [{'id': str(i), 'data': i} for i in range(1000)]
        result = dedup_verde(logs)
        assert result == logs

    def test_dedup_rendimiento(self, logs_duplicados):
        start = time.perf_counter()
        result = dedup_verde(logs_duplicados)
        elapsed = time.perf_counter() - start
        assert elapsed < 1.0
        assert len(result) == 500

    def test_dedup_lista_vacia(self):
        assert dedup_verde([]) == []


class TestTopK:
    def test_topk_resultado_correcto(self, logs_topk):
        expected = sorted(logs_topk, key=lambda x: x['severity'], reverse=True)[:10]
        result = top_k_verde(logs_topk, 10)
        assert result == expected

    def test_topk_k_mayor_que_n(self):
        logs = [{'id': str(i), 'ts': i, 'severity': i} for i in range(5)]
        result = top_k_verde(logs, 20)
        assert len(result) == 5
        assert result[0]['severity'] == 4

    def test_topk_rendimiento(self, logs_topk):
        start = time.perf_counter()
        _ = top_k_verde(logs_topk, 10)
        elapsed = time.perf_counter() - start
        assert elapsed < 0.8

    def test_topk_k_cero(self):
        logs = [{'id': '1', 'ts': 1, 'severity': 5}]
        assert top_k_verde(logs, 0) == []

    def test_topk_elementos_iguales(self):
        logs = [{'id': str(i), 'ts': i, 'severity': 10} for i in range(100)]
        result = top_k_verde(logs, 5)
        assert len(result) == 5
