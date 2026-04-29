# TODO — Principal AI Engineer Demo (Jedo / Henry)

> Roteiro oficial recebido em 2026-04-28. Ver [roteiro_jido.md](roteiro_jido.md) para o script completo.
> Prazo: enviar assim que estiver pronto → feedback de Jedo em até 1 dia útil.

---

## Decisão Crítica Primeiro

- [ ] **Definir o projeto-base da demo** — ver análise de gap abaixo.
  - O projeto precisa ter: repositório GitHub público/privado acessível, histórico de PRs criados por agente, testes automatizados, logs overnight.
  - ⚠️ FNDE é autarquia federal — verificar se pode mostrar código/PRs sem violar sigilo.
  - ⚠️ Pipeline LaTeX (livro) gera conteúdo, não código — **desqualifica automaticamente** pelo critério do Jedo.
  - ✅ Melhor opção: criar um **projeto demo dedicado** no GitHub com o pipeline SDD (Claude Code agents) gerando código real e abrindo PRs automaticamente.

---

## Alta Prioridade — Antes de Gravar

- [ ] **Criar projeto demo no GitHub** com agentes gerando código overnight.
  - Usar Claude Code (superpowers:subagent-driven-development + workflow:create-pr) como orquestrador.
  - Pipeline mínimo: issue/ticket → agente gera código → testes → PR aberto automaticamente.
  - Precisa ter pelo menos 1–2 PRs reais no histórico antes de gravar.

- [ ] **Configurar execução autônoma overnight** (cron job ou scheduled agent).
  - Opções: GitHub Actions scheduled, cron local via WSL, Claude Code /schedule.
  - O log dessa execução é o que aparece na Seção 1 do vídeo.

- [ ] **Garantir métricas visíveis** para a Seção 3.
  - Mesmo que sejam 2 semanas de dados: número de PRs abertos por agente, cobertura de testes, velocity.
  - Pode ser um dashboard simples no README ou GitHub Insights.

- [ ] **Escrever roteiro de narração em inglês** antes de qualquer gravação.
  - Adaptar as 3 falas obrigatórias do Jedo para o seu contexto real.
  - Ensaiar até ficar fluente — essa é a maior alavanca contra o gap de inglês diário.

---

## Alta Prioridade — Gravação (seguir [roteiro_jido.md](roteiro_jido.md))

- [ ] **Seção 1 (2–3 min):** Mostrar agente gerando código + logs overnight + PR no GitHub.
  - Fala obrigatória: "Este é meu sistema onde agentes geram código 24/7..."

- [ ] **Seção 2 (3–4 min):** Abrir o PR ao vivo e fazer triage linha por linha.
  - Mostrar: detecção de alucinação ou erro concreto, critério de aprovação vs. ajuste.
  - Fala obrigatória: "Agora faço triage. Olho se o agente seguiu os padrões..."

- [ ] **Seção 3 (1–2 min):** Métricas antes/depois. Posicionamento como arquiteto, não implementador.
  - Fala obrigatória: "Antes: X PRs/semana manualmente. Agora: Y PRs/semana com agentes..."

- [ ] **Verificar checklist do Jedo** antes de enviar (ver [roteiro_jido.md](roteiro_jido.md#checklist-final)).

---

## Checklist de Envio

- [ ] Agente gerando código real aparece na tela
- [ ] Code review de código gerado ao vivo (triage)
- [ ] Métricas de impacto concretas mostradas
- [ ] Frases obrigatórias mencionadas
- [ ] Demonstração prática — zero slides/teoria
- [ ] Duração entre 6–8 minutos
- [ ] **Enviar para Henry** (não diretamente para Jedo)

---

## Médio Prazo

- [ ] Clarificar com Henry: role remoto ou requer relocação?
- [ ] Clarificar com Henry: o vídeo é o gate final ou há entrevista ao vivo depois?
- [ ] Clarificar com Henry: o que Jedo define como "alinhamento cultural"?
- [ ] Documentar arquitetura WSL + Databricks (FNDE) em um README curto — útil para entrevista ao vivo.

---

## Baixa Prioridade

- [ ] Imersão diária em inglês — gap atual é prática diária, não vocabulário técnico.
- [ ] Follow up com Henry em 2 dias úteis se não vier resposta do Jedo após envio.
