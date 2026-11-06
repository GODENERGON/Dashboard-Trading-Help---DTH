import { useState } from "react";

const STEPS = [
  {
    title: "Benvenuto in Dabitur",
    body: [
      "Dabitur raccoglie in un solo posto prezzi, prodotti e rischi per aiutarti a capire i mercati.",
      "È uno strumento di informazione: non compra né vende nulla e non è consulenza finanziaria.",
    ],
  },
  {
    title: "Come si legge",
    body: [
      "La banda in alto mostra, settimana per settimana, il clima dei mercati dal 2005 a oggi.",
      "Di norma l'app è grigia come il metallo. Si scalda solo quando una regola trova qualcosa da guardare: ambra per l'attenzione, rosso per le situazioni critiche.",
      "Accanto a ogni avviso c'è «Perché?»: spiega quale regola è scattata e su quali dati.",
    ],
  },
  {
    title: "Il tuo parere conta",
    body: [
      "I prezzi si aggiornano da soli quando sei connesso a internet. Al primo avvio vedi quelli inclusi nell'app.",
      "Questa è una versione di prova: il pulsante «Invia feedback» in basso a sinistra serve a dirci cosa non è chiaro o cosa manca. Ogni commento aiuta.",
    ],
  },
];

export function Onboarding({ onDone }: { onDone: () => void }) {
  const [i, setI] = useState(0);
  const step = STEPS[i];
  const last = i === STEPS.length - 1;
  return (
    <div className="overlay" role="dialog" aria-modal="true" aria-labelledby="ob-title">
      <div className="dialog">
        <p className="step-count">Passo {i + 1} di {STEPS.length}</p>
        <h2 id="ob-title">{step.title}</h2>
        {step.body.map((p) => <p key={p}>{p}</p>)}
        <div className="dialog-actions">
          {i > 0 && <button className="btn ghost" onClick={() => setI(i - 1)}>Indietro</button>}
          <button className="btn" autoFocus onClick={() => (last ? onDone() : setI(i + 1))}>
            {last ? "Inizia" : "Avanti"}
          </button>
        </div>
      </div>
    </div>
  );
}
