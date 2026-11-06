import type { Metadata, Viewport } from "next";
import { LocaleProvider } from "@/components/locale";
import "./globals.css";

export const metadata: Metadata = { title: { default: "Investment Research Hub", template: "%s · Investment Research Hub" }, description: "Investimentos reais, contexto compartilhado e dados verificáveis.", robots: { index: false, follow: false } };
export const viewport: Viewport = { width: "device-width", initialScale: 1, themeColor: "#080f1d" };
export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return <html lang="pt-BR"><body><LocaleProvider>{children}</LocaleProvider></body></html>;
}
