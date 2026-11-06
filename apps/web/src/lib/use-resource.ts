"use client";

import { useEffect, useState } from "react";

type State<T> = { key: string; data?: T; error?: unknown; loading: boolean };

// A key change hides the preceding result immediately, before the next effect runs.
// Cancellation plus the active flag also protects against late/uncancellable responses.
export function useResource<T>(key: string | null, load: (signal: AbortSignal) => Promise<T>) {
  const [state, setState] = useState<State<T>>({ key: "", loading: true });
  useEffect(() => {
    if (key === null) return;
    const controller = new AbortController();
    let active = true;
    load(controller.signal).then(
      data => { if (active) setState({ key, data, loading: false }); },
      error => { if (active && !controller.signal.aborted) setState({ key, error, loading: false }); },
    );
    return () => { active = false; controller.abort(); };
  }, [key, load]);
  if (key === null || state.key !== key) return { data: undefined, error: undefined, loading: true };
  return state;
}
