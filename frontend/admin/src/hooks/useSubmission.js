/**
 * Hook to load, edit, and submit a weekly constraints form.
 * Each day holds a shifts map { morning, afternoon, night } → { active, from_hour, to_hour }.
 */
import { useState, useEffect, useCallback } from "react";
import { get, post } from "../api/guardApiClient.js";

const SHIFT_TYPES = ["morning", "afternoon", "night"];

/** Create a default shifts map (all inactive, no custom hours). */
function defaultShifts() {
  const map = {};
  for (const st of SHIFT_TYPES) {
    map[st] = { active: false, from_hour: "", to_hour: "" };
  }
  return map;
}

/**
 * @param {string} initData - Telegram initData for auth
 */
export function useSubmission(initData) {
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(null);
  const [week, setWeek] = useState(null);
  const [days, setDays] = useState([]);
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

      const subResult = await get("/submissions/current-week", initData);

      if (subResult.error) {
        if (isDevMode) {
          setError(
            "No open week found. Open a week from the admin dashboard first, then refresh this page.",
          );
        } else {
          setError(subResult.error);
        }
        setLoading(false);
        return;
      }

      if (cancelled) return;

      const weekData = subResult.data;
      setWeek(weekData);

      // Get existing submission (may be null)
      const { data: subData } = await get(
        `/submissions/my?week_id=${weekData.id}`,
        initData,
      );

      if (cancelled) return;

      // Build initial form state — each day gets a shifts map
      const initialDays = (weekData.days || []).map((d) => {
        const shifts = defaultShifts();

        const existingDay = subData?.days?.find(
          (s) => s.day_index === d.day_index,
        );
        if (existingDay?.shifts) {
          for (const sh of existingDay.shifts) {
            if (shifts[sh.shift_type]) {
              shifts[sh.shift_type] = {
                active: true,
                from_hour: sh.from_hour ?? sh.start_time ?? "",
                to_hour: sh.to_hour ?? sh.end_time ?? "",
              };
            }
          }
        }

        return {
          day_index: d.day_index,
          blocked: d.blocked || false,
          shifts,
        };
      });

      setDays(initialDays);
      setNotes(subData?.notes ?? subData?.general_notes ?? "");
      setLoading(false);
    }

    load();
    return () => {
      cancelled = true;
    };
  }, [initData]); // eslint-disable-line react-hooks/exhaustive-deps

  // ── Toggle a single shift (morning / afternoon / night) ──────
  const toggleShift = useCallback((dayIndex, shiftType) => {
    setDays((prev) =>
      prev.map((d) => {
        if (d.day_index !== dayIndex) return d;
        const shifts = { ...d.shifts };
        shifts[shiftType] = {
          ...shifts[shiftType],
          active: !shifts[shiftType].active,
        };
        return { ...d, shifts };
      }),
    );
  }, []);

  // ── Set custom hours for a specific shift ────────────────────
  const setShiftHours = useCallback((dayIndex, shiftType, from, to) => {
    setDays((prev) =>
      prev.map((d) => {
        if (d.day_index !== dayIndex) return d;
        const shifts = { ...d.shifts };
        shifts[shiftType] = {
          ...shifts[shiftType],
          from_hour: from,
          to_hour: to,
        };
        return { ...d, shifts };
      }),
    );
  }, []);

  // ── Submit the form ──────────────────────────────────────────
  const submit = useCallback(async () => {
    if (!week) return;

    setError(null);
    setSuccess(null);

    const payload = {
      week_id: week.id,
      general_notes: notes || null,
      days: days
        .filter((d) => !d.blocked)
        .map((d) => ({
          day_index: d.day_index,
          shifts: SHIFT_TYPES.filter((st) => d.shifts[st].active).map(
            (st) => ({
              shift_type: st,
              from_hour: d.shifts[st].from_hour || null,
              to_hour: d.shifts[st].to_hour || null,
            }),
          ),
        })),
    };

    const { error: submitErr } = await post(
      "/submissions",
      payload,
      initData,
    );

    if (submitErr) {
      setError(submitErr);
    } else {
      setSuccess(true);
    }
  }, [week, days, notes, initData]);

  const weekStatus = week?.status || null;
  const canSubmit = weekStatus === "open";
  const isLocked = !canSubmit;

  return {
    loading,
    error,
    success,
    week,
    days,
    notes,
    setNotes,
    weekStatus,
    canSubmit,
    isLocked,
    toggleShift,
    setShiftHours,
    submit,
  };
}