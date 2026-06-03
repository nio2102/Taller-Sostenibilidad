from taller_green_code.modulo5_sci import SCI_Harness, ejecutar_benchmark_completo
from taller_green_code.modulo2_cache import fib_iterativo


class TestSCIHarness:
    def test_harness_emite_reporte_completo(self):
        harness = SCI_Harness()
        result = harness.measure(fib_iterativo, (10,), 1)
        d = result.to_dict()
        assert d['funcion'] is not None
        assert d['emisiones_kg_co2'] >= 0
        assert d['duracion_segundos'] > 0
        assert d['unidad_funcional'] == 1
        assert d['sci'] >= 0
        assert d['energia_kwh'] >= 0
        assert d['reduccion_vs_baseline'] is None

    def test_harness_sci_positivo(self):
        harness = SCI_Harness()
        result = harness.measure(lambda: sum(range(1000)), (), 100)
        assert result.sci > 0
        assert result.unidad_funcional > 0

    def test_compare_reduccion_real(self):
        def fib_contaminante(n):
            if n <= 1:
                return n
            return fib_contaminante(n - 1) + fib_contaminante(n - 2)

        harness = SCI_Harness()
        comp = harness.compare(
            fib_iterativo,
            fib_contaminante,
            (30,),
            1
        )
        assert comp.reduccion_pct > 90
        assert comp.verde.duracion_segundos < comp.contaminante.duracion_segundos

    def test_export_csv_formato(self, tmp_path):
        harness = SCI_Harness()
        result = harness.measure(fib_iterativo, (10,), 1)
        path = str(tmp_path / "report.csv")
        harness.export_csv([result], path)
        import csv
        with open(path, newline='') as f:
            reader = csv.DictReader(f)
            rows = list(reader)
            assert len(rows) == 1
            assert 'funcion' in rows[0]
            assert 'sci' in rows[0]

    def test_benchmark_completo_ejecutable(self):
        result = ejecutar_benchmark_completo()
        assert 'sci_total' in result
        assert 'resultados' in result
        assert result['sci_total'] > 0
        assert len(result['resultados']) > 0
