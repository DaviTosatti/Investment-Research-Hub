"use client";
import { ErrorState } from "@/components/ui";
export default function ErrorPage({ error, reset }: { error: Error; reset: () => void }) { return <main className="fullscreen-state"><ErrorState error={error} retry={reset} /></main>; }
