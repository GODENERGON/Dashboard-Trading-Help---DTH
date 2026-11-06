# ADR 0006 — Limiti di peso per crypto e startup

- Stato: accettato
- Data: 2026-11-06

## Contesto
Con l'apertura a crypto e startup (ADR 0004, temi e tab Startup) servono limiti di peso
complessivo per queste due classi, che hanno volatilità estrema (crypto) o illiquidità e rischio
di perdita totale (startup e crowdfunding).

## Decisione
Su indicazione del proprietario del progetto:
- **Crypto:** peso complessivo massimo del **10%** del patrimonio monitorato.
- **Startup e crowdfunding:** peso complessivo massimo del **15%** del patrimonio monitorato.

I limiti sono campi di `RiskLimits` (`max_crypto`, `max_startups`) e alimentano una regola di
evidenza bloccata (`allocation_limits` in `config/highlights.example.yaml`). Come gli altri
limiti, l'utente può renderli più restrittivi dalle impostazioni, non più larghi.

## Alternative considerate
Startup al 5% (proposta iniziale): scartata dal proprietario, che preferisce più spazio per i
temi di lungo periodo (nucleare, longevità, robotica…).

## Conseguenze
Con il 15% in strumenti illiquidi, il pannello Rischio deve mostrare a parte la quota **non
liquidabile a breve**, così che drawdown ed esposizione non diano un'idea falsa della liquidità
disponibile.
