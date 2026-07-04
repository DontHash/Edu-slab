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
      className={`ds-panel ${paddingStyles[padding]} ${className} ${
        hoverable ? "ds-panel-interactive" : ""
      } animate-fade-in`}
    >
      {title && (
        <h3 className="mb-5 border-b border-border pb-3 text-lg font-bold text-foreground">
          {title}
        </h3>
      )}
      {children}
    </div>
  );
};

export default Card;
