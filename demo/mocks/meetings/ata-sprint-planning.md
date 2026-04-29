# Ata de Reunião — Sprint Planning Q2

**Data:** 18/03/2026
**Participantes:** Marcos (Tech Lead), Ana (PM), Bruno (Dev Sr.), Carla (Design), Pedro (Dev Jr.)
**Duração:** 47 minutos

---

Marcos abriu a reunião dizendo que precisamos definir as prioridades pro Q2. Ele mencionou que o sistema de notificações push tá atrasado desde o Q1 e que isso tá impactando o churn — 15% de churn nos últimos 3 meses segundo o dashboard da Ana.

Ana reforçou que o stakeholder principal (Ricardo, VP de Produto) quer ver as notificações em produção até fim de abril. "A gente precisa priorizar isso, senão perde o budget do Q3" — foram as palavras dela. Marcos concordou.

Bruno levantou uma preocupação técnica. "A arquitetura atual de mensageria não aguenta o volume que a gente tá projetando. Precisaria migrar de SQS pra Kafka, e isso leva pelo menos 2 sprints." Pedro perguntou se não dava pra fazer com SNS/SQS mesmo e escalar depois. Bruno respondeu que "até pode, mas vai dar problema em 6 meses quando a base dobrar."

Ana perguntou: "Quanto tempo leva cada opção?" Bruno estimou 2 sprints pro Kafka e 1 sprint pro SQS escalado. Decidimos ir com SQS inicialmente pra cumprir o prazo de abril, e planejar migração pro Kafka no Q3.

**Decisão: Usar SQS para MVP das notificações, migrar para Kafka no Q3.**

Carla apresentou os mockups do painel de preferências de notificação. O layout foi aprovado, mas Marcos sugeriu adicionar um toggle de "modo silencioso" que não tava nos specs originais. Carla disse que precisa de 3 dias extras pra incluir isso.

**Decisão: Incluir toggle de modo silencioso. Carla entrega mockup atualizado até sexta (21/03).**

Pedro mencionou que tá bloqueado no setup do ambiente de staging. "Faz 3 dias que abri ticket pro DevOps e não tive resposta." Marcos disse que vai escalar com o Thiago (Lead DevOps) hoje.

**Bloqueio: Ambiente de staging indisponível. Marcos vai escalar com Thiago hoje.**

Ana trouxe o tema do KPI de signup. A meta é 95% de opt-in nas notificações. Bruno achou otimista demais: "Em app mobile, 60-70% é mais realista." Ana vai revisar a meta com Ricardo.

Falamos rapidamente sobre a API de webhooks que o time do parceiro Fintech tá pedindo. Marcos disse que isso fica fora do Q2, que não dá pra abraçar tudo. Ana concordou mas pediu que a gente documentasse os endpoints já pensados pra não perder o contexto. Bruno ficou de montar um rascunho.

**Action: Bruno vai criar rascunho da API de webhooks até 28/03.**

Pedro perguntou se a gente vai continuar usando Jest ou migrar pra Vitest. "Vi uns benchmarks mostrando que Vitest é 3x mais rápido." Bruno disse que "sinceramente, tanto faz, mas se for pra mudar, faz no começo do Q2 e não no meio." Nenhuma decisão tomada — ficou como open question.

Marcos fechou a reunião com os próximos passos:
1. Carla: mockup atualizado com modo silencioso até 21/03
2. Bruno: rascunho da API de webhooks até 28/03
3. Pedro: montar estimativa de pontos pro sprint 1 até 20/03
4. Marcos: escalar staging com Thiago — hoje
5. Ana: revisar meta de opt-in com Ricardo — até 25/03

"Acho que ficou claro pessoal. Vamos com tudo pro Q2." — Marcos
