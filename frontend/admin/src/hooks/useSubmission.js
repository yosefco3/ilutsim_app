/**
 * Hook to load, edit, and submit a weekly constraints form.
 * Manages all state: loading, week data, form, events, errors.
 */
import { useState, useEffect, useCallback } from "react";
import { get, post, getCurrentWeek } from "../api/guardApiClient.js";

/**
 * @param {string} initData - Telegram initData for auth
 */
export function useSubmission(initData) {
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(null);
  const [week, setWeek] = useState(null);
  const [days, setDays] = useState([]);
  const [events, setEvents] = useState([]);
  const [notes, setNotes] = useState("");

  // ── Dev mode flag ──────────────────────────────────────────────
  const isDevMode = initData === "__DEV_MODE__";

  // ── Load current week + existing submission ──────────────────
  useEffect(() => {
    if (!initData) return;

    let cancelled = false;

    async function load() {
      setLoading(true);
      setError(null);

      // 1) Get current week + week meta (label, status) in parallel
      const [subResult, weekMetaResult] = await Promise.all([
        get("/submissions/current-week", initData),
        getCurrentWeek(initData),
      ]);

      if (subResult.error) {
        if (isDevMode) {
          setError("No open week found. Open a week from the admin dashboard first, then refresh this page.");
        } else {
          setError(subResult.error);
        }
        setLoading(false);
        return;
      }

      if (cancelled) return;

      const weekMeta = weekMetaResult.data; // { week_label, status, ... } or null
      const weekData = subResult.data;

      // Merge week meta (label, status) into the week object
      setWeek({
        ...weekData,
        week_label: weekMeta?.week_label || weekData?.week_label || null,
        status: weekMeta?.status || weekData?.status || null,
      });

      // 2) Get existing submission (may be null / endpoint may not exist in dev)
      const { data: subData } = await get(
        `/submissions/my?week_id=${weekData.week_id}`,
        initData,
      );

      if (cancelled) return;

      // Build initial form state
      const initialDays = (weekData.days || []).map((d) => {
        const existing = subData?.days?.find((s) => s.day_index === d.day_index);
        return {
          day_index: d.day_index,
          available: existing?.available ?? true,
          shift_type: existing?.shift_type ?? null,
          from_hour: existing?.from_hour ?? "",
          to_hour: existing?.to_hour ?? "",
          blocked: d.blocked || false,
        };
      });

      setDays(initialDays);
      setEvents(subData?.events || []);
      setNotes(subData?.notes || "");
      setLoading(false);
    }

    load();
    return () => {
      cancelled = true;
    };
  }, [initData]);

  // ── Toggle day availability ──────────────────────────────────
  const toggleAvailable = useCallback((dayIndex) => {
    setDays((prev) =>
      prev.map((d) =>
        d.day_index === dayIndex ? { ...d, available: !d.available } : d,
      ),
    );
  }, []);

  // ── Set shift type for a day ─────────────────────────────────
  const setShiftType = useCallback((dayIndex, shiftType) => {
    setDays((prev) =>
      prev.map((d) =>
        d.day_index === dayIndex ? { ...d, shift_type: shiftType } : d,
      ),
    );
  }, []);

  // ── Set custom hours for a day ───────────────────────────────
  const setHours = useCallback((dayIndex, from, to) => {
    setDays((prev) =>
      prev.map((d) =>
        d.day_index === dayIndex ? { ...d, from_hour: from, to_hour: to } : d,
      ),
    );
  }, []);

  // ── Toggle an event on a day ─────────────────────────────────
  const toggleEvent = useCallback((dayIndex, eventType) => {
    setEvents((prev) => {
      const idx = prev.findIndex(
        (e) => e.day_index === dayIndex && e.event_type === eventType,
      );
      if (idx >= 0) {
        return prev.filter((_, i) => i !== idx);
      }
      return [...prev, { day_index: dayIndex, event_type: eventType }];
    });
  }, []);

  // ── Submit the form ──────────────────────────────────────────
  const submit = useCallback(async () => {
    if (!week) return;

    setError(null);
    setSuccess(null);

    const payload = {
      week_id: week.week_id,
      days: days
        .filter((d) => !d.blocked)
        .map((d) => ({
          day_index: d.day_index,
          available: d.available,
          shift_type: d.shift_type,
          from_hour: d.from_hour || null,
          to_hour: d.to_hour || null,
        })),
      events: events.map((e) => ({
        day_index: e.day_index,
        event_type: e.event_type,
      })),
      notes,
    };

    const { error: submitErr } = await post(
      "/submissions/submit",
      payload,
      initData,
    );

    if (submitErr) {
      setError(submitErr);
    } else {
      setSuccess(true);
    }
  }, [week, days, events, notes, initData]);

  const weekStatus = week?.status || null;
  const canSubmit = weekStatus === "open";
  const isLocked = !canSubmit;

  return {
    loading,
    error,
    success,
    week,
    days,
    events,
    notes,
    setNotes,
    weekStatus,
    canSubmit,
    isLocked,
    toggleAvailable,
    setShiftType,
    setHours,
    toggleEvent,
    submit,
  };
}