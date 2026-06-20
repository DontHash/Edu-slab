import Input from "../common/Input";
import Textarea from "../common/Textarea";

const AnswerInput = ({ question, value, onChange }) => {
  if (question.type === "multiple-choice") {
    return (
      <div className="space-y-3">
        {question.options.map((option, index) => (
          <button
            key={index}
            onClick={() => onChange(option)}
            className={`w-full p-4 text-left border-2 rounded-lg transition-all ${
              value === option
                ? "border-[#5A5A5A] bg-[#E8DDD3]"
                : "border-[#C9BDB3] hover:border-[#5A5A5A] hover:bg-[#F5EDE5]"
            }`}
          >
            <div className="flex items-center">
              <div
                className={`w-5 h-5 rounded-full border-2 mr-3 flex items-center justify-center ${
                  value === option ? "border-[#5A5A5A]" : "border-[#C9BDB3]"
                }`}
              >
                {value === option && (
                  <div className="w-3 h-3 rounded-full bg-[#5A5A5A]"></div>
                )}
              </div>
              <span className="font-medium text-gray-700 mr-2">
                {String.fromCharCode(65 + index)}.
              </span>
              <span className="text-gray-900">{option}</span>
            </div>
          </button>
        ))}
      </div>
    );
  }

  if (question.type === "true-false") {
    return (
      <div className="flex gap-4">
        <button
          onClick={() => onChange("true")}
          className={`flex-1 p-6 border-2 rounded-lg transition-all ${
            value === "true"
              ? "border-[#5A5A5A] bg-[#E8DDD3]"
              : "border-[#C9BDB3] hover:border-[#5A5A5A] hover:bg-[#F5EDE5]"
          }`}
        >
          <div className="text-4xl mb-2">✓</div>
          <div className="font-semibold text-[#323232]">True</div>
        </button>
        <button
          onClick={() => onChange("false")}
          className={`flex-1 p-6 border-2 rounded-lg transition-all ${
            value === "false"
              ? "border-[#5A5A5A] bg-[#E8DDD3]"
              : "border-[#C9BDB3] hover:border-[#5A5A5A] hover:bg-[#F5EDE5]"
          }`}
        >
          <div className="text-4xl mb-2">✗</div>
          <div className="font-semibold text-[#323232]">False</div>
        </button>
      </div>
    );
  }

  if (question.type === "short-answer") {
    return (
      <div>
        <Input
          placeholder="Type your answer here..."
          value={value}
          onChange={(e) => onChange(e.target.value)}
        />
        <p className="text-xs text-gray-500 mt-2">
          Tip: Be concise and specific in your answer
        </p>
      </div>
    );
  }

  if (question.type === "essay" || question.type === "written") {
    return (
      <div>
        <Textarea
          placeholder="Write your detailed answer here... Our AI will evaluate your response for accuracy, clarity, and understanding."
          value={value}
          onChange={(e) => onChange(e.target.value)}
          rows={10}
        />
        <div className="flex justify-between items-center mt-2">
          <p className="text-xs text-gray-500">
            {value?.length || 0} characters
          </p>
          <p className="text-xs text-gray-500">AI evaluation enabled ✓</p>
        </div>
      </div>
    );
  }

  return null;
};

export default AnswerInput;
