/**
 * Reusable Input Component
 *
 * Props:
 * - label: Input label text
 * - type: Input type (text, email, password, etc.)
 * - value: Input value
 * - onChange: Change handler function
 * - error: Error message to display
 * - placeholder: Placeholder text
 * - required: Boolean for required field
 *
 * Usage:
 * <Input
 *   label="Email"
 *   type="email"
 *   value={email}
 *   onChange={(e) => setEmail(e.target.value)}
 *   error={errors.email}
 * />
 */

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
        <label
          className="block text-sm font-medium mb-2"
          style={{ color: "#323232" }}
        >
          {label} {required && <span className="text-red-600">*</span>}
        </label>
      )}
      <input
        type={type}
        value={value}
        onChange={onChange}
        placeholder={placeholder}
        required={required}
        className={`w-full px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:border-transparent transition-all ${
          error ? "border-red-500" : ""
        }`}
        style={{
          backgroundColor: "#F5EDE5",
          color: "#323232",
          borderColor: error ? "#ef4444" : "#C9BDB3",
          boxShadow: "0 1px 2px 0 rgba(50, 50, 50, 0.05)",
        }}
      />
      {error && <p className="mt-1 text-sm text-red-600">{error}</p>}
    </div>
  );
};

export default Input;
