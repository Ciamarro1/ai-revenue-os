import os
import sys
import json
import time
import random
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime, timezone, timedelta

from src.revenue_os.analytics.database import ExperimentDatabase

logger = logging.getLogger("revenue_os.pinterest_safety_coordinator")


# ──────────────────────────────────────────────
# Trust Score Event Deltas
# ──────────────────────────────────────────────
TRUST_SCORE_EVENTS: Dict[str, int] = {
    "PUBLISH_SUCCESS":          +2,
    "PUBLISH_SLOW":            -5,
    "TOAST_SLOW":             -10,
    "CAPTCHA_DETECTED":       -20,
    "LOGIN_REQUIRED":         -30,
    "RATE_LIMIT_429":         -50,
    "TEMPORARY_BLOCK":        -70,
    "ACCOUNT_SUSPENDED":     -100,
}

# ──────────────────────────────────────────────
# Ramp-up Policy (auto-scaling daily limits)
# ──────────────────────────────────────────────
RAMPUP_POLICY = [
    {"min_days": 0,   "max_days": 7,   "base_limit": 5,  "min_trust": 80},
    {"min_days": 7,   "max_days": 14,  "base_limit": 8,  "min_trust": 85},
    {"min_days": 14,  "max_days": 21,  "base_limit": 10, "min_trust": 85},
    {"min_days": 21,  "max_days": 30,  "base_limit": 15, "min_trust": 90},
    {"min_days": 30,  "max_days": 9999, "base_limit": 20, "min_trust": 90},
]

# ──────────────────────────────────────────────
# Exponential Backoff Delays (seconds)
# ──────────────────────────────────────────────
BACKOFF_DELAYS = [180, 1500, 7200]  # 3min, 25min, 2h


