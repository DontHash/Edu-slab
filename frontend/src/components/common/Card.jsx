/**
 * Reusable Card Component
 *
 * Props:
 * - children: Card content
 * - title: Optional card title
 * - className: Additional CSS classes
 * - padding: 'sm' | 'md' | 'lg'
 *
 * Usage:
 * <Card title="Dashboard">
 *   <p>Card content here</p>
 * </Card>
 */

const Card = ({
  children,
  title,
  className = "",
  padding = "md",
  hoverable = false,
}) => {
  const paddingStyles = {
    sm: "p-4",
    md: "p-6",
    lg: "p-8",
  };

  return (
    <div
      className={`rounded-xl shadow-sm border ${
        paddingStyles[padding]
      } ${className} ${
        hoverable
          ? "hover:shadow-md transition-all duration-200 cursor-pointer"
          : ""
      }`}
      style={{
        backgroundColor: "#F5EDE5",
        borderColor: "#C9BDB3",
        boxShadow: "0 1px 2px 0 rgba(50, 50, 50, 0.05)",
      }}
    >
      {title && (
        <h3
          className="text-lg font-bold mb-5 pb-3"
          style={{ color: "#323232", borderBottom: "1px solid #C9BDB3" }}
        >
          {title}
        </h3>
      )}
      {children}
    </div>
  );
};

export default Card;
