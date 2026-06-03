# ==============================
# MODULO 4: Carbon awareness y time/demand shifting
# ==============================
#
# INSTRUCCIONES:
# Implementa las versiones "verde" de cada clase/funcion.
# Las versiones contaminantes estan como referencia.

from dataclasses import dataclass
from typing import Callable
import time
import math


@dataclass
class Job:
    id: str
    duracion_horas: float
    deadline: int
    puede_pausar: bool
    prioridad: int           # 1=critico, 2=normal, 3=diferible


@dataclass
class VentanaCarbon:
    hora: int                # 0-23
    intensidad: float        # gCO2/kWh


# ============================================================
# VERSION CONTAMINANTE — asigna todos los jobs a la hora actual
# ============================================================

class NaiveScheduler:
    def schedule(self, jobs: list[Job], ventanas: list[VentanaCarbon]) -> dict:
        return {j.id: 0 for j in jobs}

# ============================================================
# TAREA: CarbonScheduler
# ============================================================
# Scheduler que minimiza SCI de la cola de jobs.
#
# Algoritmo requerido:
# 1. Clasifica ventanas de 24h en: verde (<100), amarilla (100-250), roja (>250)
# 2. Asigna jobs diferibles (prioridad >= 2) a ventanas verdes usando greedy
# 3. Jobs criticos (prioridad = 1) se asignan a la primera hora disponible
# 4. Calcula SCI_total = suma(E_job * I_ventana) / total_requests_procesados
#
# Metodos:
# - schedule(jobs, ventanas) -> dict[str, int]  (job_id -> hora_inicio)
# - sci_estimado(schedule, jobs, ventanas) -> float
# - carbon_evitado_vs_naive(schedule, jobs, ventanas) -> float  (gCO2)
#
# PISTA: ordena las ventanas por intensidad ascendente.
# Para cada job diferible, busca la ventana verde con menor intensidad.


class CarbonScheduler:
    def schedule(self, jobs: list[Job], ventanas: list[VentanaCarbon]) -> dict:
        """Scheduler carbon-aware que minimiza SCI"""
        schedule = {}
        
        # Clasificar ventanas
        ventanas_verdes = [v for v in ventanas if v.intensidad < 100]
        ventanas_amarillas = [v for v in ventanas if 100 <= v.intensidad < 250]
        ventanas_rojas = [v for v in ventanas if v.intensidad >= 250]
        
        # Ordenar por intensidad ascendente
        ventanas_verdes.sort(key=lambda v: v.intensidad)
        ventanas_amarillas.sort(key=lambda v: v.intensidad)
        ventanas_rojas.sort(key=lambda v: v.intensidad)
        
        # Separar jobs por criticidad
        jobs_criticos = [j for j in jobs if j.prioridad == 1]
        jobs_diferibles = [j for j in jobs if j.prioridad > 1]
        
        # Asignar jobs críticos a sus deadlines más próximos
        for job in jobs_criticos:
            # Buscar ventana disponible antes del deadline
            for ventana in ventanas:
                if ventana.hora <= job.deadline:
                    schedule[job.id] = ventana.hora
                    break
            if job.id not in schedule:
                schedule[job.id] = job.deadline
        
        # Asignar jobs diferibles a ventanas verdes
        for job in jobs_diferibles:
            mejor_hora = 0
            mejor_intensidad = float('inf')
            
            # Buscar ventana verde disponible antes del deadline
            for ventana in ventanas_verdes:
                if ventana.hora <= job.deadline and ventana.intensidad < mejor_intensidad:
                    mejor_hora = ventana.hora
                    mejor_intensidad = ventana.intensidad
            
            # Si no hay ventana verde, usar amarilla
            if mejor_intensidad == float('inf'):
                for ventana in ventanas_amarillas:
                    if ventana.hora <= job.deadline and ventana.intensidad < mejor_intensidad:
                        mejor_hora = ventana.hora
                        mejor_intensidad = ventana.intensidad
            
            # Si no hay amarilla, usar roja o última hora
            if mejor_intensidad == float('inf'):
                mejor_hora = min(job.deadline, 23)
            
            schedule[job.id] = mejor_hora
        
        return schedule
    
    def sci_estimado(self, schedule: dict, jobs: list[Job], ventanas: list[VentanaCarbon]) -> float:
        """Calcula SCI estimado para el schedule"""
        ventana_map = {v.hora: v for v in ventanas}
        total_energia = 0.0
        
        for job in jobs:
            hora = schedule[job.id]
            ventana = ventana_map.get(hora, ventanas[0])
            # Asumir relación lineal: energia = duracion_horas * 0.1 kWh
            energia = job.duracion_horas * 0.1
            # SCI_job = (Energia * Intensidad_carbon) / requests
            total_energia += energia * ventana.intensidad
        
        total_requests = len(jobs) * 100  # Asumir 100 requests por job
        sci = total_energia / total_requests if total_requests > 0 else 0.0
        return sci
    
    def carbon_evitado_vs_naive(self, schedule: dict, jobs: list[Job], ventanas: list[VentanaCarbon]) -> float:
        """Calcula gCO2 evitado comparado con asignación ingenua"""
        ventana_map = {v.hora: v for v in ventanas}
        
        # Naive: todos en hora 0
        naive_carbon = 0.0
        naive_ventana = ventanas[0]
        for job in jobs:
            energia = job.duracion_horas * 0.1
            naive_carbon += energia * naive_ventana.intensidad / 1000  # convertir a kg
        
        # Óptimo: según schedule
        optimal_carbon = 0.0
        for job in jobs:
            hora = schedule[job.id]
            ventana = ventana_map.get(hora, ventanas[0])
            energia = job.duracion_horas * 0.1
            optimal_carbon += energia * ventana.intensidad / 1000
        
        return max(0.0, naive_carbon - optimal_carbon) * 1000  # convertir a gCO2


