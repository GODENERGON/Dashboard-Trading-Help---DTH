"""Markdown rendering of the product ranking (docs/PRODUCTS.md)."""

from __future__ import annotations

from typing import Any

from dth.products.models import build_model_portfolios
from dth.products.scorecard import WEIGHTS


def _pct(x: float) -> str:
    return f"{x:.2f}%".replace(".", ",")


def render_products_markdown(ranking: dict[str, Any]) -> str:
    out = [
        "# Classifica prodotti per caratteristiche",
        "",
        f"Generata dal catalogo `config/products.example.yaml` (dati verificati il "
        f"{ranking['verified_on']}) con le regole dell'"
        "[ADR 0009](adr/0009-product-scorecard-and-model-portfolios.md). Rigenerare con "
        "`python -m dth.cli products-report` dopo ogni aggiornamento del catalogo.",
        "",
        "**Pesi:** " + ", ".join(f"{k} {int(v * 100)}%" for k, v in WEIGHTS.items()) + ". "
        "Punteggi da 0 a 100, calcolati dentro ogni categoria. Non è una raccomandazione "
        "d'investimento: TER e patrimoni cambiano, verificare sempre la scheda dell'emittente.",
        "",
    ]
    for cat in ranking["categories"].values():
        out += [
            f"## {cat['label']}",
            "",
            "| | Prodotto | ISIN | TER | Proventi | Punteggio | Perché |",
            "|---|---|---|---|---|---|---|",
        ]
        for p in cat["featured"] + cat["others"]:
            pr = p["product"]
            tag = "⭐ in evidenza" if p["featured"] else f"{p['rank']}°"
            why = p["reasons"]["fiscalita"].split(";")[0]
            if p["warnings"]:
                why += " · ⚠️ " + "; ".join(p["warnings"])
            income = "accumulazione" if pr["income"] == "accumulating" else "distribuzione"
            out.append(
                f"| {tag} | {pr['ticker']} — {pr['name']} | {pr['isin']} | {_pct(pr['ter_pct'])} "
                f"| {income} | {p['total']:.0f} | {why} |"
            )
        for na in cat["not_available"]:
            pr = na["product"]
            name = f"{pr['ticker']} — {pr['name']}"
            out.append(f"| 🚫 | {name} | {pr['isin']} | — | — | — | {na['reason']} |")
        out.append("")
    models = build_model_portfolios(ranking)
    out += [
        "## Portafogli modello",
        "",
        f"> {models['disclaimer']} Ribilanciamento: {models['rebalance']}.",
        "",
    ]
    for m in models["models"].values():
        lines = ", ".join(f"{int(ln['weight'] * 100)}% {ln['ticker']}" for ln in m["lines"])
        out.append(
            f"- **{m['label']}** — {m['description']} {lines}. "
            f"TER medio ponderato {_pct(m['weighted_ter_pct'])}."
        )
    return "\n".join(out) + "\n"
