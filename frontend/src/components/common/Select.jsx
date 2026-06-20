const Select = ({
  label,
  name,
  value,
  onChange,
  options = [],
  error,
  required = false,
  disabled = false,
  className = "",
  placeholder = "Select an option",
}) => {
  return (
    <div className={`mb-4 ${className}`}>
      {label && (
        <label
          className="block text-sm font-medium mb-1"
          style={{ color: "#323232" }}
        >
          {label}
          {required && <span className="text-red-600 ml-1">*</span>}
        </label>
      )}
      <select
        name={name}
        value={value}
        onChange={onChange}
        required={required}
        disabled={disabled}
        className={`w-full px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 disabled:opacity-50 disabled:cursor-not-allowed transition-all ${
          error ? "border-red-500" : ""
        }`}
        style={{
          backgroundColor: "#F5EDE5",
          color: "#323232",
          borderColor: error ? "#ef4444" : "#C9BDB3",
          boxShadow: "0 1px 2px 0 rgba(50, 50, 50, 0.05)",
        }}
      >
        <option value="">{placeholder}</option>
        {options.map((option, index) => (
          <option key={index} value={option.value}>
            {option.label}
          </option>
        ))}
      </select>
      {error && <p className="mt-1 text-sm text-red-600">{error}</p>}
    </div>
  );
};

export default Select;
