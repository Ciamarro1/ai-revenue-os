import sys
import time
from pathlib import Path
sys.stdout.reconfigure(encoding='utf-8')
sys.path.append(str(Path(__file__).parent.parent))

from rich.live import Live
from rich.table import Table
from rich.layout import Layout
from rich.panel import Panel
from rich.console import Console
from rich.text import Text
from rich.progress_bar import ProgressBar

from src.revenue_os.analytics.database import ExperimentDatabase
from src.revenue_os.analytics.aggregator import MetricsAggregator

def _trust_bar(score: int) -> str:
    """Gera barra visual colorida para Trust Score."""
    filled = score // 5  # 20 blocos
    empty = 20 - filled
    if score >= 80:
        color = "green"
    elif score >= 50:
        color = "yellow"
    else:
        color = "red"
    bar = f"[bold {color}]{'█' * filled}{'░' * empty}[/bold {color}] {score}/100"
    return bar

def generate_layout(aggregator: MetricsAggregator) -> Layout:
    snapshot = aggregator.get_snapshot()
    
    layout = Layout()
    layout.split_column(
        Layout(name="header", size=3),
        Layout(name="main")
    )
    layout["header"].update(Panel("[bold cyan]AI Revenue OS - Autonomous Dashboard v2.0[/bold cyan]", style="blue"))
    
    layout["main"].split_row(
        Layout(name="left", ratio=3),
        Layout(name="right", ratio=2),
    )
    
    # === LEFT: System + Pinterest ===
    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("Metric", style="dim", width=30)
    table.add_column("Value")
    
    table.add_row("Research Queue (CREATED)", str(snapshot.research_queue_size))
    table.add_row("Rendering Queue (HYPOTHESIZED)", str(snapshot.rendering_queue_size))
    table.add_row("Calibration Queue (PUBLISHED)", str(snapshot.calibration_queue_size))
    table.add_row("Policy Violations", str(snapshot.policy_violations))
    
    fh = snapshot.factory_health
    table.add_row("---", "---")
    table.add_row("Factory Health Status", fh["status"])
    table.add_row("Avg Render Time (P50)", f"{fh['avg_render_time']}s")
    table.add_row("Avg CPU", f"{fh['avg_cpu']}%")
    table.add_row("Avg RAM", f"{fh['avg_ram']}MB")
    
    ps = snapshot.pinterest_state
    table.add_row("---", "---")
    
    # Trust Score com barra visual
    trust = ps.get("trust_score", 100)
    table.add_row("[bold]Pinterest Trust Score[/bold]", _trust_bar(trust))
    
    p_state = ps.get("state", "HEALTHY")
    state_color = "green" if p_state == "HEALTHY" else ("yellow" if p_state == "WARNING" else "red")
    table.add_row("Account State", f"[bold {state_color}]{p_state}[/bold {state_color}]")
    
    daily_limit = ps.get("daily_limit", 5)
    posts_today = ps.get("posts_today", 0)
    table.add_row("Posts Today", f"{posts_today} / {daily_limit}")
    table.add_row("Consecutive Failures", f"{ps.get('consecutive_failures', 0)} / 3")
    table.add_row("Account Age", f"{ps.get('account_age_days', 0)} dias")
    table.add_row("Total Posts (Lifetime)", str(ps.get("total_posts", 0)))
    table.add_row("Last Post Time", ps.get("last_post_time") or "N/A")
    
    if p_state == "COOLDOWN":
        table.add_row("Cooldown Until", f"[red]{ps.get('cooldown_until') or 'N/A'}[/red]")
    else:
        table.add_row("Next Scheduled Post", ps.get("next_scheduled_post") or "N/A")
    
    # Score History (últimas 5)
    history = ps.get("score_history", [])
    if history:
        table.add_row("---", "---")
        table.add_row("[bold]Score History (Recent)[/bold]", "")
        for h in history[-5:]:
            delta = h.get("delta", 0)
            delta_str = f"[green]+{delta}[/green]" if delta > 0 else f"[red]{delta}[/red]"
            table.add_row(f"  {h.get('event', '?')}", f"{h.get('old_score', '?')} → {h.get('new_score', '?')} ({delta_str})")
    
    layout["left"].update(Panel(table, title="System Snapshot"))
    
    # === RIGHT: Queue + Boards ===
    right_table = Table(show_header=True, header_style="bold cyan")
    right_table.add_column("Metric", style="dim", width=25)
    right_table.add_column("Value")
    
    qs = snapshot.queue_stats
    right_table.add_row("[bold]Publication Queue[/bold]", "")
    right_table.add_row("Pending Jobs", str(qs.get("pending", 0)))
    right_table.add_row("Processing", str(qs.get("processing", 0)))
    right_table.add_row("Published Today", str(qs.get("published_today", 0)))
    
    # Feature Flags status
    right_table.add_row("---", "---")
    right_table.add_row("[bold]Feature Flags[/bold]", "")
    try:
        from src.revenue_os.analytics.feature_flags import FeatureFlags
        flags = FeatureFlags()
        for name, enabled in sorted(flags.get_all().items()):
            status = "[green]ON[/green]" if enabled else "[dim]OFF[/dim]"
            short_name = name.replace("ENABLE_", "")
            right_table.add_row(f"  {short_name}", status)
    except Exception:
        right_table.add_row("  (não disponível)", "")
    
    # Board Stats
    if snapshot.board_stats:
        right_table.add_row("---", "---")
        right_table.add_row("[bold]Board Metrics[/bold]", "")
        for b in snapshot.board_stats:
            right_table.add_row(f"  {b.get('board_name', '?')}", 
                                f"Posts: {b.get('total_posts', 0)} | CTR: {b.get('avg_ctr', 0):.1f}% | Trust: {b.get('trust_score', 100)}")
    
    layout["right"].update(Panel(right_table, title="Queue & Boards"))
    
    return layout

def main():
    db = ExperimentDatabase("prod_db.sqlite3")
    aggregator = MetricsAggregator(db)
    
    print("Iniciando dashboard ao vivo... (Pressione Ctrl+C para sair)")
    
    with Live(generate_layout(aggregator), refresh_per_second=1, screen=True) as live:
        try:
            while True:
                live.update(generate_layout(aggregator))
                time.sleep(2)
        except KeyboardInterrupt:
            pass

if __name__ == "__main__":
    main()
