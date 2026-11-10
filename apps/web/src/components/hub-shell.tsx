"use client";

import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import { createContext, useCallback, useContext, useEffect, useRef, useState, type ReactNode } from "react";
import { allPages, api, ApiError, filterQuery } from "@/lib/api";
import { today } from "@/lib/format";
import { useResource } from "@/lib/use-resource";
import type { Dashboard, Filters, Instrument, Owner, Portfolio, User } from "@/lib/types";
import { useLocale } from "./locale";
import { Brand, ErrorState, Icon, LoadingState, type IconName } from "./ui";

const routes: { path: string; pt: string; en: string; icon: IconName }[] = [
  { path: "/inicio", pt: "Visão geral", en: "Overview", icon: "home" },
  { path: "/carteiras", pt: "Carteiras", en: "Portfolios", icon: "wallet" },
  { path: "/operacoes", pt: "Operações", en: "Transactions", icon: "arrows" },
  { path: "/dados", pt: "Dados e auditoria", en: "Data & audit", icon: "database" },
  { path: "/administracao", pt: "Administração", en: "Administration", icon: "settings" },
];
type ReferenceData = { owners: Owner[]; portfolios: Portfolio[]; instruments: Instrument[] };
type HubContextValue = {
  user: User; filters: Filters; setFilters: (filters: Filters) => void;
  references?: ReferenceData; referencesLoading: boolean; referencesError?: unknown;
  dashboard?: Dashboard; dashboardLoading: boolean; dashboardError?: unknown;
  revision: number; refresh: () => void; canWrite: boolean;
};
const HubContext = createContext<HubContextValue | null>(null);
export function useHub() {
  const context = useContext(HubContext);
  if (!context) throw new Error("HubShell is required");
  return context;
}
export function HubShell({ children }: { children: ReactNode }) {
  const { language, tr, toggle } = useLocale();
  const router = useRouter();
  const pathname = usePathname();
  const [revision, setRevision] = useState(0);
  const [collapsed, setCollapsed] = useState(false);
  const [filters, setFilters] = useState<Filters>({ owner_id: "", portfolio_id: "", as_of: today() });
  const [logoutError, setLogoutError] = useState<unknown>();
  const [loggingOut, setLoggingOut] = useState(false);
  const drawer = useRef<HTMLDialogElement>(null);
  const loadSession = useCallback((signal: AbortSignal) => api<{ user: User }>("/auth/session", { signal }), []);
  const session = useResource("session", loadSession);
  const user = session.data?.user;
  const loadReferences = useCallback(async (signal: AbortSignal) => {
    const [owners, portfolios, instruments] = await Promise.all([
      allPages<Owner>("/owners", signal), allPages<Portfolio>("/portfolios", signal), allPages<Instrument>("/instruments", signal),
    ]);
    return { owners, portfolios, instruments };
  }, []);
  const references = useResource(user ? `references:${revision}` : null, loadReferences);
  const query = filterQuery(filters);
  const loadDashboard = useCallback((signal: AbortSignal) => api<Dashboard>(`/dashboard?${query}`, { signal }), [query]);
  const dashboard = useResource(user ? `dashboard:${query}:${revision}` : null, loadDashboard);
  const refresh = useCallback(() => setRevision(value => value + 1), []);

  useEffect(() => {
    const expired = () => router.replace("/login");
    window.addEventListener("hub:session-expired", expired);
    return () => window.removeEventListener("hub:session-expired", expired);
  }, [router]);
  useEffect(() => { if (session.error instanceof ApiError && session.error.status === 401) router.replace("/login"); }, [session.error, router]);
  async function logout() {
    setLoggingOut(true); setLogoutError(undefined);
    try { await api<void>("/auth/logout", { method: "POST" }); router.replace("/login"); router.refresh(); }
    catch (error) { setLogoutError(error); setLoggingOut(false); }
  }
  const navigation = (mobile = false) => <nav className="navigation" aria-label={tr("Navegação principal", "Main navigation")}>
    {[{ pt: "ACOMPANHAMENTO", en: "MONITORING", items: routes.slice(0, 3) }, { pt: "GESTÃO", en: "MANAGEMENT", items: routes.slice(3) }].map(group => <div className="nav-group" key={group.en} role="group" aria-label={tr(group.pt, group.en)}><p className="nav-label">{tr(group.pt, group.en)}</p>
      {group.items.map(route => <Link key={route.path} href={route.path} className={`nav-link ${pathname === route.path ? "active" : ""}`} aria-label={tr(route.pt, route.en)} aria-current={pathname === route.path ? "page" : undefined} title={collapsed && !mobile ? tr(route.pt, route.en) : undefined} onClick={() => { if (mobile) drawer.current?.close(); }}><Icon name={route.icon} /><span>{tr(route.pt, route.en)}</span>{pathname === route.path && <span className="nav-active-dot" />}</Link>)}
    </div>)}
  </nav>;
  if (session.loading || (session.error instanceof ApiError && session.error.status === 401)) return <div className="fullscreen-state"><Brand /><LoadingState /></div>;
  if (!user) return <div className="fullscreen-state"><Brand /><ErrorState error={session.error} retry={() => window.location.reload()} /><Link className="text-link" href="/login">{tr("Voltar ao acesso", "Return to sign in")}</Link></div>;
  return <HubContext.Provider value={{ user, filters, setFilters, references: references.data, referencesLoading: references.loading, referencesError: references.error, dashboard: dashboard.data, dashboardLoading: dashboard.loading, dashboardError: dashboard.error, revision, refresh, canWrite: user.role !== "viewer" }}>
    <a href="#main-content" className="skip-link">{tr("Pular para o conteúdo", "Skip to content")}</a>
    <div className={`app-shell ${collapsed ? "sidebar-collapsed" : ""}`}>
      <aside className="sidebar"><Link className="brand-link" href="/inicio" aria-label="Investment Research Hub"><Brand compact={collapsed} /></Link>{navigation()}<div className="sidebar-bottom"><div className="workspace-note"><span className="badge">{tr("GRUPO PRIVADO", "PRIVATE GROUP")}</span><p>{tr("Um grupo. Múltiplas perspectivas.", "One group. Multiple perspectives.")}</p></div><button className="collapse-button" onClick={() => setCollapsed(value => !value)} aria-label={collapsed ? tr("Expandir menu", "Expand menu") : tr("Recolher menu", "Collapse menu")} aria-expanded={!collapsed}><Icon name="chevron" /><span>{tr("Recolher menu", "Collapse menu")}</span></button></div></aside>
      <div className="app-body"><header className="topbar"><div className="topbar-start"><button className="icon-button mobile-menu" aria-label={tr("Abrir menu", "Open menu")} onClick={() => drawer.current?.showModal()}><Icon name="menu" /></button><span className="breadcrumb">Workspace <span>/</span> <strong>{tr(routes.find(route => route.path === pathname)?.pt ?? "Visão geral", routes.find(route => route.path === pathname)?.en ?? "Overview")}</strong></span></div><div className="topbar-actions"><span className="group-tag"><Icon name="shield" size={14} />{tr("Grupo privado", "Private group")}</span><button className="language-button" onClick={toggle} aria-label={tr("Switch to English", "Mudar para português")}>{language === "pt" ? "EN" : "PT"}</button><span className="topbar-divider" /><span className="avatar" aria-hidden="true">{user.name.slice(0, 1).toUpperCase()}</span><span className="user-name">{user.name}<small>{user.role === "admin" ? tr("Administrador", "Administrator") : user.role === "viewer" ? tr("Leitor", "Viewer") : tr("Membro", "Member")}</small></span><button className="icon-button" onClick={logout} disabled={loggingOut} aria-label={tr("Sair da conta", "Sign out")}><Icon name="logout" /></button></div></header>
        <main id="main-content" tabIndex={-1} className="main-content">
          {logoutError !== undefined && <ErrorState error={logoutError} retry={logout} />}
          <div className="filter-bar"><div className="filter-context"><span className="context-dot" /><span>{tr("Contexto compartilhado", "Shared context")}</span></div><label className="filter-field"><span>{tr("Titular", "Owner")}</span><select value={filters.owner_id} disabled={references.loading || !references.data} onChange={event => setFilters({ ...filters, owner_id: event.target.value, portfolio_id: "" })}><option value="">{tr("Todos os titulares", "All owners")}</option>{references.data?.owners.map(owner => <option key={owner.id} value={owner.id}>{owner.name}</option>)}</select></label><label className="filter-field"><span>{tr("Carteira", "Portfolio")}</span><select value={filters.portfolio_id} disabled={references.loading || !references.data} onChange={event => setFilters({ ...filters, portfolio_id: event.target.value })}><option value="">{tr("Consolidado do grupo", "Group overview")}</option>{references.data?.portfolios.filter(portfolio => !filters.owner_id || portfolio.owner_id === filters.owner_id).map(portfolio => <option key={portfolio.id} value={portfolio.id}>{portfolio.name} · {portfolio.owner_name}</option>)}</select></label><label className="filter-field date-filter"><span>{tr("Data de referência", "Reference date")}</span><input type="date" value={filters.as_of} max={today()} required onChange={event => { if (event.target.value && event.target.validity.valid) setFilters({ ...filters, as_of: event.target.value }); }} /></label><span className="currency-label">BRL</span><button className="icon-button refresh-button" onClick={refresh} aria-label={tr("Atualizar dados", "Refresh data")}><Icon name="refresh" /></button></div>
          {references.error !== undefined && <ErrorState error={references.error} retry={refresh} />}
          {children}
          <footer className="app-footer"><span>Investment Research Hub</span><span>{tr("Investimentos reais", "Real investments")}<span className="footer-dot">·</span>{tr("Titularidade individual preservada", "Individual ownership preserved")}</span></footer>
        </main>
      </div>
    </div>
    <dialog className="mobile-drawer" ref={drawer} aria-labelledby="drawer-title" onClick={event => { if (event.target === event.currentTarget) drawer.current?.close(); }}><div className="drawer-inner"><div className="drawer-heading"><span id="drawer-title"><Brand /></span><button className="icon-button" aria-label={tr("Fechar menu", "Close menu")} onClick={() => drawer.current?.close()}><Icon name="close" /></button></div>{navigation(true)}<p className="drawer-footnote">{tr("Grupo privado · Dados compartilhados", "Private group · Shared data")}</p></div></dialog>
  </HubContext.Provider>;
}
