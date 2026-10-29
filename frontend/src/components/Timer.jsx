import { useEffect, useRef, useState } from "react";

function format(seconds) {
  const whole = Math.max(0, Math.ceil(seconds));
  return `${Math.floor(whole / 60)}:${String(whole % 60).padStart(2, "0")}`;
}

export default function Timer({ seconds, limit, running, onExpire, resetKey }) {
  const [remaining, setRemaining] = useState(seconds);
  const expired = useRef(false);
  const onExpireRef = useRef(onExpire);
  onExpireRef.current = onExpire;

  useEffect(() => {
    if (!running) return undefined; // freeze the display once the bug is answered
    expired.current = false;
    setRemaining(seconds);
    const end = Date.now() + seconds * 1000;
    const id = setInterval(() => {
      const left = Math.max(0, (end - Date.now()) / 1000);
      setRemaining(left);
      if (left <= 0 && !expired.current) {
        expired.current = true;
        clearInterval(id);
        onExpireRef.current?.();
      }
    }, 200);
    return () => clearInterval(id);
  }, [resetKey, running, seconds]);

  const percent = Math.max(0, Math.min(100, (remaining / limit) * 100));
  const urgent = remaining <= 10;
  return (
    <div className={urgent ? "timer urgent" : "timer"} role="timer" aria-label="Time left">
      <div className="timer-bar" aria-hidden="true">
        <div className="timer-fill" style={{ width: `${percent}%` }} />
      </div>
      <span className="timer-text">{format(remaining)}</span>
    </div>
  );
}
