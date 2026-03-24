"""Minimal orchestration entrypoint for Phase 0."""

from __future__ import annotations

from dataclasses import dataclass

from argos.feature_store.materializer import FeatureMaterializer, MaterializedFeatureSet


@dataclass
class Phase0Pipeline:
    """Tiny pipeline wrapper to centralize phase 0 orchestration."""

    materializer: FeatureMaterializer

    def run_identity_feature(self, *args, **kwargs) -> MaterializedFeatureSet:
        return self.materializer.materialize_mean_feature(*args, **kwargs)
