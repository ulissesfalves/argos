# Fase 0 - Critérios de aprovação

## Objetivo

Construir a espinha dorsal do ARGOS com disciplina temporal, contratos de dados, materialização determinística e bloqueios explícitos contra erros de engenharia que contaminam pesquisa e backtest.

## Escopo implementado neste branch

- estrutura inicial em `src`;
- contratos temporais e canônicos tipados;
- validação explícita de ordem temporal;
- política de join com falha para calendários incompatíveis sem carry rule;
- materialização determinística de features com lineage mínimo;
- testes automáticos para os gates centrais da fase.

## Gates de aprovação

1. **Governança temporal**
   - toda série e toda feature carregam `availability_date`;
   - `publication_date < observation_date` falha;
   - `availability_date < publication_date` falha.

2. **Integridade de joins**
   - join exato entre frequências diferentes falha;
   - forward fill só é aceito quando a política estiver explícita.

3. **Reprodutibilidade**
   - mesmos inputs, mesma assinatura SHA-256;
   - materialização gera lineage mínimo auditável.

4. **Prontidão para evolução**
   - estrutura desacoplada para incorporar motores A, B, C e D;
   - ponto único simples de orquestração para a fundação.

## No-go

- qualquer feature sem `availability_date`;
- joins temporais implícitos;
- outputs não determinísticos;
- ausência de metadata de lineage.
