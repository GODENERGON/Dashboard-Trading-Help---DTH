import { useState } from "react";
import { api, openExternal } from "../api";

const EMAIL = import.meta.env.VITE_FEEDBACK_EMAIL;

export function FeedbackDialog({ view, live, onClose }: { view: string; live: boolean; onClose: () => void }) {
  const [text, setText] = useState("");
  const [state, setState] = useState<"idle" | "saved" | "error">("idle");

  const save = async () => {
    try {
      await api("/feedback", { method: "POST", body: JSON.stringify({ message: text, view }) });
      setState("saved");
    } catch {
      setState("error");
    }
  };
  const mail = () => {
    const subject = encodeURIComponent(`Dabitur, feedback su ${view}`);
    const body = encodeURIComponent(text);
    void openExternal(`mailto:${EMAIL}?subject=${subject}&body=${body}`);
  };
  const copy = () => void navigator.clipboard?.writeText(text);

  return (
    <div className="overlay" role="dialog" aria-modal="true" aria-labelledby="fb-title" onKeyDown={(e) => e.key === "Escape" && onClose()}>
      <div className="dialog">
        <h2 id="fb-title">Invia feedback</h2>
        <p>Scrivi con parole tue cosa non è chiaro, cosa ti piace o cosa manca. Sezione: <strong>{view}</strong>.</p>
        <textarea
          autoFocus value={text} maxLength={5000} rows={7}
          placeholder="Per esempio: non capisco cosa vuol dire «drawdown»…"
          onChange={(e) => { setText(e.target.value); setState("idle"); }}
        />
        {state === "saved" && <p className="ok">Salvato sul tuo computer, grazie!{EMAIL ? " Se vuoi, mandalo anche per e-mail." : ""}</p>}
        {state === "error" && <p className="err">Non sono riuscito a salvarlo. Puoi copiarlo e mandarlo come preferisci.</p>}
        <div className="dialog-actions">
          <button className="btn ghost" onClick={onClose}>Chiudi</button>
          {(state === "error" || !live) && <button className="btn ghost" disabled={!text} onClick={copy}>Copia testo</button>}
          {EMAIL && <button className="btn ghost" disabled={!text} onClick={mail}>Invia per e-mail</button>}
          {live && <button className="btn" disabled={!text || state === "saved"} onClick={save}>Salva</button>}
        </div>
      </div>
    </div>
  );
}
