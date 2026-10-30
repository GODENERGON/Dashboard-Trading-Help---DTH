"""TimesFM 2.5 adapter. Requires the ``[tsfm]`` extra; heavy imports are lazy (CLAUDE.md rule 6).

Experimental: enabled in the UI only when its walk-forward skill score vs the matching
baseline is > 0 (docs/VALIDATION.md).
"""

from __future__ import annotations

import numpy as np

from dth.forecast.base import ForecastResult

_LEVELS = (0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9)


class TimesFMForecaster:
    name = "timesfm_2p5"

    def __init__(
        self,
        checkpoint: str = "google/timesfm-2.5-200m-pytorch",
        max_context: int = 1024,
        max_horizon: int = 256,
    ) -> None:
        self._checkpoint = checkpoint
        self._max_context = max_context
        self._max_horizon = max_horizon
        self._model = None

    def _load(self):  # pragma: no cover - needs model weights
        if self._model is None:
            import timesfm

            model = timesfm.TimesFM_2p5_200M_torch.from_pretrained(self._checkpoint)
            model.compile(
                timesfm.ForecastConfig(
                    max_context=self._max_context,
                    max_horizon=self._max_horizon,
                    normalize_inputs=True,
                    use_continuous_quantile_head=True,
                )
            )
            self._model = model
        return self._model

    def forecast(self, history: np.ndarray, horizon: int) -> ForecastResult:  # pragma: no cover
        model = self._load()
        ctx = np.asarray(history, dtype=float)[-self._max_context :]
        point, quant = model.forecast(horizon=horizon, inputs=[ctx])
        # Expected quant shape: (batch, horizon, 1 + len(levels)), index 0 = mean.
        # VERIFY against the installed timesfm version before enabling (M3).
        q = np.asarray(quant)[0]
        quantiles = {lv: q[:, i + 1] for i, lv in enumerate(_LEVELS)}
        return ForecastResult(point=np.asarray(point)[0], quantiles=quantiles)
