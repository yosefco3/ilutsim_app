/**
 * Banner shown when the week is not open for submissions.
 * Displays a status-specific message.
 */
import { messages } from "../utils/messages.js";

const STATUS_MESSAGES = {
  locked: messages.LOCK_STATUS_LOCKED,
  published: messages.LOCK_STATUS_PUBLISHED,
};

export default function LockBanner({ status }) {
  const text = STATUS_MESSAGES[status] || messages.LOCK_NO_WEEK;
  return <div className="lock-banner">{text}</div>;
}