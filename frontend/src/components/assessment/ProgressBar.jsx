const ProgressBar = ({ current, total, percentage }) => {
  const calculatedPercentage = percentage || (current / total) * 100;

  return (
    <div className="w-full">
      <div className="flex justify-between text-sm text-gray-600 mb-2">
        <span>Progress</span>
        <span>{Math.round(calculatedPercentage)}%</span>
      </div>
      <div className="w-full bg-[#E8DDD3] rounded-full h-3 overflow-hidden">
        <div
          className="h-full bg-[#5A5A5A] rounded-full transition-all duration-500 ease-out"
          style={{ width: `${calculatedPercentage}%` }}
        ></div>
      </div>
      <div className="flex justify-between text-xs text-gray-500 mt-1">
        <span>
          {current} of {total} completed
        </span>
        <span>{total - current} remaining</span>
      </div>
    </div>
  );
};

export default ProgressBar;
