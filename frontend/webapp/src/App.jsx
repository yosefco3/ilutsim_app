/**
 * Root component — wires Telegram hook to submission hook.
 */
import { useTelegram } from "./hooks/useTelegram.js";
import { useSubmission } from "./hooks/useSubmission.js";
import SubmissionForm from "./components/SubmissionForm.jsx";

export default function App() {
  const { initData, isDevMode } = useTelegram();
  const submission = useSubmission(initData);

  return (
    <>
      {isDevMode && (
        <div
          style={{
            background: "#fff3cd",
            borderBottom: "1px solid #ffc107",
            padding: "8px 16px",
            textAlign: "center",
            fontSize: "13px",
            color: "#856404",
            fontFamily: "sans-serif",
          }}
        >
          ⚙️ <strong>Dev Mode</strong> — Running outside Telegram. Data is read-only until you open a week from the{" "}
          <a href="http://localhost:3001" target="_blank" rel="noreferrer" style={{ color: "#856404", textDecoration: "underline" }}>
            Admin Dashboard
          </a>.
        </div>
      )}
      <SubmissionForm submission={submission} />
    </>
  );
}
