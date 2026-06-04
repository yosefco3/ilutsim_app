/**
 * Banner shown when the week is locked for submissions.
 */
import { messages } from "../utils/messages.js";

export default function LockBanner() {
  return <div className="lock-banner">{messages.LOCK_BANNER}</div>;
}