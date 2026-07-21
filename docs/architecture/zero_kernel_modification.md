# AI Revenue OS — Política de Modificação Zero no Kernel (v6.0)

> **Diretriz de Produção**: *Zero-Kernel Modification. All Features as Drop-in Plugins.*  
> O **AI Revenue OS (v6.0)** atingiu o estado de conclusão de engenharia de infraestrutura (*Feature Complete Kernel*). Nenhuma nova abstração, gerenciador ou classe de framework será criada no Kernel.

---

## 🔒 Regra de Desenvolvimento por Plugins

1. **Desenvolvimento Exclusivo via SDK**: 100% dos novos conectores de mídia, geradores visuais, integradores de marketplace, ferramentas de analytics e plataformas sociais devem ser implementados estritamente como **Plugins Drop-in** utilizando o **AI Revenue OS Plugin SDK** (`src/revenue_os/sdk/`).
2. **Manutenção Mínima**: As únicas alterações autorizadas no Kernel são correções de bugs críticos, patches de segurança ou otimizações de performance mensuráveis.

---

## 🎯 Distribuição de Esforço Operacional (70 / 20 / 10)

```text
       ┌─────────────────────────────────────────┐
 70%   │ Operação em Produção (PM-1 a PM-5)      │
       ├─────────────────────────────────────────┤
 20%   │ Desenvolvimento de Plugins via SDK      │
       ├─────────────────────────────────────────┤
 10%   │ Manutenção do Kernel (Bugs & Segurança) │
       └─────────────────────────────────────────┘
```
