# Motor A baseline - guia de uso

## Objetivo

O Motor A baseline transforma sinais canonicos de escassez em:
- um `score` continuo entre 0 e 1;
- um `regime` operacional (`folga`, `aperto_ciclico`, `aperto_estrutural`, `squeeze`);
- uma decomposicao auditavel por feature.

## O que entra no baseline

O baseline desta fase foi desenhado para o sleeve inicial de cobre e espera series canonicas ja point-in-time safe.

Cada feature precisa declarar:
- `name`
- `source_metric`
- `weight`
- `direction`
- `frequency`
- `group`
- `reliability_weight`
- `is_relief`
- `evidence_threshold`
- `min_history`

## Como o score e construido

1. o motor filtra apenas pontos com `availability_date <= decision_date`;
2. cada serie e normalizada com:
   - ECDF expansiva com decaimento;
   - ECDF de curto prazo;
3. o score blended e calculado como:

`blended = alpha * long_score + (1 - alpha) * short_score`

4. features de alivio entram com peso assinado negativo;
5. o score agregado e truncado em `[0, 1]`.

## Exemplo minimo

```python
from datetime import date

from argos.contracts.series import CanonicalPoint
from argos.contracts.temporal import TemporalMetadata
from argos.core.types import CalendarFrequency
from argos.motors.motor_a.engine import MotorAEngine
from argos.motors.motor_a.models import MotorAConfig, MotorAFeatureSpec, ScarcityDirection

engine = MotorAEngine(MotorAConfig())

specs = {
    "inventory": MotorAFeatureSpec(
        name="inventory",
        source_metric="inventory",
        weight=0.30,
        direction=ScarcityDirection.LOWER_IS_SCARCER,
        frequency=CalendarFrequency.WEEKLY,
        group="inventory",
    ),
    "term": MotorAFeatureSpec(
        name="term",
        source_metric="spread_0_3m",
        weight=0.25,
        direction=ScarcityDirection.HIGHER_IS_SCARCER,
        frequency=CalendarFrequency.WEEKLY,
        group="term",
    ),
}

series = {
    "inventory": [
        CanonicalPoint(
            entity_id="copper",
            metric="inventory",
            value=80.0,
            unit="tons",
            currency=None,
            frequency=CalendarFrequency.WEEKLY,
            temporal=TemporalMetadata(
                observation_date=date(2025, 1, 3),
                publication_date=date(2025, 1, 3),
                availability_date=date(2025, 1, 3),
                effective_date=date(2025, 1, 3),
            ),
        ),
    ],
    "term": [
        CanonicalPoint(
            entity_id="copper",
            metric="spread_0_3m",
            value=4.0,
            unit="usd_per_ton",
            currency="USD",
            frequency=CalendarFrequency.WEEKLY,
            temporal=TemporalMetadata(
                observation_date=date(2025, 1, 3),
                publication_date=date(2025, 1, 3),
                availability_date=date(2025, 1, 3),
                effective_date=date(2025, 1, 3),
            ),
        ),
    ],
}

snapshot = engine.compute_snapshot(
    commodity="copper",
    decision_date=date(2025, 1, 3),
    feature_specs=specs,
    feature_series=series,
)

print(snapshot.score)
print(snapshot.regime)
print(snapshot.active_evidence_groups)
```

## Gates de uso

Antes de usar o Motor A em pesquisa ou backtest, confirme:
- todos os pontos possuem `availability_date`;
- nenhuma feature depende de dado futuro;
- a direcao economica esta correta;
- o grupo da feature esta correto;
- alivio estrutural nao esta misturado com sinal de aperto.

## Limites desta fase

- ainda nao ha ingestao real de LME/COMEX/SHFE;
- o baseline nao esta calibrado com dados reais;
- histerese e persistencia estao implementadas para baseline, nao para producao institucional;
- nao existe ainda integração com Motor B, C ou D.
