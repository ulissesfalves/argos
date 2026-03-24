# Fase 1 - critérios de aceitação do Motor A baseline

## Objetivo

Fechar o baseline do Motor A com critérios objetivos para decidir se a codificação evolui ou não para a próxima fase.

## Escopo aceito nesta fase

- motor point-in-time para o sleeve inicial de cobre;
- normalização robusta via ECDF expansiva com decaimento e ECDF de curto prazo;
- score contínuo em `[0, 1]`;
- tratamento explícito de sinais de alívio;
- classificação de regime com histerese;
- testes sintéticos alinhados à lógica econômica.

## Testes mínimos obrigatórios

### 1. Segurança temporal
- outlier futuro não altera score passado;
- decisão usa apenas `availability_date <= decision_date`.

### 2. Monotonicidade econômica
- queda de estoque aumenta escassez;
- aumento de backwardation aumenta escassez;
- piora em oferta aumenta escassez;
- aumento de alívio estrutural reduz score agregado.

### 3. Regime
- múltiplos sinais coerentes devem levar a `aperto_estrutural` ou `squeeze`;
- uma única observação de alívio não pode desmontar imediatamente a tese.

### 4. Auditabilidade
- snapshot precisa expor decomposição por feature;
- grupos de evidência ativos precisam ser explicitados.

## Gates de aprovação

A Fase 1 só pode ser considerada aprovada se:
- todos os testes da Fase 0 continuarem passando;
- todos os testes da Fase 1 passarem;
- não houver uso de z-score como score principal;
- o score for reprodutível para os mesmos inputs;
- houver decomposição por feature no snapshot final.

## Indicadores de avanço

### Go
- score final estável e coerente com cenários sintéticos;
- evidência multissinal emergindo nos testes de estresse;
- documentação suficiente para outro engenheiro reproduzir uso básico.

### No-go
- regime muda por ruído trivial;
- score depende da ordem incorreta das datas;
- output sem explicabilidade;
- acoplamento precoce com ingestão real antes da validação da fonte.

## Risco aberto conhecido

O baseline desta fase é útil para pesquisa e evolução arquitetural, mas ainda não equivale a um motor institucional completo. Antes da Fase 2, será necessário endurecer ainda mais a persistência de estado de regime, a calibração e a integração com dados reais validados.
