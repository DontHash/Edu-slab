/**
 * Reusable Badge Component
 *
 * Props:
 * - children: Badge text
 * - variant: 'success' | 'warning' | 'danger' | 'info'
 * - size: 'sm' | 'md' | 'lg'
 *
 * Usage:
 * <Badge variant="success">Active</Badge>
 */

const Badge = ({ children, variant = "info", size = "md" }) => {
  const variants = {
    success: "bg-[#F5EDE5] text-[#323232] border border-[#C9BDB3]",
    warning: "bg-[#E8DDD3] text-[#323232] border border-[#C9BDB3]",
    danger: "bg-[#EBE1D8] text-[#323232] border border-[#C9BDB3]",
    info: "bg-[#F5EDE5] text-[#5A5A5A] border border-[#C9BDB3]",
  };

  const sizes = {
    sm: "text-xs px-2.5 py-0.5",
    md: "text-xs px-3 py-1 font-semibold",
    lg: "text-sm px-4 py-1.5 font-semibold",
  };

  return (
    <span
      className={`inline-flex items-center rounded-full ${variants[variant]} ${sizes[size]}`}
    >
      {children}
    </span>
  );
};

export default Badge;
