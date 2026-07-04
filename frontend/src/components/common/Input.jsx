const Input = ({
  label,
  type = "text",
  value,
  onChange,
  error,
  placeholder,
  required = false,
  className = "",
}) => {
  return (
    <div className={`mb-4 ${className}`}>
      {label && (
        <label className="ds-mono-label mb-2 block">
          {label} {required && <span className="text-danger">*</span>}
        </label>
      )}
      <input
        type={type}
        value={value}
        onChange={onChange}
        placeholder={placeholder}
        required={required}
        className={`ds-input ${error ? "border-danger/50 focus:ring-danger/20" : ""}`}
      />
      {error && <p className="mt-1 text-sm text-danger">{error}</p>}
    </div>
  );
};

export default Input;
