import time
from taller_green_code.modulo4_carbon import (
    CarbonScheduler, CarbonPredictor, EnergyCircuitBreaker, Job, VentanaCarbon
)


class TestScheduler:
    def test_scheduler_todos_asignados(self, jobs_mezclados, ventanas_carbon):
        scheduler = CarbonScheduler()
        schedule = scheduler.schedule(jobs_mezclados, ventanas_carbon)
        assert len(schedule) == len(jobs_mezclados)
        for job in jobs_mezclados:
            assert job.id in schedule
            assert 0 <= schedule[job.id] <= 23

    def test_scheduler_prefiere_ventanas_verdes(self, ventanas_carbon):
        scheduler = CarbonScheduler()
        jobs = [
            Job(id="deferrable", duracion_horas=1.0, deadline=23,
                puede_pausar=True, prioridad=3),
        ]
        schedule = scheduler.schedule(jobs, ventanas_carbon)
        start = schedule["deferrable"]
        ventanas_verdes = [v for v in ventanas_carbon if v.intensidad < 100]
        if ventanas_verdes:
            assert any(v.hora <= start < v.hora + 1 for v in ventanas_verdes)

    def test_scheduler_criticos_inmediatos(self, ventanas_carbon):
        scheduler = CarbonScheduler()
        jobs = [
            Job(id="critico", duracion_horas=0.5, deadline=1,
                puede_pausar=False, prioridad=1),
        ]
        schedule = scheduler.schedule(jobs, ventanas_carbon)
        assert "critico" in schedule

    def test_carbon_evitado_positivo(self, ventanas_carbon):
        scheduler = CarbonScheduler()
        jobs = [
            Job(id="j1", duracion_horas=1.0, deadline=23,
                puede_pausar=True, prioridad=3),
        ]
        schedule = scheduler.schedule(jobs, ventanas_carbon)
        evitado = scheduler.carbon_evitado_vs_naive(schedule, jobs, ventanas_carbon)
        low_intensity = min(v.intensidad for v in ventanas_carbon)
        high_intensity = max(v.intensidad for v in ventanas_carbon)
        if low_intensity < high_intensity:
            assert evitado >= 0

    def test_sci_estimado(self, ventanas_carbon):
        scheduler = CarbonScheduler()
        jobs = [Job(id="test", duracion_horas=1.0, deadline=23,
                     puede_pausar=True, prioridad=2)]
        schedule = scheduler.schedule(jobs, ventanas_carbon)
        sci = scheduler.sci_estimado(schedule, jobs, ventanas_carbon)
        assert sci > 0


class TestPredictor:
    def test_predictor_forma_salida(self):
        predictor = CarbonPredictor()
        historical = [
            (int(time.time()) - 86400 + i * 3600, 50 + (i % 24) * 10)
            for i in range(720)
        ]
        predictor.fit(historical)
        pred = predictor.predict(24)
        assert len(pred) == 24
        assert all(p > 0 for p in pred)

    def test_predictor_mae(self):
        predictor = CarbonPredictor()
        historical = [
            (int(time.time()) - 86400 + i * 3600, 50 + (i % 24) * 10)
            for i in range(720)
        ]
        predictor.fit(historical)
        mae = predictor.error_mae()
        assert mae >= 0


class TestCircuitBreaker:
    def test_circuit_breaker_transiciones(self):
        cb = EnergyCircuitBreaker()
        job = Job(id="j1", duracion_horas=1.0, deadline=23,
                  puede_pausar=True, prioridad=2)
        can, state = cb.check_and_act(80, job)
        assert can is True
        assert cb.get_state() == "VERDE"
        can, state = cb.check_and_act(160, job)
        assert can is True
        assert cb.get_state() == "AMARILLO"
        can, state = cb.check_and_act(290, job)
        assert cb.get_state() == "ROJO"

    def test_circuit_breaker_rojo_rechaza_baja_prioridad(self):
        cb = EnergyCircuitBreaker()
        job_alta = Job(id="j1", duracion_horas=1.0, deadline=23,
                       puede_pausar=True, prioridad=1)
        job_baja = Job(id="j2", duracion_horas=1.0, deadline=23,
                       puede_pausar=True, prioridad=3)
        cb.check_and_act(290, job_alta)
        can, state = cb.check_and_act(290, job_baja)
        assert cb.get_state() == "ROJO"
        assert can is False

    def test_circuit_breaker_reset(self):
        cb = EnergyCircuitBreaker()
        job = Job(id="j1", duracion_horas=1.0, deadline=23,
                  puede_pausar=True, prioridad=2)
        cb.check_and_act(290, job)
        assert cb.get_state() == "ROJO"
        cb.reset()
        assert cb.get_state() == "VERDE"

    def test_circuit_breaker_carbon_log(self):
        cb = EnergyCircuitBreaker()
        job = Job(id="j1", duracion_horas=1.0, deadline=23,
                  puede_pausar=True, prioridad=3)
        cb.check_and_act(290, job)
        log = cb.carbon_saved_log()
        assert len(log) >= 1
        assert 'carbon_saved_g' in log[0]
