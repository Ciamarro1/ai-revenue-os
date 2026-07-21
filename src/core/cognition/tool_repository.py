import sqlite3
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional
from src.core.cognition.models import Provider, Tool, Capability, ToolExecution

class ToolRepository:
    """
    ToolRepository (Sprint 7.1).
    Persiste e recupera provedores, ferramentas, capacidades e logs de execução.
    """
    def __init__(self, db: Any):
        self.db = db

    def _get_conn(self):
        return self.db._get_conn()

    # ==========================================
    # Provedores (Providers)
    # ==========================================
    def save_provider(self, provider: Provider) -> Provider:
        ts = datetime.now(timezone.utc).isoformat() + "Z"
        with self._get_conn() as conn:
            c = conn.cursor()
            if provider.id is None:
                c.execute("""
                    INSERT INTO providers (name, description, status, created_at)
                    VALUES (?, ?, ?, ?)
                """, (provider.name, provider.description, provider.status, ts))
                provider.id = c.lastrowid
                provider.created_at = ts
            else:
                c.execute("""
                    UPDATE providers SET name = ?, description = ?, status = ? WHERE id = ?
                """, (provider.name, provider.description, provider.status, provider.id))
            conn.commit()
        return provider

    def get_provider(self, provider_id: int) -> Optional[Provider]:
        with self._get_conn() as conn:
            c = conn.cursor()
            c.execute("SELECT id, name, description, status, created_at FROM providers WHERE id = ?", (provider_id,))
            r = c.fetchone()
            if r:
                return Provider(id=r[0], name=r[1], description=r[2], status=r[3], created_at=r[4])
        return None

    def get_providers(self) -> List[Provider]:
        with self._get_conn() as conn:
            c = conn.cursor()
            c.execute("SELECT id, name, description, status, created_at FROM providers ORDER BY id DESC")
            rows = c.fetchall()
            return [Provider(id=r[0], name=r[1], description=r[2], status=r[3], created_at=r[4]) for r in rows]

    # ==========================================
    # Ferramentas (Tools)
    # ==========================================
    def save_tool(self, tool: Tool) -> Tool:
        ts = datetime.now(timezone.utc).isoformat() + "Z"
        with self._get_conn() as conn:
            c = conn.cursor()
            if tool.id is None:
                c.execute("""
                    INSERT INTO tools (name, version, provider_id, capabilities, cost, latency, reliability, health_score, created_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (tool.name, tool.version, tool.provider_id, tool.capabilities, tool.cost, tool.latency, tool.reliability, tool.health_score, ts))
                tool.id = c.lastrowid
                tool.created_at = ts
            else:
                c.execute("""
                    UPDATE tools SET name = ?, version = ?, provider_id = ?, capabilities = ?, cost = ?, latency = ?, reliability = ?, health_score = ?
                    WHERE id = ?
                """, (tool.name, tool.version, tool.provider_id, tool.capabilities, tool.cost, tool.latency, tool.reliability, tool.health_score, tool.id))
            conn.commit()
        return tool

    def get_tool(self, tool_id: int) -> Optional[Tool]:
        with self._get_conn() as conn:
            c = conn.cursor()
            c.execute("""
                SELECT id, name, version, provider_id, capabilities, cost, latency, reliability, health_score, created_at
                FROM tools WHERE id = ?
            """, (tool_id,))
            r = c.fetchone()
            if r:
                return Tool(id=r[0], name=r[1], version=r[2], provider_id=r[3], capabilities=r[4], cost=r[5], latency=r[6], reliability=r[7], health_score=r[8], created_at=r[9])
        return None

    def get_tools(self) -> List[Tool]:
        with self._get_conn() as conn:
            c = conn.cursor()
            c.execute("""
                SELECT id, name, version, provider_id, capabilities, cost, latency, reliability, health_score, created_at
                FROM tools ORDER BY id DESC
            """)
            rows = c.fetchall()
            return [
                Tool(id=r[0], name=r[1], version=r[2], provider_id=r[3], capabilities=r[4], cost=r[5], latency=r[6], reliability=r[7], health_score=r[8], created_at=r[9])
                for r in rows
            ]

    def get_tools_by_capability(self, cap_name: str) -> List[Tool]:
        # Busca ferramentas que contenham a cap_name na lista separada por vírgulas
        all_tools = self.get_tools()
        matched = []
        for t in all_tools:
            caps = [c.strip() for c in t.capabilities.split(",")]
            if cap_name in caps:
                matched.append(t)
        return matched

    # ==========================================
    # Capacidades (Capabilities)
    # ==========================================
    def save_capability(self, cap: Capability) -> Capability:
        ts = datetime.now(timezone.utc).isoformat() + "Z"
        with self._get_conn() as conn:
            c = conn.cursor()
            if cap.id is None:
                c.execute("""
                    INSERT INTO capabilities (name, description, created_at)
                    VALUES (?, ?, ?)
                    ON CONFLICT(name) DO UPDATE SET description = excluded.description
                """, (cap.name, cap.description, ts))
                c.execute("SELECT id, created_at FROM capabilities WHERE name = ?", (cap.name,))
                r = c.fetchone()
                if r:
                    cap.id = r[0]
                    cap.created_at = r[1]
            else:
                c.execute("""
                    UPDATE capabilities SET name = ?, description = ? WHERE id = ?
                """, (cap.name, cap.description, cap.id))
            conn.commit()
        return cap

    def get_capability(self, cap_id: int) -> Optional[Capability]:
        with self._get_conn() as conn:
            c = conn.cursor()
            c.execute("SELECT id, name, description, created_at FROM capabilities WHERE id = ?", (cap_id,))
            r = c.fetchone()
            if r:
                return Capability(id=r[0], name=r[1], description=r[2], created_at=r[3])
        return None

    def get_capabilities(self) -> List[Capability]:
        with self._get_conn() as conn:
            c = conn.cursor()
            c.execute("SELECT id, name, description, created_at FROM capabilities ORDER BY id DESC")
            rows = c.fetchall()
            return [Capability(id=r[0], name=r[1], description=r[2], created_at=r[3]) for r in rows]

    # ==========================================
    # Histórico de Execução de Ferramentas (ToolExecutions)
    # ==========================================
    def log_tool_execution(self, exec_data: ToolExecution) -> ToolExecution:
        ts = datetime.now(timezone.utc).isoformat() + "Z"
        with self._get_conn() as conn:
            c = conn.cursor()
            c.execute("""
                INSERT INTO tool_executions (tool_id, latency, cost, success, error_message, executed_at)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (exec_data.tool_id, exec_data.latency, exec_data.cost, exec_data.success, exec_data.error_message, ts))
            exec_data.id = c.lastrowid
            exec_data.executed_at = ts
            conn.commit()
        
        # Atualiza métricas agregadas da ferramenta de forma rolante (decay/rolling update)
        self.update_tool_stats(exec_data.tool_id, exec_data.latency, exec_data.success)
        return exec_data

    def get_tool_executions(self, tool_id: int) -> List[ToolExecution]:
        with self._get_conn() as conn:
            c = conn.cursor()
            c.execute("""
                SELECT id, tool_id, latency, cost, success, error_message, executed_at
                FROM tool_executions WHERE tool_id = ? ORDER BY id DESC
            """, (tool_id,))
            rows = c.fetchall()
            return [
                ToolExecution(id=r[0], tool_id=r[1], latency=r[2], cost=r[3], success=bool(r[4]), error_message=r[5], executed_at=r[6])
                for r in rows
            ]

    def update_tool_stats(self, tool_id: int, latency: float, success: bool) -> None:
        tool = self.get_tool(tool_id)
        if not tool:
            return

        # Média móvel ponderada: 80% histórico + 20% nova medição
        new_latency = (tool.latency * 0.8) + (latency * 0.2) if tool.latency > 0 else latency
        
        # Confiabilidade móvel: 90% histórico + 10% novo status (1.0 ou 0.0)
        success_val = 1.0 if success else 0.0
        new_reliability = (tool.reliability * 0.9) + (success_val * 0.1)

        # Health score cai 0.2 se falhar, ou sobe 0.05 se suceder (limitado a 0.0 - 1.0)
        if success:
            new_health = min(1.0, tool.health_score + 0.05)
        else:
            new_health = max(0.0, tool.health_score - 0.2)

        with self._get_conn() as conn:
            c = conn.cursor()
            c.execute("""
                UPDATE tools SET latency = ?, reliability = ?, health_score = ?
                WHERE id = ?
            """, (new_latency, new_reliability, new_health, tool_id))
            conn.commit()
