const Badge = ({ children, variant = "info", size = "md", className = "", style }) => {
  const variants = {
    success: "ds-badge-primary",
    warning: "ds-badge-warn",
    danger: "ds-badge-danger",
    info: "ds-badge-muted",
  };

  const sizes = {
    sm: "text-[9px] px-2 py-0.5",
    md: "",
    lg: "text-xs px-3 py-1",
  };

  return (
    <span
      className={`${variants[variant] || variants.info} ${sizes[size]} ${className}`}
      style={style}
    >
      {children}
    </span>
  );
};

export default Badge;
