function Logo({
  size = 42,
  showText = true,
  dark = true,
}) {
  return (
    <div className="docpilot-logo">
      <svg
        className="docpilot-mark"
        viewBox="0 0 100 100"
        width={size}
        height={size}
        fill="none"
        xmlns="http://www.w3.org/2000/svg"
        aria-label="DocPilot logo"
      >
        <defs>
          <linearGradient
            id="docPilotGradient"
            x1="15"
            y1="10"
            x2="85"
            y2="90"
            gradientUnits="userSpaceOnUse"
          >
            <stop offset="0%" stopColor="#22D3EE" />
            <stop offset="50%" stopColor="#3B82F6" />
            <stop offset="100%" stopColor="#8B5CF6" />
          </linearGradient>
        </defs>

        {/* Document */}
        <path
          d="M25 8H62L82 28V78C82 84.6 76.6 90 70 90H25C18.4 90 13 84.6 13 78V20C13 13.4 18.4 8 25 8Z"
          stroke="url(#docPilotGradient)"
          strokeWidth="7"
          strokeLinejoin="round"
        />

        {/* Fold */}
        <path
          d="M62 8V25C62 27.8 64.2 30 67 30H82"
          stroke="url(#docPilotGradient)"
          strokeWidth="7"
          strokeLinejoin="round"
        />

        {/* Document lines */}
        <path
          d="M29 35H51"
          stroke="url(#docPilotGradient)"
          strokeWidth="5"
          strokeLinecap="round"
        />

        <path
          d="M29 46H58"
          stroke="url(#docPilotGradient)"
          strokeWidth="5"
          strokeLinecap="round"
        />

        <path
          d="M29 57H46"
          stroke="url(#docPilotGradient)"
          strokeWidth="5"
          strokeLinecap="round"
        />

        {/* Main AI spark */}
        <path
          d="M56 38L59.8 47.2L69 51L59.8 54.8L56 64L52.2 54.8L43 51L52.2 47.2L56 38Z"
          fill="white"
          stroke="url(#docPilotGradient)"
          strokeWidth="3"
          strokeLinejoin="round"
        />

        {/* Small spark */}
        <path
          d="M35 67L37 71L41 73L37 75L35 79L33 75L29 73L33 71L35 67Z"
          fill="url(#docPilotGradient)"
        />

        {/* Pilot / navigation plane */}
        <path
          d="M20 77L76 57L48 91L43 78L20 77Z"
          fill="url(#docPilotGradient)"
          stroke="#0F172A"
          strokeWidth="2.5"
          strokeLinejoin="round"
        />

        <path
          d="M20 77L43 78L76 57"
          stroke="#E0F2FE"
          strokeWidth="3"
          strokeLinecap="round"
          strokeLinejoin="round"
        />
      </svg>

      {showText && (
        <div
          className={`docpilot-wordmark ${
            dark ? "wordmark-dark" : "wordmark-light"
          }`}
        >
          <span className="doc-text">Doc</span>
          <span className="pilot-text">Pilot</span>
        </div>
      )}
    </div>
  );
}

export default Logo;