const Alert = ({ type = "info", message, onClose, className = "" }) => {
  const types = {
    success: "border-primary/30 bg-primary/10 text-primary",
    error: "border-danger/30 bg-danger/10 text-danger",
    warning: "border-warning/30 bg-warning/10 text-warning",
    info: "border-border bg-surface-raised text-muted",
  };

  return (
    <div className={`mb-4 rounded-lg border p-4 ${types[type]} ${className}`}>
      <div className="flex items-start justify-between gap-3">
        <p className="text-sm font-medium">{message}</p>
        {onClose && (
          <button onClick={onClose} className="text-muted hover:text-foreground">
            ✕
          </button>
        )}
      </div>
    </div>
  );
};

export default Alert;
