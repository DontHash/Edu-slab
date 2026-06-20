/**
 * Loading Spinner Component
 *
 * Props:
 * - size: 'sm' | 'md' | 'lg'
 * - text: Optional loading text
 *
 * Usage:
 * <Loader size="lg" text="Loading..." />
 */

const Loader = ({ size = "md", text }) => {
  const sizes = {
    sm: "w-6 h-6",
    md: "w-10 h-10",
    lg: "w-16 h-16",
  };

  return (
    <div className="flex flex-col items-center justify-center">
      <div
        className={`${sizes[size]} border-4 border-[#E8DDD3] border-t-[#323232] rounded-full animate-spin`}
      />
      {text && <p className="mt-4 text-[#323232]">{text}</p>}
    </div>
  );
};

export default Loader;
