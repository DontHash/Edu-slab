const Loading = ({
  size = "md",
  fullScreen = false,
  message = "Loading...",
}) => {
  const sizes = {
    sm: "w-8 h-8",
    md: "w-12 h-12",
    lg: "w-16 h-16",
  };

  const spinner = (
    <div className="flex flex-col items-center justify-center">
      <div
        className={`${sizes[size]} border-4 rounded-full animate-spin`}
        style={{ borderColor: "#E8DDD3", borderTopColor: "#323232" }}
      ></div>
      {message && (
        <p className="mt-4" style={{ color: "#323232" }}>
          {message}
        </p>
      )}
    </div>
  );

  if (fullScreen) {
    return (
      <div
        className="fixed inset-0 flex items-center justify-center z-50"
        style={{ backgroundColor: "rgba(221, 208, 200, 0.95)" }}
      >
        {spinner}
      </div>
    );
  }

  return spinner;
};

export default Loading;