class PinterestSafetyCoordinator:
    """
    Coordenador de Segurança e Agendador Inteligente do Pinterest.
    
    Gerencia:
    - Trust Score numérico (0-100) com derivação de estado textual
    - Ramp-up automático de limites diários baseado em idade da conta
    - Backoff exponencial para retries inteligentes
    - Verificação de similaridade textual (anti-spam)
    - Detecção de anomalias na página do Playwright (captcha, login, 429)
    - Agendamento pseudo-aleatório de publicações
    """
    
    def __init__(self, db: Optional[ExperimentDatabase] = None):
        self.db = db or ExperimentDatabase("prod_db.sqlite3")
        self._init_state()

    def _init_state(self):
        state = self.db.get_system_state("PINTEREST_ACC_STATE")
        if not state or "trust_score" not in state:
            state = self._default_state(state)
            self.db.set_system_state("PINTEREST_ACC_STATE", state)

    @staticmethod
    def _default_state(existing: Optional[Dict] = None) -> Dict[str, Any]:
        """Retorna o estado padrão, preservando campos existentes se possível."""
        base = {
            "trust_score": 100,
            "state": "HEALTHY",
            "consecutive_failures": 0,
            "cooldown_until": None,
            "last_post_time": existing.get("last_post_time") if existing else None,
            "next_scheduled_post": existing.get("next_scheduled_post") if existing else None,
            "account_age_days": 0,
            "first_post_date": existing.get("first_post_date") if existing else None,
            "total_posts": existing.get("total_posts", 0) if existing else 0,
            "total_successes": existing.get("total_successes", 0) if existing else 0,
            "score_history": [],
        }
        return base

    # ──────────────────────────────────────────────
    # Trust Score
    # ──────────────────────────────────────────────

    def get_state(self) -> Dict[str, Any]:
        state = self.db.get_system_state("PINTEREST_ACC_STATE")
        if not state:
            state = self._default_state()
        
        # Migração: se não tem trust_score, adiciona
        if "trust_score" not in state:
            state["trust_score"] = 100
            state["account_age_days"] = 0
            state["first_post_date"] = None
            state["total_posts"] = 0
            state["total_successes"] = 0
            state["score_history"] = []
            
        # Verifica se o cooldown já expirou
        if state["state"] == "COOLDOWN" and state.get("cooldown_until"):
            try:
                cooldown_str = state["cooldown_until"]
                if cooldown_str.endswith('Z'):
                    cooldown_str = cooldown_str[:-1] + '+00:00'
                cooldown_time = datetime.fromisoformat(cooldown_str)
                if datetime.now(timezone.utc) >= cooldown_time:
                    # Recupera parcialmente o score ao sair do cooldown
                    state["trust_score"] = min(100, state["trust_score"] + 10)
                    state["state"] = self._derive_state(state["trust_score"])
                    state["consecutive_failures"] = 0
                    state["cooldown_until"] = None
                    self.db.set_system_state("PINTEREST_ACC_STATE", state)
            except Exception as e:
                logger.error(f"Erro ao verificar expiracao do cooldown: {e}")
        
        # Atualiza account_age_days dinamicamente
        if state.get("first_post_date"):
            try:
                first = state["first_post_date"]
                if first.endswith('Z'):
                    first = first[:-1] + '+00:00'
                first_dt = datetime.fromisoformat(first)
                state["account_age_days"] = (datetime.now(timezone.utc) - first_dt).days
            except Exception:
                pass
                
        return state
    
    @staticmethod
    def _derive_state(trust_score: int) -> str:
        """Deriva o estado textual a partir do Trust Score numérico."""
        if trust_score >= 80:
            return "HEALTHY"
        elif trust_score >= 50:
            return "WARNING"
        else:
            return "COOLDOWN"
    
    def update_trust_score(self, event: str) -> int:
        """
        Aplica o delta do evento ao Trust Score e persiste.
        Retorna o novo score.
        """
        delta = TRUST_SCORE_EVENTS.get(event, 0)
        if delta == 0:
            logger.warning(f"Evento de Trust Score desconhecido: {event}")
            return self.get_state().get("trust_score", 100)
        
        state = self.get_state()
        old_score = state.get("trust_score", 100)
        new_score = max(0, min(100, old_score + delta))
        
        state["trust_score"] = new_score
        state["state"] = self._derive_state(new_score)
        
        # Histórico (últimas 20 entradas)
        history = state.get("score_history", [])
        history.append({
            "event": event,
            "delta": delta,
            "old_score": old_score,
            "new_score": new_score,
            "timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        })
        state["score_history"] = history[-20:]
        
        self.db.set_system_state("PINTEREST_ACC_STATE", state)
        logger.info(f"Trust Score: {old_score} → {new_score} (evento: {event}, delta: {delta})")
        return new_score

    # ──────────────────────────────────────────────
    # Ramp-up Automático
    # ──────────────────────────────────────────────

    def get_daily_limit(self) -> int:
        """
        Calcula o limite diário dinâmico baseado na idade da conta e Trust Score.
        Regressa para fases anteriores se o Trust Score cair.
        """
        state = self.get_state()
        trust = state.get("trust_score", 100)
        age = state.get("account_age_days", 0)
        
        # Encontra a fase atual pelo age
        current_phase = RAMPUP_POLICY[0]
        for phase in RAMPUP_POLICY:
            if phase["min_days"] <= age < phase["max_days"]:
                current_phase = phase
                break
        
        # Se trust está abaixo do mínimo da fase, regressa
        effective_phase = current_phase
        if trust < current_phase["min_trust"]:
            for phase in reversed(RAMPUP_POLICY):
                if trust >= phase["min_trust"] and phase["min_days"] <= age:
                    effective_phase = phase
                    break
            else:
                effective_phase = RAMPUP_POLICY[0]  # Fase mais conservadora
        
        limit = effective_phase["base_limit"]
        
        # Se houve cooldown nos últimos 7 dias, reduz pela metade
        history = state.get("score_history", [])
        recent_cooldowns = [
            h for h in history 
            if h.get("new_score", 100) < 50
        ]
        if recent_cooldowns:
            try:
                last_cooldown_ts = recent_cooldowns[-1].get("timestamp", "")
                if last_cooldown_ts.endswith('Z'):
                    last_cooldown_ts = last_cooldown_ts[:-1] + '+00:00'
                last_cd = datetime.fromisoformat(last_cooldown_ts)
                if (datetime.now(timezone.utc) - last_cd).days < 7:
                    limit = max(3, limit // 2)
            except Exception:
                pass
        
        return limit

    # ──────────────────────────────────────────────
    # Backoff Exponencial
    # ──────────────────────────────────────────────

    def get_retry_delay(self, attempt: int) -> int:
        """
        Retorna delay em segundos com jitter.
        Retorna -1 se deve entrar em cooldown (tentativas esgotadas).
        """
        if attempt >= len(BACKOFF_DELAYS):
            return -1  # Sinaliza cooldown
        delay = BACKOFF_DELAYS[attempt]
        jitter = random.randint(0, delay // 4)
        return delay + jitter

    # ──────────────────────────────────────────────
    # Similaridade Textual (Anti-spam)
    # ──────────────────────────────────────────────

    def _lexical_similarity(self, text1: str, text2: str) -> float:
        if not text1 or not text2:
            return 0.0
        set1 = set(text1.lower().split())
        set2 = set(text2.lower().split())
        intersection = len(set1.intersection(set2))
        union = len(set1.union(set2))
        return intersection / union if union > 0 else 0.0

    def check_diversity(self, title: str, description: str) -> Dict[str, Any]:
        """
        Verifica a diversidade do conteúdo comparando com as últimas 5 publicações.
        """
        past_contents: List[Dict] = []
        try:
            with self.db._get_conn() as conn:
                c = conn.cursor()
                c.execute(
                    "SELECT payload_json FROM experiment_events WHERE event_type = 'PUBLISH_CONTENT' ORDER BY timestamp DESC LIMIT 5"
                )
                rows = c.fetchall()
                for row in rows:
                    try:
                        past_contents.append(json.loads(row[0]))
                    except Exception:
                        pass
        except Exception as e:
            logger.warning(f"Erro ao consultar historico de publicacoes: {e}")
            
        max_similarity = 0.0
        similar_title = ""
        
        for past in past_contents:
            past_title = past.get("title", "")
            past_desc = past.get("description", "")
            
            t_sim = self._lexical_similarity(title, past_title)
            d_sim = self._lexical_similarity(description, past_desc)
            
            sim = max(t_sim, d_sim)
            if sim > max_similarity:
                max_similarity = sim
                similar_title = past_title
                
        if max_similarity > 0.65:
            return {
                "safe": False,
                "reason": "DIVERSITY_LIMIT_EXCEEDED",
                "score": max_similarity,
                "detail": f"Similaridade de {max_similarity*100:.1f}% com Pin anterior: '{similar_title}'"
            }
            
        return {"safe": True, "score": max_similarity}

    # ──────────────────────────────────────────────
    # Detecção de Anomalias (Playwright)
    # ──────────────────────────────────────────────

    def check_page_anomalies(self, page) -> Optional[str]:
        """
        Varre a página do Playwright para detectar capchas, tela de login ou bloqueios.
        """
        try:
            url = page.url.lower()
            if "login" in url or "signin" in url:
                return "LOGIN_REQUIRED"
                
            # Verifica campos de login
            try:
                if page.locator("input[id='email']").first.is_visible():
                    return "LOGIN_REQUIRED"
            except Exception:
                pass
                    
            # Verifica Captchas
            captcha_selectors = [
                "iframe[src*='recaptcha']",
                "iframe[src*='arkose']",
                "div[class*='captcha']",
                "div[id*='captcha']",
                "#arkose-iframe"
            ]
            for sel in captcha_selectors:
                try:
                    if page.locator(sel).first.is_visible():
                        return "CAPTCHA_DETECTED"
                except Exception:
                    pass
                    
            # Verifica 429
            try:
                body_text = page.locator("body").inner_text().lower()
                if "too many requests" in body_text or "limite de solicitacoes" in body_text or "429" in body_text:
                    return "RATE_LIMIT_429"
            except Exception:
                pass
                
        except Exception as e:
            logger.warning(f"Erro ao verificar anomalias na pagina: {e}")
            
        return None

    # ──────────────────────────────────────────────
    # Resultado de Publicação
    # ──────────────────────────────────────────────

    def handle_publish_result(self, success: bool, error_type: Optional[str] = None, 
                              publish_duration_sec: float = 0.0, toast_duration_sec: float = 0.0):
        """
        Atualiza o estado da conta com base no resultado da publicação.
        Integra Trust Score + cooldown + agendamento.
        """
        state_data = self.get_state()
        
        if success:
            state_data["consecutive_failures"] = 0
            state_data["cooldown_until"] = None
            now_str = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
            state_data["last_post_time"] = now_str
            state_data["total_posts"] = state_data.get("total_posts", 0) + 1
            state_data["total_successes"] = state_data.get("total_successes", 0) + 1
            
            # Primeiro post: registra data
            if not state_data.get("first_post_date"):
                state_data["first_post_date"] = now_str
            
            # Trust Score: evento baseado na duração
            if publish_duration_sec > 30:
                event = "PUBLISH_SLOW"
            elif toast_duration_sec > 15:
                event = "TOAST_SLOW"
            else:
                event = "PUBLISH_SUCCESS"
            
            # Aplica delta ao score
            delta = TRUST_SCORE_EVENTS.get(event, 0)
            old_score = state_data.get("trust_score", 100)
            new_score = max(0, min(100, old_score + delta))
            state_data["trust_score"] = new_score
            state_data["state"] = self._derive_state(new_score)
            
            # Histórico
            history = state_data.get("score_history", [])
            history.append({
                "event": event,
                "delta": delta,
                "old_score": old_score,
                "new_score": new_score,
                "timestamp": now_str
            })
            state_data["score_history"] = history[-20:]
            
            # Calcula próximo agendamento pseudo-aleatório (entre 2 e 4 horas)
            delay_seconds = random.randint(2 * 3600, 4 * 3600)
            next_time = time.time() + delay_seconds
            state_data["next_scheduled_post"] = datetime.fromtimestamp(next_time, timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        else:
            state_data["consecutive_failures"] = state_data.get("consecutive_failures", 0) + 1
            state_data["total_posts"] = state_data.get("total_posts", 0) + 1
            
            # Trust Score: aplica penalidade pelo tipo de erro
            event = error_type if error_type in TRUST_SCORE_EVENTS else "PUBLISH_SLOW"
            delta = TRUST_SCORE_EVENTS.get(event, -5)
            old_score = state_data.get("trust_score", 100)
            new_score = max(0, min(100, old_score + delta))
            state_data["trust_score"] = new_score
            
            # Histórico
            history = state_data.get("score_history", [])
            history.append({
                "event": event,
                "delta": delta,
                "old_score": old_score,
                "new_score": new_score,
                "timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
            })
            state_data["score_history"] = history[-20:]
            
            is_critical = error_type in ["CAPTCHA_DETECTED", "LOGIN_REQUIRED", "RATE_LIMIT_429", "SLA_VIOLATION_CRITICAL"]
            if is_critical or state_data["consecutive_failures"] >= 3 or new_score < 50:
                state_data["state"] = "COOLDOWN"
                cooldown_hours = 24 if is_critical else 12
                cooldown_time = time.time() + cooldown_hours * 3600
                state_data["cooldown_until"] = datetime.fromtimestamp(cooldown_time, timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
                
                # Registra o AUTOPAUSE global por segurança
                reason = "PINTEREST_INTEGRATION_CRITICAL" if is_critical else "PINTEREST_CONSECUTIVE_FAILURES"
                self.db.set_system_state("AUTOPAUSE", {
                    "active": True,
                    "reason": reason,
                    "subreason": error_type or "MAX_CONSECUTIVE_FAILURES_EXCEEDED"
                })
            else:
                state_data["state"] = self._derive_state(new_score)
                
        self.db.set_system_state("PINTEREST_ACC_STATE", state_data)
