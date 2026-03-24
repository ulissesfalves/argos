# Fase 1 - Motor A baseline (cobre)

## Objetivo

Implementar o baseline do Motor A de forma monotona, auditavel e point-in-time safe, seguindo a especificacao do ARGOS v1.2.

## Fatos da especificacao que governam esta fase

- o sleeve inicial recomendado e cobre;
- o Motor A nao usa z-score como score principal;
- a normalizacao deve usar ECDF expansiva com decaimento mais percentil de curto prazo;
- a saida deve ser um score continuo de escassez e uma classificacao de regime com histerese;
- a transicao de regime exige regra multissinal de 3 de 5 evidencias ou persistencia;
- uma semana isolada de alivio nao deve desmontar a tese.

## Escopo desta implementacao

Esta fase implementa apenas o baseline do Motor A, sem ainda conectar fontes reais de mercado.

Entram nesta fase:
- contratos do Motor A;
- normalizacao robusta por ECDF com decaimento e janela curta;
- score monotono configuravel;
- classificador de regime com histerese;
- engine point-in-time para uma commodity;
- testes unitarios e cenarios sinteticos economicamente coerentes.

Nao entram nesta fase:
- ingestao real de LME/COMEX/SHFE;
- calibracao supervisionada de pesos;
- dashboards;
- integracao com Motor B, C ou D.

## Plano de implementacao

### Etapa 1 - Contratos e configuracao
Criar enums, contratos e configuracoes do Motor A.

**Critérios de aprovação**
- cada feature precisa declarar direcao economica;
- cada feature precisa declarar peso, grupo e frequencia;
- alivio estrutural precisa ter tratamento explicito e separado.

### Etapa 2 - Normalizacao robusta
Implementar ECDF expansiva com decaimento e ECDF de curto prazo.

**Critérios de aprovação**
- scores limitados a [0,1];
- funcoes usam apenas historico ate t;
- direcoes economicas invertidas funcionam corretamente para estoque.

### Etapa 3 - Score baseline
Combinar features normalizadas em um score continuo, monotono e auditavel.

**Critérios de aprovação**
- aumento de feature escassez positiva eleva score;
- aumento de feature de alivio reduz score;
- a decomposicao por feature precisa ser rastreavel.

### Etapa 4 - Regime com histerese
Transformar score em estados operacionais.

**Critérios de aprovação**
- classificar folga, aperto ciclico, aperto estrutural e squeeze;
- exigir confirmacao multissinal;
- nao desmontar tese por alivio isolado.

### Etapa 5 - Testes economicos e gates
Validar comportamento com cenarios sinteticos alinhados a fatos economicos.

**Critérios de aprovação**
- estoques caindo + backwardation subindo + oferta piorando precisam elevar regime;
- um outlier futuro nao pode alterar score passado;
- alivio estrutural precisa reduzir score agregado.

## Indicadores de go/no-go

### Go
- 100% dos testes do Motor A passando;
- 0 uso de z-score no baseline;
- 0 dependencia de dados futuros nos testes point-in-time;
- regime estrutural ou squeeze emergindo em cenarios sinteticos coerentes.

### No-go
- score sem decomposicao por feature;
- classificador instavel a ruido trivial;
- necessidade de dados futuros para gerar score corrente;
- regra de regime sem evidencias multissinal.

## Estratégia de dados

Nesta fase, o codigo sera preparado para receber dados canonicos ja alinhados temporalmente. Nenhuma fonte externa sera hardcoded antes da validacao de disponibilidade, lag real e qualidade. Isso evita engenharia baseada em suposicao.
