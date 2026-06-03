import pytest
import random
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

random.seed(42)


@pytest.fixture
def logs_ordenados():
    n = 10000
    return sorted(
        [{'id': str(i), 'ts': i * 10, 'severity': i % 100} for i in range(n)],
        key=lambda x: x['ts']
    )


@pytest.fixture
def logs_ordenados_pequeno():
    return sorted(
        [{'id': str(i), 'ts': i, 'severity': i % 10} for i in range(20)],
        key=lambda x: x['ts']
    )


@pytest.fixture
def logs_duplicados():
    return [
        {'id': str(i % 500), 'ts': i, 'severity': i % 100}
        for i in range(10000)
    ]


@pytest.fixture
def logs_topk():
    n = 10000
    return [{'id': str(i), 'ts': i, 'severity': i % 1000} for i in range(n)]


@pytest.fixture
def user_ids():
    return list(range(1000))


@pytest.fixture
def urls_comunes():
    return [f"/api/{p}/{i}" for p in ['v1', 'v2', 'v3'] for i in range(100)]


@pytest.fixture
def ventanas_carbon():
    from taller_green_code.modulo4_carbon import VentanaCarbon
    return [VentanaCarbon(hora=h, intensidad=max(10, 50 + (h - 4) * 30 if h < 12 else 300 - (h - 12) * 20))
            for h in range(24)]


@pytest.fixture
def jobs_mezclados():
    from taller_green_code.modulo4_carbon import Job
    return [
        Job(id=f"j{i}", duracion_horas=random.uniform(0.5, 2.0),
            deadline=random.randint(6, 23), puede_pausar=bool(random.randint(0, 1)),
            prioridad=random.randint(1, 3))
        for i in range(20)
    ]


@pytest.fixture
def csv_temporal(tmp_path):
    import csv as csv_module
    p = tmp_path / "test.csv"
    with open(p, 'w', newline='') as f:
        w = csv_module.writer(f)
        w.writerow(['id', 'latency_ms', 'status'])
        for i in range(5000):
            w.writerow([i, random.gauss(50, 10), 200])
    return str(p)
