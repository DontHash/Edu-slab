/**
 * Reusable Button Component
 *
 * Props:
 * - children: Button text/content
 * - variant: 'primary' | 'secondary' | 'outline' | 'danger'
 * - size: 'sm' | 'md' | 'lg'
 * - onClick: Click handler function
 * - disabled: Boolean to disable button
 * - className: Additional CSS classes
 *
 * Usage:
 * <Button variant="primary" onClick={handleClick}>Click Me</Button>
 */

const Button = ({
  children,
  variant = "primary",
  size = "md",
  onClick,
  disabled = false,
  className = "",
  type = "button",
}) => {
  // Define base styles
  const baseStyles =
    "font-semibold rounded-lg transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed shadow-sm hover:shadow-md";

  // Define variant styles
  const variants = {
    primary: "text-white hover:opacity-90",
    secondary: "hover:opacity-90",
    outline: "border-2 hover:opacity-80",
    danger:
      "bg-gradient-to-r from-rose-600 to-red-700 text-white hover:from-rose-700 hover:to-red-800",
    success: "hover:opacity-90",
    ghost: "hover:opacity-80",
  };

  const getVariantStyle = (variant) => {
    switch (variant) {
      case "primary":
        return { backgroundColor: "#323232", color: "#DDD0C8" };
      case "secondary":
        return { backgroundColor: "#4A4A4A", color: "#DDD0C8" };
      case "outline":
        return {
          borderColor: "#323232",
          color: "#323232",
          backgroundColor: "transparent",
        };
      case "success":
        return { backgroundColor: "#323232", color: "#DDD0C8" };
      case "ghost":
        return { color: "#323232", backgroundColor: "transparent" };
      default:
        return { backgroundColor: "#323232", color: "#DDD0C8" };
    }
  };

  // Define size styles
  const sizes = {
    sm: "px-4 py-2 text-sm",
    md: "px-5 py-2.5 text-sm",
    lg: "px-6 py-3 text-base",
  };

  return (
    <button
      type={type}
      onClick={onClick}
      disabled={disabled}
      className={`${baseStyles} ${variants[variant]} ${sizes[size]} ${className}`}
      style={variant !== "danger" ? getVariantStyle(variant) : {}}
    >
      {children}
    </button>
  );
};

export default Button;
