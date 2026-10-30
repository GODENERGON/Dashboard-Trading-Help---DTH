# ADR 0001 — Registrare le decisioni architetturali

- Stato: accettato
- Data: 2026-10-30

## Contesto
Il progetto è sviluppato in gran parte da agenti AI su più sessioni. Senza una traccia scritta,
le decisioni vengono rimesse in discussione o contraddette.

## Decisione
Ogni decisione che cambia architettura, contratti, policy di rischio o fonti dati si registra
come ADR numerato in `docs/adr/` (modello: [`template.md`](template.md)). Gli ADR non si
modificano: si sostituiscono con uno nuovo che li dichiara superati.

## Conseguenze
Chi lavora sul repo, persona o agente, legge gli ADR prima di cambiare un contratto.