# ============================================================
# VERSION CONTAMINANTE — llama a la API cada vez
# ============================================================

class NaivePredictor:
    def predict(self, horizon_hours: int) -> list[float]:
        return [300.0] * horizon_hours

# ============================================================
# TAREA: CarbonPredictor
# ============================================================
# Predice intensidad de carbono para las proximas N horas
# usando datos historicos (serie temporal de 30 dias).
#
# Requisitos:
# - fit(historical: list[tuple[int,float]]) -> None
#   entrena con (unix_timestamp, gCO2_kWh)
# - predict(horizon_hours: int) -> list[float]
#   usa promedio movil ponderado + patron diario (24h seasonality)
# - cache: cada prediccion valida por 30min evita recalculo
# - error_mae() -> float  (mean absolute error sobre holdout set)
#
# PISTA: calcula el promedio de intensidad para cada hora del dia (0-23)
# usando los datos historicos. Combina ese patron diario (70%)
# con un promedio movil reciente (30%) para suavizar.


class CarbonPredictor:
    def __init__(self):
        self.historical = None
        self.daily_pattern = {}  # hora -> intensidad promedio
        self.last_prediction = None
        self.last_prediction_time = None
        self.cache_ttl = 1800  # 30 minutos
        self.mae = 0.0
    
    def fit(self, historical: list[tuple[int, float]]) -> None:
        """Entrena el predictor con datos históricos"""
        self.historical = historical
        
        # Calcular patrón diario (promedio por hora)
        hour_sum = {}
        hour_count = {}
        
        for timestamp, intensity in historical:
            # Convertir timestamp Unix a hora del día
            hour = (timestamp // 3600) % 24
            if hour not in hour_sum:
                hour_sum[hour] = 0.0
                hour_count[hour] = 0
            hour_sum[hour] += intensity
            hour_count[hour] += 1
        
        for hour in range(24):
            if hour in hour_sum:
                self.daily_pattern[hour] = hour_sum[hour] / hour_count[hour]
            else:
                # Completar con promedio global
                self.daily_pattern[hour] = sum(i for _, i in historical) / len(historical)
        
        # Calcular MAE en un holdout set (últimos 10% de datos)
        if len(historical) > 10:
            split_idx = int(len(historical) * 0.9)
            holdout = historical[split_idx:]
            
            errors = 0.0
            for timestamp, true_intensity in holdout:
                predicted = self.daily_pattern[(timestamp // 3600) % 24]
                errors += abs(true_intensity - predicted)
            
            self.mae = errors / len(holdout) if holdout else 0.0
    
    def predict(self, horizon_hours: int) -> list[float]:
        """Predice intensidad para las próximas N horas"""
        if not self.historical:
            return [300.0] * horizon_hours
        
        # Usar caché si está disponible
        current_time = time.time()
        if self.last_prediction_time and current_time - self.last_prediction_time < self.cache_ttl:
            return self.last_prediction[:horizon_hours]
        
        predictions = []
        current_timestamp = int(time.time())
        
        # Combinar patrón diario (70%) con promedio móvil reciente (30%)
        recent_avg = sum(i for _, i in self.historical[-24:]) / len(self.historical[-24:]) if self.historical else 300.0
        
        for h in range(horizon_hours):
            future_hour = ((current_timestamp + h * 3600) // 3600) % 24
            daily = self.daily_pattern.get(future_hour, 300.0)
            prediction = 0.7 * daily + 0.3 * recent_avg
            predictions.append(prediction)
        
        self.last_prediction = predictions
        self.last_prediction_time = current_time
        return predictions
    
    def error_mae(self) -> float:
        """Retorna el error absoluto medio"""
        return self.mae


# ============================================================
# VERSION CONTAMINANTE — ejecuta sin importar intensidad
# ============================================================

class NoBreaker:
    def check_and_act(self, intensidad: float, job: Job) -> tuple[bool, str]:
        return (True, "sin control")

# ============================================================
# TAREA: EnergyCircuitBreaker
# ============================================================
# Patron Circuit Breaker aplicado a consumo energetico.
#
# Estados: VERDE -> AMARILLO -> ROJO -> VERDE (tras cooldown)
#
# En estado ROJO:
# - Rechaza jobs de prioridad 3
# - Jobs aceptados corren con degradacion
# - Loguea gCO2 evitado por cada accion
#
# Implementa:
# - check_and_act(intensidad: float, job: Job) -> tuple[bool, str]
#   retorna (puede_ejecutar, motivo)
# - get_state() -> str
# - reset() -> None
# - carbon_saved_log() -> list[dict]
#
# Umbrales:
#   UMBRAL_AMARILLO = 150.0 gCO2/kWh
#   UMBRAL_ROJO = 280.0 gCO2/kWh
#   COOLDOWN = 1800 segundos


class EnergyCircuitBreaker:
    UMBRAL_AMARILLO = 150.0
    UMBRAL_ROJO = 280.0
    COOLDOWN_SEGUNDOS = 1800

    def __init__(self):
        self.state = "VERDE"  # VERDE, AMARILLO, ROJO
        self.last_transition_time = time.time()
        self.carbon_log = []
    
    def check_and_act(self, intensidad: float, job: Job) -> tuple[bool, str]:
        """Verifica el estado y decide si ejecutar el job"""
        # Verificar si es momento de transicionar desde ROJO
        if self.state == "ROJO":
            elapsed = time.time() - self.last_transition_time
            if elapsed >= self.COOLDOWN_SEGUNDOS:
                self.state = "VERDE"
        
        # Transicionar según intensidad
        if intensidad < self.UMBRAL_AMARILLO:
            self.state = "VERDE"
        elif intensidad < self.UMBRAL_ROJO:
            self.state = "AMARILLO"
        else:
            self.state = "ROJO"
        
        # Decidir ejecución
        if self.state == "ROJO":
            if job.prioridad == 1:  # Crítico
                # Ejecutar pero loguear
                self.carbon_log.append({
                    'timestamp': time.time(),
                    'job_id': job.id,
                    'state': self.state,
                    'intensidad': intensidad,
                    'carbon_saved_g': job.duracion_horas * 0.1 * (intensidad - self.UMBRAL_ROJO) * 100
                })
                return (True, "ROJO: crítico ejecutado")
            elif job.prioridad == 3:  # Diferible
                # Rechazar
                self.carbon_log.append({
                    'timestamp': time.time(),
                    'job_id': job.id,
                    'state': self.state,
                    'intensidad': intensidad,
                    'carbon_saved_g': job.duracion_horas * 0.1 * intensidad * 10
                })
                return (False, "ROJO: diferible rechazado")
            else:  # Normal
                # Ejecutar pero loguear
                self.carbon_log.append({
                    'timestamp': time.time(),
                    'job_id': job.id,
                    'state': self.state,
                    'intensidad': intensidad,
                    'carbon_saved_g': job.duracion_horas * 0.1 * (intensidad - self.UMBRAL_ROJO) * 50
                })
                return (True, "ROJO: normal ejecutado con degradación")
        else:
            return (True, f"Estado {self.state}: permitido")
    
    def get_state(self) -> str:
        """Retorna el estado actual del circuit breaker"""
        return self.state
    
    def reset(self) -> None:
        """Resetea el circuit breaker"""
        self.state = "VERDE"
        self.last_transition_time = time.time()
    
    def carbon_saved_log(self) -> list[dict]:
        """Retorna el log de carbono ahorrado"""
        return self.carbon_log
