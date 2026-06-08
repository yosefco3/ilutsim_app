/**
 * Hook to load, edit, and submit a weekly constraints form.
 * Each day holds a shifts map { morning, afternoon, night } → { active, from_hour, to_hour }.
 *
 * Default hours come from the server (editable by admin via /admin/settings),
 * falling back to SHIFT_DEFAULTS from guardMessages.js.
 */
import { useState, useEffect, useCallback } from "react";
import { get, post } from "../api/guardApiClient.js";
import { SHIFT_DEFAULTS } from "../utils/guardMessages.js";

const SHIFT_TYPES = ["morning", "afternoon", "night"];

/** Create a default shifts map using supplied defaults. */
function makeShifts(defaults) {
  const map = {};
  for (const st of SHIFT_TYPES) {
    const d = defaults[st] || { from_hour: "", to_hour: "" };
    map[st] = { active: false, from_hour: d.from_hour, to_hour: d.to_hour };
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
  const [shiftDefaults, setShiftDefaults] = useState(SHIFT_DEFAULTS);

  // ── Dev mode flag ──────────────────────────────────────────────
  const isDevMode = initData === "__DEV_MODE__";

  // ── Fetch shift defaults from server (fallback to static SHIFT_DEFAULTS)
  useEffect(() => {
    if (!initData) return;
    get("/submissions/shift-defaults", initData).then(({ data, error: err }) => {
      if (!err && data) {
        // Server returns { shift_default_morning: {from_hour, to_hour}, ... }
        // Map keys: shift_default_morning → morning
        const mapped = {};
        for (const key of Object.keys(data)) {
          const short = key.replace("shift_default_", "");
          if (SHIFT_TYPES.includes(short)) {
            mapped[short] = data[key];
          }
        }
        if (Object.keys(mapped).length === 3) {
          setShiftDefaults(mapped);
        }
      }
    });
  }, [initData]);

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
        // Use current shiftDefaults (may have been updated from server)
        const shifts = makeShifts(SHIFT_DEFAULTS);

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
  const toggleShift = useCallback(
    (dayIndex, shiftType) => {
      setDays((prev) =>
        prev.map((d) => {
          if (d.day_index !== dayIndex) return d;
          const shifts = { ...d.shifts };
          const current = shifts[shiftType];
          // When toggling ON, ensure default hours are filled
          const def = shiftDefaults[shiftType] || { from_hour: "", to_hour: "" };
          shifts[shiftType] = {
            ...current,
            active: !current.active,
            from_hour: current.from_hour || def.from_hour,
            to_hour: current.to_hour || def.to_hour,
          };
          return { ...d, shifts };
        }),
      );
    },
    [shiftDefaults],
  );

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

    const { error: submitErr } = await post("/submissions", payload, initData);

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