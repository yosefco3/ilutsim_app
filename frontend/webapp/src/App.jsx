/**
 * Root component — wires Telegram hook to submission hook.
 */
import { useTelegram } from "./hooks/useTelegram.js";
import { useSubmission } from "./hooks/useSubmission.js";
import SubmissionForm from "./components/SubmissionForm.jsx";

export default function App() {
  const { initData } = useTelegram();
  const submission = useSubmission(initData);

  return <SubmissionForm submission={submission} />;
}