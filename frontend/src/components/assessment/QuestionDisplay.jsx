import Card from "../common/Card";

const QuestionDisplay = ({ question, questionNumber, totalQuestions }) => {
  return (
    <Card>
      <div className="mb-4">
        <div className="flex justify-between items-center text-sm text-gray-600 mb-2">
          <span>
            Question {questionNumber} of {totalQuestions}
          </span>
          <span className="px-3 py-1 bg-gray-100 rounded-full">
            {question.difficulty}
          </span>
        </div>
      </div>

      <div className="mb-6">
        <h3 className="text-xl font-semibold text-gray-900 mb-4">
          {question.question}
        </h3>

        {question.image && (
          <img
            src={question.image}
            alt="Question visual"
            className="max-w-md mx-auto rounded-lg shadow-md mb-4"
          />
        )}

        {question.context && (
          <div className="p-4 bg-[#F5EDE5] border-l-4 border-[#C9BDB3] rounded mb-4">
            <p className="text-[#323232]">{question.context}</p>
          </div>
        )}
      </div>
    </Card>
  );
};

export default QuestionDisplay;
