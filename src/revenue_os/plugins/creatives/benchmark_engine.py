import time
from typing import List, Dict, Any, Callable
from src.revenue_os.plugins.creatives.models import BenchmarkResult

class CreativeBenchmarkEngine:
    """
    Motor de Benchmark de Latência, Vazão e Taxa de Erro para a Fábrica Criativa.
    """

    def run_benchmark(self, task_function: Callable[[], Any], num_iterations: int = 5) -> BenchmarkResult:
        start_total = time.time()
        successes = 0
        failures = 0
        latencies: List[float] = []

        for _ in range(num_iterations):
            step_start = time.time()
            try:
                task_function()
                successes += 1
            except Exception:
                failures += 1
            latencies.append(time.time() - step_start)

        elapsed_raw = time.time() - start_total
        total_time = max(0.0001, round(elapsed_raw, 6))
        avg_latency = round(sum(latencies) / len(latencies), 6) if latencies else 0.0
        throughput = round(num_iterations / total_time, 2)
        success_rate = round((successes / num_iterations) * 100.0, 2) if num_iterations > 0 else 0.0

        return BenchmarkResult(
            total_jobs=num_iterations,
            successful_jobs=successes,
            failed_jobs=failures,
            total_time_sec=round(total_time, 4),
            average_latency_sec=round(avg_latency, 4),
            throughput_jobs_per_sec=throughput,
            success_rate_pct=success_rate
        )
