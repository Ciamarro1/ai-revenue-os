from typing import Optional, Any

from src.core.cognition.repository import CognitiveRepository
from src.core.cognition.belief_manager import BeliefManager
from src.core.cognition.evidence_engine import EvidenceEngine
from src.core.cognition.hypothesis_repository import HypothesisRepository
from src.core.cognition.hypothesis_service import HypothesisService
from src.core.cognition.reflection_repository import ReflectionRepository
from src.core.cognition.reflection_service import ReflectionService
from src.core.cognition.planning_repository import PlanningRepository
from src.core.cognition.planning_service import PlanningService
from src.core.cognition.strategy_repository import StrategyRepository
from src.core.cognition.strategy_service import StrategyService
from src.core.cognition.executive_repository import ExecutiveRepository
from src.core.cognition.executive_service import ExecutiveService
from src.core.cognition.tool_repository import ToolRepository
from src.core.cognition.tool_service import ToolRegistryService
from src.core.cognition.skill_repository import SkillRepository
from src.core.cognition.skill_service import SkillRegistryService
from src.core.memory.vector_memory import VectorMemoryProvider
from src.core.memory.retrieval import MemoryRetriever
from src.core.events.event_bus import EventBus

from src.core.belief_api import BeliefAPI
from src.core.evidence_api import EvidenceAPI
from src.core.decision_api import DecisionAPI
from src.core.memory_api import MemoryAPI
from src.core.event_api import EventAPI
from src.core.hypothesis_api import HypothesisAPI
from src.core.reflection_api import ReflectionAPI
from src.core.planning_api import PlanningAPI
from src.core.strategy_api import StrategyAPI
from src.core.executive_api import ExecutiveAPI
from src.core.tool_api import ToolAPI
from src.core.skill_api import SkillAPI

from src.ports import ProviderRegistry, MemoryPort, EventPort

class CognitiveKernel:
    """
    Cognitive Kernel Facade (Sprint 5.8).
    Unifica todos os subsistemas cognitivos sob uma interface única (Facade).
    Garante que agentes e workflows externos acessem a inteligência de forma
    indireta, protegida por contratos e rastreada por eventos.
    """
    def __init__(
        self,
        db: Any,
        qdrant_host: Optional[str] = None,
        qdrant_port: Optional[int] = None
    ):
        self.db = db
        registry = ProviderRegistry()
        
        # 1. Instanciar repositórios e gerenciadores centrais
        self.repo = CognitiveRepository(db)
        self.belief_mgr = BeliefManager(self.repo)
        self.evidence_engine = EvidenceEngine(self.repo)
        
        # 2. Instanciar/Resolver provedores de memória
        if registry.has_capability(MemoryPort):
            self.memory_provider = registry.resolve(MemoryPort)
        else:
            self.memory_provider = VectorMemoryProvider(
                db,
                qdrant_host=qdrant_host,
                qdrant_port=qdrant_port
            )
            registry.register(MemoryPort, self.memory_provider)
            
        self.memory_retriever = MemoryRetriever(self.memory_provider)
        
        # 3. Instanciar/Resolver barramento de eventos
        if registry.has_capability(EventPort):
            self.event_bus = registry.resolve(EventPort)
        else:
            self.event_bus = EventBus(db)
            registry.register(EventPort, self.event_bus)
        
        # 4. Inicializar as APIs da fronteira (facades)
        self.beliefs = BeliefAPI(self.repo, self.belief_mgr)
        self.evidence = EvidenceAPI(self.repo, self.evidence_engine)
        self.decision = DecisionAPI(self.repo)
        self.memory = MemoryAPI(self.memory_provider, self.memory_retriever)
        self.events = EventAPI(self.event_bus)
        
        self.hypothesis_repo = HypothesisRepository(db)
        self.hypothesis_service = HypothesisService(self.hypothesis_repo, self.repo)
        self.hypotheses = HypothesisAPI(self.hypothesis_repo, self.hypothesis_service)
        
        self.reflection_repo = ReflectionRepository(db)
        self.reflection_service = ReflectionService(self.reflection_repo, self.repo, db)
        self.reflections = ReflectionAPI(self.reflection_repo, self.reflection_service)
        
        self.planning_repo = PlanningRepository(db)
        self.planning_service = PlanningService(self.planning_repo, self.repo, db)
        self.planning = PlanningAPI(self.planning_repo, self.planning_service)
        
        self.strategy_repo = StrategyRepository(db)
        self.strategy_service = StrategyService(self.strategy_repo, self.planning_repo, self.repo, db)
        self.strategy = StrategyAPI(self.strategy_repo, self.strategy_service)
        
        self.executive_repo = ExecutiveRepository(db)
        self.executive_service = ExecutiveService(self.executive_repo, self.planning_repo, self.repo, db)
        self.executive = ExecutiveAPI(self.executive_repo, self.executive_service)
        
        self.tool_repo = ToolRepository(db)
        self.tool_service = ToolRegistryService(self.tool_repo, self.repo, db)
        self.tools = ToolAPI(self.tool_repo, self.tool_service)
        
        self.skill_repo = SkillRepository(db)
        self.skill_service = SkillRegistryService(self.skill_repo, self.tool_service, self.event_bus, db)
        self.skills = SkillAPI(self.skill_repo, self.skill_service)
        self.skills.service.bootstrap_default_skills()


