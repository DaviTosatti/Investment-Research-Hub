"use client";

import { api } from "@/lib/api";
import { decimal, decimalPattern, text } from "@/lib/forms";
import { today } from "@/lib/format";
import { useHub } from "./hub-shell";
import { useLocale } from "./locale";
import { Field, Panel, Submit, useMutation } from "./ui";

export function ManualPriceForm() {
  const { references, referencesLoading, canWrite, refresh } = useHub();
  const { tr } = useLocale();
  const mutation = useMutation();
  return <Panel title={tr("Avaliação manual", "Manual valuation")} subtitle={tr("Uma referência de preço com origem e data", "A price reference with a source and date")}><form className="panel-form" onSubmit={event => mutation.run(event, async form => { const data = new FormData(form); await api("/prices", { method: "POST", body: JSON.stringify({ instrument_id: text(data, "instrument_id"), price: decimal(data, "price"), as_of: text(data, "as_of"), source: text(data, "source") }) }); form.reset(); refresh(); }, tr("Avaliação registrada. O painel usará a referência aplicável à data selecionada.", "Valuation recorded. The dashboard will use the reference applicable to the selected date."))}><fieldset disabled={!canWrite || mutation.busy || referencesLoading || !references?.instruments.length}><Field label={tr("Ativo", "Instrument")}><select name="instrument_id" defaultValue="" required><option value="" disabled>{tr("Selecione o ativo", "Select an instrument")}</option>{references?.instruments.map(instrument => <option key={instrument.id} value={instrument.id}>{instrument.ticker} · {instrument.name}</option>)}</select></Field><div className="form-row"><Field label={tr("Preço (BRL)", "Price (BRL)")}><input name="price" inputMode="decimal" pattern={decimalPattern} required autoComplete="off" /></Field><Field label={tr("Data da avaliação", "Valuation date")}><input name="as_of" type="date" max={today()} required defaultValue={today()} /></Field></div><Field label={tr("Fonte da avaliação", "Valuation source")} hint={tr("Descreva a procedência para permitir a conferência pelo grupo.", "Describe the source so the group can verify it.")}><input name="source" required maxLength={200} /></Field>{mutation.feedback}<Submit busy={mutation.busy}>{tr("Registrar avaliação", "Record valuation")}</Submit></fieldset>{!referencesLoading && !references?.instruments.length && <p className="muted small">{tr("Cadastre um ativo para adicionar uma avaliação.", "Create an instrument to add a valuation.")}</p>}</form></Panel>;
}
