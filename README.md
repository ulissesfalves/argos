# ARGOS

Sistema de inteligência de escassez estrutural e alocação de capital.

## Estado atual

Este branch inicia a **Fase 0** do ARGOS: fundação de engenharia, governança temporal, contratos de dados e materialização determinística de features.

## Objetivos da Fase 0

- impor disciplina temporal com `observation_date`, `publication_date`, `availability_date` e `effective_date`;
- criar contratos de dados auditáveis e tipados;
- bloquear joins entre calendários incompatíveis sem regra explícita de carry;
- materializar features de forma determinística e reproduzível;
- deixar a arquitetura pronta para acoplar os motores A, B, C e D sem retrabalho destrutivo.

## Estrutura inicial

```text
argos/
  config/
  docs/
  src/argos/
    canonical/
    contracts/
    core/
    feature_store/
    orchestration/
  tests/
```

## Rodando localmente

```bash
python -m pip install -e .[dev]
pytest
```

## Critérios mínimos da Fase 0

- nenhuma feature principal pode ser materializada sem `availability_date`;
- joins incompatíveis sem regra de carry devem falhar explicitamente;
- o mesmo input deve gerar a mesma assinatura determinística;
- toda materialização deve gerar metadados de lineage.
