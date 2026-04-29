# Roteiro Oficial — Vídeo Loom para Jedo (CTO/Founder)

> Recebido via WhatsApp de Henry em 2026-04-28.
> Duração total: **6–8 minutos**.

---

## Frase de Abertura Obrigatória

> "Há X meses nossos engenheiros não escrevem código de implementação. Vou mostrar como agentes fazem isso 24/7 enquanto dormimos e como eu faço a auditoria."

---

## Seção 1 — Agente Gerando Código Sozinho (2–3 min)

**O que gravar na tela:**
- Dashboard/terminal do sistema de agentes (AutoGPT, GPT-Pilot, Cursor Agents, pipeline custom)
- GitHub mostrando PRs criados automaticamente
- Logs de execução overnight ou background jobs

**Fala obrigatória:**
> "Este é meu sistema onde agentes geram código 24/7. Ontem à noite configurei esta tarefa [mostrar ticket/issue]. O agente gerou este código [abrir arquivo], criou testes, e abriu este PR — tudo sem minha intervenção enquanto eu dormia."

**Pontos essenciais a mencionar:**
- Que roda automaticamente (cron jobs noturnos, pipelines, filas)
- Que gera código de produção, não apenas protótipos

---

## Seção 2 — Processo de Triage (3–4 min) — MAIS IMPORTANTE

**O que gravar na tela:**
- Abrir PR real gerado pelo agente no GitHub
- Fazer code review ao vivo, linha por linha
- Mostrar testes rodando/passando
- Apontar erros ou ajustes necessários

**O que fazer ao vivo:**
- Revisar o código explicando o raciocínio
- Mostrar como detectar alucinações ou erros do agente
- Explicar critérios: o que aprova direto vs. o que precisa correção
- Demonstrar quality gates e validações

**Fala obrigatória:**
> "Agora faço triage. Olho se o agente seguiu os padrões [apontar exemplos], se os testes cobrem os casos [mostrar coverage], e se não tem alucinações. Aqui aprovo direto, aqui preciso ajustar [dar exemplo concreto]. O agente fez 80% do trabalho, eu só garanto qualidade."

---

## Seção 3 — Impacto e Transformação (1–2 min)

**O que gravar na tela:**
- Dashboard com métricas (PRs/semana, velocity, deployment frequency)
- Gráfico antes vs. depois

**Fala obrigatória:**
> "Antes: X PRs/semana manualmente. Agora: Y PRs/semana com agentes overnight. Eu e o time viramos arquitetos — definimos o que fazer, os agentes implementam. Nossos engenheiros não escrevem mais código de implementação."

---

## Checklist Final (aprovação antes de enviar)

- [ ] Agente gerando código real aparece na tela
- [ ] Code review de código gerado ao vivo
- [ ] Métricas de impacto concretas mostradas
- [ ] Frases obrigatórias mencionadas
- [ ] Demonstração prática, não teórica

---

## Desqualificação Automática — NÃO enviar se:

- Mostrar apenas Copilot/ChatGPT acelerando seu coding
- Agentes que geram conteúdo/design (não código)
- Só teoria/slides sem demonstração ao vivo
- Não mostrar processo de triage na prática
- Não mostrar código real sendo gerado pelo agente

> **Regra de ouro:** Se não mostrar agente codificando E você fazendo triage na prática = NÃO enviar o vídeo.
