# KNOWN FAILURES (FALHAS CONHECIDAS)

Registro de assinaturas de erros recorrentes de APIs e infraestrutura e seus respectivos procedimentos de mitigação.

## F-001: Playwright Session Expiration
* **Erro**: Redirecionamento forçado para a tela de login (`/login/`) durante a tentativa de postagem no Pinterest.
* **Causa**: Cookies de sessão expiram ou foram invalidados pelo Pinterest.
* **Solução**: Rodar manualmente `.\venv\Scripts\python scripts/setup_session.py` para re-autenticar o perfil.

## F-002: MoneyPrinterTurbo Rendering Timeout
* **Erro**: Timeout ou processo travado durante subprocess call de FFMPEG na geração de vídeos.
* **Causa**: CPU local saturada ou arquivos de áudio corrompidos passados para o MPT.
* **Solução**: Reiniciar os workers e verificar as faixas de áudio do creative.
