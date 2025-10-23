import { create } from "zustand";

type AppState = {
  tenant: string | null;
  range: "7d" | "14d" | "30d";
  refreshSec: number;
  tick: number;
  setTenant: (t: string | null) => void;
  setRange: (r: AppState["range"]) => void;
  setRefresh: (sec: number) => void;
};

export const useAppStore = create<AppState>((set, get) => {
  // auto-refresh tick
  let timer: number | null = null;

  const setRefreshInternal = (sec: number) => {
    if (timer) {
      window.clearInterval(timer);
      timer = null;
    }
    if (sec > 0) {
      timer = window.setInterval(() => {
        set({ tick: get().tick + 1 });
      }, sec * 1000) as unknown as number;
    }
    set({ refreshSec: sec });
  };

  return {
    tenant: null,
    range: "7d",
    refreshSec: 30,
    tick: 0,
    setTenant: (t) => set({ tenant: t }),
    setRange: (r) => set({ range: r }),
    setRefresh: setRefreshInternal,
  };
});
