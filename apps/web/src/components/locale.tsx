"use client";

import { createContext, useContext, useEffect, useState, type ReactNode } from "react";
import type { Language } from "@/lib/format";

const LocaleContext = createContext<{ language: Language; tr: (pt: string, en: string) => string; toggle: () => void } | null>(null);
export function LocaleProvider({ children }: { children: ReactNode }) {
  const [language, setLanguage] = useState<Language>("pt");
  useEffect(() => { document.documentElement.lang = language === "pt" ? "pt-BR" : "en"; }, [language]);
  return <LocaleContext.Provider value={{ language, tr: (pt, en) => language === "pt" ? pt : en, toggle: () => setLanguage(value => value === "pt" ? "en" : "pt") }}>{children}</LocaleContext.Provider>;
}
export function useLocale() {
  const context = useContext(LocaleContext);
  if (!context) throw new Error("LocaleProvider is required");
  return context;
}
