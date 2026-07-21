import os
import json
import time
import base64
import logging
from pathlib import Path
from typing import Dict, Any, Optional
import requests

from playwright.sync_api import sync_playwright, Page, BrowserContext
from src.execution.publisher.base import BasePublisher
from src.reality.social.pinterest.safety_coordinator import PinterestSafetyCoordinator

logger = logging.getLogger("execution.publisher.pinterest")

class PinterestPlaywrightPublisher(BasePublisher):
    """
    Publisher do Pinterest baseado em Playwright.
    Executa fluxos de publicação determinísticos e possui fallback cognitivo via Vision LLM (OpenRouter).
    """

    def __init__(self, openrouter_key: Optional[str] = None):
        super().__init__("pinterest")
        self.safety_coordinator = PinterestSafetyCoordinator()
        # Tenta carregar a chave do OpenRouter do ambiente ou usa fallback do config.toml
        self.openrouter_key = openrouter_key or os.getenv("OPENROUTER_API_KEY")
        if not self.openrouter_key:
            # Carrega a partir do config.toml do MoneyPrinterTurbo se disponível
            try:
                mpt_config_path = Path("MoneyPrinterTurbo/config.toml")
                if mpt_config_path.exists():
                    import tomllib
                    with open(mpt_config_path, "rb") as f:
                        cfg = tomllib.load(f)
                        self.openrouter_key = cfg.get("app", {}).get("openai_api_key")
            except Exception as e:
                logger.warning(f"Erro ao carregar chave do OpenRouter: {e}")

    def _query_vision_model(self, screenshot_path: Path, prompt: str) -> Optional[Dict[str, Any]]:
        """
        Envia a captura de tela e o prompt para o modelo de visão da API OpenRouter/Gemini.
        """
        if not self.openrouter_key:
            logger.error("Chave da API OpenRouter não configurada. Fallback por visão indisponível.")
            return None

        try:
            with open(screenshot_path, "rb") as image_file:
                base64_image = base64.b64encode(image_file.read()).decode("utf-8")

            headers = {
                "Authorization": f"Bearer {self.openrouter_key}",
                "Content-Type": "application/json",
                "HTTP-Referer": "https://github.com/google/ai-revenue-os",
                "X-Title": "AI Revenue OS Publisher"
            }

            payload = {
                "model": "google/gemini-2.5-flash",
                "messages": [
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": prompt + "\nRetorne a resposta estritamente no formato JSON, ex: {\"x\": 350, \"y\": 420, \"selector\": \"#publish-btn\"}. Não use markdown block de código JSON."
                            },
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/png;base64,{base64_image}"
                                }
                            }
                        ]
                    }
                ],
                "response_format": {"type": "json_object"}
            }

            logger.info("Enviando screenshot para o modelo de visão...")
            response = requests.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers=headers,
                json=payload,
                timeout=30
            )

            if response.status_code == 200:
                result_json = response.json()["choices"][0]["message"]["content"]
                return json.loads(result_json)
            else:
                logger.error(f"Erro na chamada do Vision Model: HTTP {response.status_code} - {response.text}")
        except Exception as e:
            logger.error(f"Exceção ao chamar Vision Model: {e}")

        return None

    def _interact_with_fallback(self, page: Page, action_desc: str, prompt: str, default_selector: Optional[str] = None, evidence_dir: Optional[Path] = None) -> bool:
        """
        Tenta interagir com a página. Se falhar, usa o Vision Fallback.
        """
        if default_selector:
            try:
                page.wait_for_selector(default_selector, timeout=5000)
                if "click" in action_desc:
                    page.click(default_selector)
                return True
            except Exception as e:
                logger.warning(f"Falha ao usar seletor padrão '{default_selector}' para '{action_desc}': {e}. Acionando Vision Fallback...")

        # Tira screenshot de falha
        screenshot_dir = evidence_dir or Path("cache/screenshots")
        screenshot_dir.mkdir(parents=True, exist_ok=True)
        screenshot_path = screenshot_dir / f"fail_{action_desc.replace(' ', '_')}_{int(time.time())}.png"
        page.screenshot(path=str(screenshot_path))

        # Consulta o Vision Model com prompt aprimorado
        vision_result = self._query_vision_model(
            screenshot_path,
            f"Estou tentando executar a seguinte ação no Pinterest: {prompt}. "
            "Por favor, analise a tela e encontre preferencialmente um seletor textual do Playwright "
            "(ex: 'text=\"Salvar\"' ou 'text=\"Adicionar\"') que identifique o elemento de forma única. "
            "Se não for possível encontrar um seletor textual confiável, retorne as coordenadas "
            "de pixel (x, y) do centro do elemento na imagem."
        )

        if vision_result:
            x = vision_result.get("x")
            y = vision_result.get("y")
            sel = vision_result.get("selector")

            if sel:
                try:
                    logger.info(f"Tentando clique no seletor retornado pela visão: {sel}")
                    page.wait_for_selector(sel, timeout=5000)
                    page.click(sel)
                    return True
                except Exception as sel_err:
                    logger.warning(f"Falha ao clicar no seletor da visão '{sel}': {sel_err}. Tentando coordenadas.")

            if x is not None and y is not None:
                logger.info(f"Clicando nas coordenadas retornadas pela visão: ({x}, {y})")
                page.mouse.click(x, y)
                return True

        return False

    def publish(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Realiza a publicação de um Pin (vídeo ou imagem) usando Playwright.
        """
        media_path = payload.get("media_path")
        title = payload.get("title", "Sem título")
        description = payload.get("description", "")
        link = payload.get("link", "")
        board_name = payload.get("board", "default")
        headless = payload.get("headless", True)
        experiment_id = payload.get("experiment_id")

        if not media_path or not os.path.exists(media_path):
            raise FileNotFoundError(f"Arquivo de mídia não encontrado: {media_path}")

        session_file = self.get_session_path()
        test_url = payload.get("test_url")
        
        if not test_url and not session_file.exists():
            raise FileNotFoundError(
                "Sessão de autenticação não encontrada! Execute primeiro o utilitário 'setup_session.py'."
            )

        # Prepara diretório de evidências do experimento se informado
        evidence_dir = None
        steps_log = []
        if experiment_id:
            evidence_dir = Path("experiments") / experiment_id / "publication_evidence"
            evidence_dir.mkdir(parents=True, exist_ok=True)

        def log_step(name: str, status: str, details: str = ""):
            entry = {"step": name, "status": status, "details": details, "timestamp": time.time()}
            steps_log.append(entry)
            logger.info(f"[{name}] {status} - {details}")

        result = {
            "status": "failed",
            "url": None,
            "pin_id": None,
            "error": None
        }

        with sync_playwright() as p:
            log_step("Browser Launch", "start")
            browser = p.chromium.launch(
                headless=headless,
                args=[
                    "--disable-blink-features=AutomationControlled",
                    "--use-fake-ui-for-media-stream"
                ]
            )
            
            # Carrega a sessão/cookies salvos se existir, e força Viewport 1280x800
            ctx_args = {"viewport": {"width": 1280, "height": 800}}
            if session_file.exists():
                ctx_args["storage_state"] = str(session_file)
                
            context = browser.new_context(**ctx_args)
            page = context.new_page()
            
            try:
                # 1. Navegar para a página do Pin Builder do Pinterest
                log_step("Navigate Pin Builder", "start")
                target_url = test_url or "https://www.pinterest.com/pin-builder/"
                page.goto(target_url, timeout=60000)
                page.wait_for_load_state("domcontentloaded")
                
                # Auto-descartar modais de onboarding/tutoriais se houver
                time.sleep(5)
                logger.info("Tentando fechar pop-ups e tutoriais iniciais...")
                page.keyboard.press("Escape")
                time.sleep(2)

                # Verifica se fomos redirecionados para a tela de login ou outra anomalia
                anomaly = self.safety_coordinator.check_page_anomalies(page)
                if anomaly:
                    log_step("Navigate Pin Builder", "failed", f"Anomalia detectada: {anomaly}")
                    raise RuntimeError(f"Pinterest safety anomaly detected: {anomaly}")
                
                if "login" in page.url and not test_url:
                    log_step("Navigate Pin Builder", "failed", "Sessão expirada ou inválida")
                    raise RuntimeError("Sessão expirada! Por favor, execute setup_session.py novamente. [LOGIN_REQUIRED]")
                log_step("Navigate Pin Builder", "success")

                # 2. Upload de Mídia (Input de arquivo)
                logger.info("Realizando upload da mídia...")
                file_input_selector = "input[type='file']"
                page.wait_for_selector(file_input_selector, timeout=10000)
                page.set_input_files(file_input_selector, os.path.abspath(media_path))
                time.sleep(4) # Aguarda preview / upload do arquivo

                # 3. Preenchimento de Título
                log_step("Fill Title", "start")
                title_selector = "textarea[placeholder*='título'], textarea[placeholder*='title'], input[placeholder*='título'], input[placeholder*='title'], [data-testid='pin-builder-title']"
                title_filled = False
                for sel in title_selector.split(", "):
                    try:
                        if page.is_visible(sel):
                            page.fill(sel, title)
                            title_filled = True
                            break
                    except Exception:
                        continue
                
                if not title_filled:
                    self._interact_with_fallback(
                        page,
                        "Preencher título",
                        f"Encontre a caixa de texto para digitar o título '{title}'",
                        default_selector="[data-testid='pin-builder-title']",
                        evidence_dir=evidence_dir
                    )
                    page.keyboard.type(title)
                log_step("Fill Title", "success")

                # 4. Preenchimento de Descrição
                log_step("Fill Description", "start")
                desc_selector = "div[contenteditable='true'], textarea[placeholder*='descrição'], [aria-label*='descrição'], [aria-label*='description'], [data-testid='pin-builder-description']"
                desc_filled = False
                for sel in desc_selector.split(", "):
                    try:
                        if page.is_visible(sel):
                            page.fill(sel, description)
                            desc_filled = True
                            break
                    except Exception:
                        continue

                if not desc_filled:
                    self._interact_with_fallback(
                        page,
                        "Preencher descrição",
                        f"Encontre o campo de descrição ou caixa de texto de conteúdo para digitar '{description}'",
                        evidence_dir=evidence_dir
                    )
                    page.keyboard.type(description)
                log_step("Fill Description", "success")

                # 5. Preenchimento de Link
                if link:
                    log_step("Fill Link", "start")
                    link_selector = "textarea[placeholder*='link'], textarea[placeholder*='destino'], input[placeholder*='link'], [data-testid='pin-builder-link']"
                    link_filled = False
                    for sel in link_selector.split(", "):
                        try:
                            if page.is_visible(sel):
                                page.fill(sel, link)
                                link_filled = True
                                break
                        except Exception:
                            continue

                    if not link_filled:
                        self._interact_with_fallback(
                            page,
                            "Preencher link",
                            f"Encontre a caixa de texto do link de destino para digitar '{link}'",
                            evidence_dir=evidence_dir
                        )
                        page.keyboard.type(link)
                    log_step("Fill Link", "success")

                # 5.5 Selecionar ou Criar Pasta (Board)
                logger.info("Selecionando pasta (board)...")
                board_dropdown = page.locator("button[data-testid='board-dropdown-select-button'], div[data-testid='board-dropdown-select-button'], [aria-label*='pasta'], [aria-label*='board'], div:text-is('Selecionar'), button:has-text('Selecionar')").first
                if board_dropdown.count() > 0 and board_dropdown.is_visible():
                    board_dropdown.click()
                    time.sleep(2)
                    
                    # Procura o campo de pesquisa do dropdown
                    search_input = page.locator("input[placeholder*='Pesquisar'], input[placeholder*='Search'], input[placeholder*='pesquisar']").first
                    if search_input.count() > 0 and search_input.is_visible():
                        logger.info("Filtrando pasta por nome 'AI Revenue OS'...")
                        search_input.fill("AI Revenue OS")
                        time.sleep(2.5) # Aguarda o filtro da API do Pinterest
                        
                        no_results = page.locator("text='Nenhuma pasta encontrada', text='No boards found'")
                        if no_results.count() > 0 and no_results.first.is_visible():
                            logger.info("Pasta 'AI Revenue OS' nao existe. Criando nova pasta...")
                            create_board_btn = page.locator("text='Criar pasta'").first
                            if create_board_btn.count() > 0 and create_board_btn.is_visible():
                                create_board_btn.click()
                                time.sleep(2)
                                
                                # Preenche o nome da pasta no modal de criação
                                board_name_input = page.locator("input[placeholder*='Lugares'], input[placeholder*='Receitas'], input[id*='board-name']").first
                                if board_name_input.count() > 0:
                                    board_name_input.fill("AI Revenue OS")
                                    time.sleep(1)
                                    
                                    # Confirma a criação
                                    create_confirm_btn = page.locator("button:text-is('Criar')").first
                                    if create_confirm_btn.count() > 0:
                                        create_confirm_btn.click()
                                        time.sleep(4) # Aguarda criação e seleção automática
                        else:
                            # A pasta já existe e foi filtrada! Clica nela na lista
                            board_option = page.locator("div[role='list'] div[role='button']:has-text('AI Revenue OS'), div[role='option']:has-text('AI Revenue OS'), text='AI Revenue OS'").last
                            if board_option.count() > 0:
                                logger.info("Pasta 'AI Revenue OS' encontrada na lista. Selecionando...")
                                board_option.click()
                                time.sleep(1)
                            else:
                                logger.info("Selecionando pasta filtrada via teclado...")
                                page.keyboard.press("ArrowDown")
                                page.keyboard.press("Enter")
                                time.sleep(1)

                # 6. Publicar Pin
                log_step("Publish Button Click", "start")
                publish_selector = "div[role='button']:has-text('Publicar'), button:has-text('Publicar'), button[data-testid='board-dropdown-save-button'], button[type='submit'], text='Publicar', text='Avançar', button:has-text('Salvar')"
                publish_clicked = False
                for sel in publish_selector.split(", "):
                    try:
                        if page.is_visible(sel):
                            page.click(sel)
                            publish_clicked = True
                            break
                    except Exception:
                        continue

                if not publish_clicked:
                    self._interact_with_fallback(
                        page,
                        "Clicar em publicar",
                        "Encontre o botão de salvar, salvar alteração ou publicar no topo direito",
                        evidence_dir=evidence_dir
                    )
                log_step("Publish Button Click", "success")

                # Aguarda o redirecionamento ou pop-up de sucesso
                logger.info("Aguardando confirmação de publicação...")
                time.sleep(8)
                
                # Tenta localizar a toast/modal de sucesso de publicação para extrair o link real do Pin
                published_url = page.url
                try:
                    toast_link = page.locator("a[href*='/pin/']").first
                    if toast_link.count() > 0:
                        href = toast_link.get_attribute("href")
                        if href:
                            if href.startswith("/"):
                                published_url = "https://www.pinterest.com" + href
                            else:
                                published_url = href
                except Exception as e:
                    logger.warning(f"Não foi possível extrair a URL exata do Pin via link de sucesso: {e}")

                logger.info(f"URL final pós-publicação: {published_url}")
                
                # Salva screenshot final de sucesso se o diretório de evidência estiver ativo
                if evidence_dir:
                    page.screenshot(path=str(evidence_dir / "publish_success.png"))

                result["status"] = "success"
                result["url"] = published_url
                result["pin_id"] = published_url.split("/")[-2] if "pin/" in published_url else f"PL-{int(time.time())}"
                log_step("Workflow End", "success", f"Pin publicado: {result['url']}")

            except Exception as e:
                log_step("Workflow Error", "failed", str(e))
                result["error"] = str(e)
                # Extrai o tipo de anomalia de seguranca para sinalizar o circuit breaker
                for anomaly_type in ["CAPTCHA_DETECTED", "LOGIN_REQUIRED", "RATE_LIMIT_429"]:
                    if anomaly_type in str(e):
                        result["error_type"] = anomaly_type
                        break
            finally:
                # Salva os logs das etapas na evidência do experimento
                if evidence_dir:
                    with open(evidence_dir / "publication_evidence.json", "w", encoding="utf-8") as f:
                        json.dump({"steps": steps_log, "result": result}, f, indent=2, ensure_ascii=False)
                context.close()
                browser.close()

        return result
