"""Educational, non-personalised model portfolios (ADR 0009).

Simple, low-turnover allocations rebalanced once a year, built with the best-ranked product
of each category. The study of 2026-11-06 found that low turnover beats every trend variant
tested once Italian taxes are applied.
"""

from __future__ import annotations

from typing import Any

DISCLAIMER = (
    "Esempio educativo, non personalizzato: non tiene conto della tua situazione, dei tuoi "
    "obiettivi né della tua tolleranza al rischio. Non è una raccomandazione d'investimento."
)

MODEL_PORTFOLIOS: dict[str, dict[str, Any]] = {
    "prudente": {
        "label": "Prudente",
        "description": "Più titoli di Stato che azioni: oscillazioni contenute, crescita lenta.",
        "weights": {"equity_world": 0.25, "govt_bonds_eur": 0.55, "gold": 0.10, "cash_eur": 0.10},
    },
    "bilanciato": {
        "label": "Bilanciato",
        "description": "Il classico 60/40 con un po' di oro: il riferimento degli studi.",
        "weights": {"equity_world": 0.55, "govt_bonds_eur": 0.35, "gold": 0.10},
    },
    "dinamico": {
        "label": "Dinamico",
        "description": "Prevalenza azionaria: più crescita attesa, cali anche del 30-50%.",
        "weights": {"equity_world": 0.70, "equity_em": 0.10, "govt_bonds_eur": 0.10, "gold": 0.10},
    },
}


def build_model_portfolios(ranking: dict[str, Any]) -> dict[str, Any]:
    """Fill each model with the top product of every category it uses."""
    cats = ranking["categories"]

    def best(cat: str) -> dict[str, Any] | None:
        pool = cats[cat]["featured"] or cats[cat]["others"]
        return pool[0]["product"] if pool else None

    out: dict[str, Any] = {"disclaimer": DISCLAIMER, "rebalance": "una volta l'anno", "models": {}}
    for key, model in MODEL_PORTFOLIOS.items():
        lines = []
        for cat, weight in model["weights"].items():
            prod = best(cat)
            lines.append(
                {
                    "category": cat,
                    "category_label": cats[cat]["label"],
                    "weight": weight,
                    "ticker": prod["ticker"] if prod else None,
                    "isin": prod["isin"] if prod else None,
                    "name": prod["name"] if prod else None,
                    "ter_pct": prod["ter_pct"] if prod else None,
                }
            )
        ter = sum(line["weight"] * (line["ter_pct"] or 0) for line in lines)
        out["models"][key] = {
            "label": model["label"],
            "description": model["description"],
            "lines": lines,
            "weighted_ter_pct": round(ter, 3),
        }
    return out
