"use client";

import { useCallback, useState } from "react";
import { api } from "@/lib/api";
import { text } from "@/lib/forms";
import type { PageResult, User } from "@/lib/types";
import { useResource } from "@/lib/use-resource";
import { useHub } from "@/components/hub-shell";
import { useLocale } from "@/components/locale";
import { EmptyState, ErrorState, Field, LoadingState, Notice, PageHeading, Pagination, Panel, Submit, useMutation } from "@/components/ui";

export default function AdminPage() {
  const { user } = useHub();
  const { tr } = useLocale();
  if (user.role !== "admin") return <><PageHeading eyebrow={tr("ADMINISTRAÇÃO", "ADMINISTRATION")} title={tr("Acesso administrativo", "Administrative access")} description={tr("A gestão das contas de acesso é reservada aos administradores.", "Login account management is restricted to administrators.")} /><Notice>{tr("Você pode continuar consultando os dados compartilhados nas demais áreas. Para criar uma conta de acesso, fale com um administrador do grupo.", "You can continue viewing shared data in other areas. Contact a group administrator to create a login account.")}</Notice></>;
  return <AdminContent />;
}

function AdminContent() {
  const { user, revision, refresh } = useHub();
  const { tr } = useLocale();
  const mutation = useMutation();
  const [offset, setOffset] = useState(0);
  const load = useCallback((signal: AbortSignal) => api<PageResult<User>>(`/members?limit=25&offset=${offset}`, { signal }), [offset]);
  const members = useResource(`members:${offset}:${revision}`, load);
  const role = (value: string) => value === "admin" ? tr("Administrador", "Administrator") : value === "viewer" ? tr("Leitor", "Viewer") : tr("Membro", "Member");
  return <><PageHeading eyebrow={tr("ADMINISTRAÇÃO / ACESSO", "ADMINISTRATION / ACCESS")} title={tr("Um grupo de confiança.", "A trusted group.")} description={tr("Contas individuais para compartilhar a visão do grupo e preservar a autoria de cada registro.", "Individual accounts to share the group’s perspective and preserve authorship of every record.")} />
    <div className="forms-grid"><Panel title={tr("Adicionar participante", "Add a participant")} subtitle={tr("Cria uma conta de acesso, não um titular econômico", "Creates a login account, not an economic owner")}><form className="panel-form" onSubmit={event => mutation.run(event, async form => { const data = new FormData(form); await api("/members", { method: "POST", body: JSON.stringify({ name: text(data, "name"), email: text(data, "email"), password: String(data.get("password") ?? ""), role: text(data, "role") }) }); form.reset(); refresh(); }, tr("Conta criada. Compartilhe o acesso com o participante por um canal adequado.", "Account created. Share access with the participant through an appropriate channel."))}><fieldset disabled={mutation.busy}><Field label={tr("Nome", "Name")}><input name="name" required maxLength={100} autoComplete="off" /></Field><Field label={tr("E-mail", "Email")}><input name="email" required type="email" maxLength={254} autoComplete="off" /></Field><Field label={tr("Senha inicial", "Initial password")} hint={tr("Use de 12 a 128 caracteres.", "Use between 12 and 128 characters.")}><input name="password" type="password" required minLength={12} maxLength={128} autoComplete="new-password" /></Field><Field label={tr("Permissão", "Role")}><select name="role" defaultValue="member"><option value="member">{role("member")}</option><option value="viewer">{role("viewer")}</option><option value="admin">{role("admin")}</option></select></Field>{mutation.feedback}<Submit busy={mutation.busy}>{tr("Criar conta de acesso", "Create login account")}</Submit></fieldset></form></Panel><Panel title={tr("Permissões do grupo", "Group permissions")} subtitle={tr("Dados compartilhados, autoria individual", "Shared data, individual authorship")}><div className="permission-list"><div><span className="badge valid">{role("admin")}</span><p>{tr("Consulta os dados, registra eventos e gerencia as contas de acesso do grupo.", "Views data, records events and manages group login accounts.")}</p></div><div><span className="badge neutral">{role("member")}</span><p>{tr("Consulta dados de todo o grupo e registra titulares, carteiras, ativos, operações e avaliações.", "Views all group data and records owners, portfolios, instruments, transactions and valuations.")}</p></div><div><span className="badge neutral">{role("viewer")}</span><p>{tr("Consulta as carteiras, operações, avaliações e auditoria do grupo, sem registrar alterações.", "Views group portfolios, transactions, valuations and audit records without making changes.")}</p></div></div><div className="panel-bottom-note">{tr("Cada registro mantém seu autor. As contas de acesso e a titularidade econômica são cadastros distintos.", "Every record preserves its author. Login accounts and economic ownership are separate records.")}</div></Panel></div>
    <Panel title={tr("Participantes autorizados", "Authorized participants")} subtitle={tr("Acesso individual ao workspace privado", "Individual access to the private workspace")}>
      {members.loading ? <LoadingState /> : members.error !== undefined ? <ErrorState error={members.error} retry={refresh} /> : members.data && <>{members.data.items.length === 0 ? <EmptyState icon="shield" title={tr("Nenhum participante retornado", "No participants returned")} description={tr("Atualize para consultar as contas do grupo.", "Refresh to query group accounts.")} /> : <div className="table-scroll"><table className="responsive-table"><caption className="sr-only">{tr("Contas de acesso do grupo", "Group login accounts")}</caption><thead><tr><th>{tr("Participante", "Participant")}</th><th>{tr("E-mail", "Email")}</th><th>{tr("Permissão", "Role")}</th></tr></thead><tbody>{members.data.items.map(member => <tr key={member.id}><td data-label={tr("Participante", "Participant")}><strong>{member.name}</strong>{member.id === user.id && <span className="cell-secondary">{tr("Sua conta", "Your account")}</span>}</td><td data-label={tr("E-mail", "Email")}>{member.email}</td><td data-label={tr("Permissão", "Role")}><span className={`badge ${member.role === "admin" ? "valid" : "neutral"}`}>{role(member.role)}</span></td></tr>)}</tbody></table></div>}<Pagination total={members.data.total} offset={offset} limit={25} change={setOffset} /></>}
    </Panel>
  </>;
}
