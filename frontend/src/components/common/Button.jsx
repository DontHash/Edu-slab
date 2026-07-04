const Button = ({
  children,
  variant = "primary",
  size = "md",
  onClick,
  disabled = false,
  className = "",
  type = "button",
}) => {
  const variants = {
    primary: "ds-btn-primary",
    secondary: "ds-btn-primary opacity-90",
    outline: "ds-btn-outline",
    danger:
      "ds-btn bg-danger/90 text-white px-5 py-2.5 hover:bg-danger active:scale-[0.98]",
    success: "ds-btn-primary",
    ghost: "ds-btn-ghost",
  };

  const sizes = {
    sm: "px-3 py-1.5 text-xs",
    md: "",
    lg: "px-7 py-3 text-base",
  };

  return (
    <button
      type={type}
      onClick={onClick}
      disabled={disabled}
      className={`${variants[variant] || variants.primary} ${sizes[size]} ${className}`}
    >
      {children}
    </button>
  );
};

export default Button;
