import React, { useState } from "react";
import Card from "../common/Card";
import Button from "../common/Button";

const AssessmentView = ({ onComplete }) => {
  const [currentQuestion, setCurrentQuestion] = useState(0);
  const [answers, setAnswers] = useState({});
  const [isSubmitting, setIsSubmitting] = useState(false);

  // This would be dynamic from the backend
  const questions = [
    {
      id: 1,
      question: "What is 2 + 2?",
      type: "multiple-choice",
      options: ["2", "3", "4", "5"],
      difficulty: "easy",
    },
  ];

  const handleAnswer = (answer) => {
    setAnswers({ ...answers, [currentQuestion]: answer });
  };

  const handleNext = () => {
    if (currentQuestion < questions.length - 1) {
      setCurrentQuestion(currentQuestion + 1);
    }
  };

  const handlePrevious = () => {
    if (currentQuestion > 0) {
      setCurrentQuestion(currentQuestion - 1);
    }
  };

  const handleSubmit = async () => {
    setIsSubmitting(true);
    // Submit answers to backend
    setTimeout(() => {
      setIsSubmitting(false);
      onComplete?.();
    }, 1000);
  };

  const question = questions[currentQuestion];
  const progress = ((currentQuestion + 1) / questions.length) * 100;

  return (
    <div className="max-w-4xl mx-auto">
      <Card>
        {/* Progress Bar */}
        <div className="mb-6">
          <div className="flex justify-between text-sm text-gray-600 mb-2">
            <span>
              Question {currentQuestion + 1} of {questions.length}
            </span>
            <span>{Math.round(progress)}% Complete</span>
          </div>
          <div className="w-full bg-gray-200 rounded-full h-2">
            <div
              className="bg-blue-600 h-2 rounded-full transition-all duration-300"
              style={{ width: `${progress}%` }}
            ></div>
          </div>
        </div>

        {/* Question */}
        <div className="mb-8">
          <h2 className="text-2xl font-semibold text-gray-900 mb-6">
            {question.question}
          </h2>

          {question.type === "multiple-choice" && (
            <div className="space-y-3">
              {question.options.map((option, index) => (
                <button
                  key={index}
                  onClick={() => handleAnswer(option)}
                  className={`w-full p-4 text-left border-2 rounded-lg transition-all ${
                    answers[currentQuestion] === option
                      ? "border-blue-500 bg-blue-50"
                      : "border-gray-200 hover:border-gray-300"
                  }`}
                >
                  <span className="font-medium">
                    {String.fromCharCode(65 + index)}.
                  </span>{" "}
                  {option}
                </button>
              ))}
            </div>
          )}
        </div>

        {/* Navigation */}
        <div className="flex justify-between items-center pt-6 border-t">
          <Button
            variant="outline"
            onClick={handlePrevious}
            disabled={currentQuestion === 0}
          >
            Previous
          </Button>

          {currentQuestion === questions.length - 1 ? (
            <Button
              onClick={handleSubmit}
              loading={isSubmitting}
              disabled={!answers[currentQuestion]}
            >
              Submit Assessment
            </Button>
          ) : (
            <Button onClick={handleNext} disabled={!answers[currentQuestion]}>
              Next
            </Button>
          )}
        </div>
      </Card>
    </div>
  );
};

export default AssessmentView;
