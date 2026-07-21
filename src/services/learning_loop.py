from typing import Optional, Dict, Any
from src.core.kernel import CognitiveKernel
from src.services.experiment_runner import ExperimentRunner, ExperimentState
from src.services.decision_queue import DecisionQueue
from src.services.observation_scheduler import ObservationScheduler
from src.core.cognition.models import Belief

class LearningLoop:
    """
    Revenue Scientist Learning Loop Orchestrator (Sprint 6.3).
    Conecta todo o pipeline cognitivo aos dados reais de negócio.
    """
    def __init__(
        self,
        kernel: CognitiveKernel,
        runner: ExperimentRunner,
        queue: DecisionQueue,
        scheduler: ObservationScheduler
    ):
        self.kernel = kernel
        self.runner = runner
        self.queue = queue
        self.scheduler = scheduler

    def execute_loop_iteration(self, related_belief_id: int) -> Dict[str, Any]:
        """
        Executa uma iteração completa do loop científico:
        1. Busca experimentos pendentes do Decision Queue.
        2. Transiciona status para 'Running'.
        3. Executa o ciclo de geração/publicação via ExperimentRunner.
        4. Transiciona status para 'Completed' (ou 'Failed' sob erro).
        5. Aciona o ObservationScheduler para coletar métricas (Observations).
        6. O Kernel atualiza Crenças e o Grafo de Evidências.
        7. Atualiza e calibra a confiança da Hipótese correspondente.
        """
        pending = self.queue.get_pending()
        if not pending:
            return {"status": "no_pending_experiments"}

        next_exp = pending[0]
        exp_id = next_exp["experiment_id"]
        hyp_id = next_exp["hypothesis_id"]

        # Transiciona para Running
        self.queue.transition_state(exp_id, "Pending", "Running")

        try:
            # Configura contexto do runner para simular a execução desse experimento específico
            self.runner.ctx = {
                "state": ExperimentState.CREATED,
                "experiment_id": exp_id,
                "hypothesis_id": hyp_id,
                "variant_id": "B"
            }
            
            # Executa até PUBLISHED
            run_result = self.runner.run_cycle(stop_at_state=ExperimentState.PUBLISHED)
            
            if run_result and run_result.get("status") == "failed":
                self.queue.update_status(exp_id, "Failed")
                return {"status": "execution_failed", "experiment_id": exp_id, "error": run_result.get("error")}

            # Adquire o content_id do runner
            content_id = self.runner.ctx.get("content_id", f"PIN-{exp_id}")
            
            # Sucesso na execução -> transiciona para Completed
            self.queue.update_status(exp_id, "Completed")

            # 5. Observation Scheduler: busca novas observações
            num_obs = self.scheduler.poll_metrics(
                content_id=content_id,
                related_belief_id=related_belief_id,
                experiment_id=exp_id
            )

            # 6. Avaliação/Calibração na Hipótese com base no impacto da última evidência
            evidences = self.kernel.evidence.get_by_experiment(exp_id)
            if evidences:
                latest_ev = evidences[0] # ordenada decrescente por ID, então a primeira é a última criada
                is_supporting = latest_ev.impact == "positivo"
                self.kernel.hypotheses.evaluate(
                    hypothesis_id=hyp_id,
                    evidence_id=latest_ev.id,
                    is_supporting=is_supporting,
                    learning_rate=0.15
                )

            return {
                "status": "success",
                "experiment_id": exp_id,
                "content_id": content_id,
                "observations_count": num_obs
            }

        except Exception as e:
            self.queue.update_status(exp_id, "Failed")
            return {"status": "failed", "experiment_id": exp_id, "error": str(e)}
