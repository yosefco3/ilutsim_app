/**
 * Hook to access Telegram WebApp SDK.
 * Returns initData, user info, theme params, mainButton API, and close.
 */
import { useMemo } from "react";

export function useTelegram() {
  return useMemo(() => {
    const tg = window?.Telegram?.WebApp;

    return {
      /** Telegram initData string for API authentication */
      initData: tg?.initData || "",
      /** User info from initDataUnsafe */
      user: tg?.initDataUnsafe?.user || { id: null, first_name: "", last_name: "" },
      /** Telegram theme color params */
      themeParams: tg?.themeParams || {},
      /** Telegram MainButton API */
      mainButton: {
        show: (text) => {
          if (tg?.MainButton) {
            tg.MainButton.text = text || "Submit";
            tg.MainButton.show();
          }
        },
        hide: () => tg?.MainButton?.hide(),
        onClick: (fn) => tg?.MainButton?.onClick(fn),
        offClick: (fn) => tg?.MainButton?.offClick(fn),
      },
      /** Close the WebApp */
      close: () => tg?.close(),
      /** Raw Telegram WebApp reference */
      webApp: tg,
    };
  }, []);
}