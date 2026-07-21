# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2026-07-11

### Added
- Arquitetura base do orquestrador de vídeos autônomo (Campaign Autopilot).
- **RenderQA**: Módulo de auditoria determinística de metadados e Computer Vision (OpenCV).
- **VideoCritic**: Agente de avaliação rigorosa estruturada via TOML profiles.
- **CreativeOptimizer**: Agente retroalimentador de falhas para iteração 100% autônoma (Max 3 Tries).
- **ExperimentTracker**: Sistema de telemetria "caixa preta" persistindo logs no formato JSONL com FPY e Cache Hits O(1).
- **KnowledgeBase**: Memória JSON de padrões para evitar erros crônicos e repetições de antipadrões.
- **Integração MPT**: Adapter completo, sem estado e executando renderização via shell isolado (subprocess).

### Changed
- MoneyPrinterTurbo Adapter atualizado para usar **Cache SHA256**. O pipeline agora mapeia as dependências da stack até o motor de TTS para evitar renderizações redundantes e garantir reprodutibilidade.

### Fixed
- Extrações robustas e tratamento de falhas em integrações no nível do adaptador (MoviePy e EdgeTTS abstraídos no núcleo do MPT).
