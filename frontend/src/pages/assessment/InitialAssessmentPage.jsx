import { useState } from "react";
import { useNavigate } from "react-router-dom";
import AnswerInput from "../../components/assessment/AnswerInput";
import Button from "../../components/common/Button";
import Card from "../../components/common/Card";

const InitialAssessmentPage = () => {
  const navigate = useNavigate();
  const [currentQuestion, setCurrentQuestion] = useState(0);
  const [answers, setAnswers] = useState({});
  const [loading, setLoading] = useState(false);

  // Mock questions - in real app, fetch from API
  const questions = [
    {
      id: 1,
      type: "multiple_choice",
      subject: "Mathematics",
      topic: "Algebra",
      question: "What is the solution to 2x + 5 = 13?",
      options: ["x = 2", "x = 4", "x = 6", "x = 8"],
      difficulty: "medium",
    },
    {
      id: 2,
      type: "multiple_choice",
      subject: "Mathematics",
      topic: "Geometry",
      question: "What is the area of a triangle with base 6 and height 4?",
      options: ["10", "12", "24", "48"],
      difficulty: "easy",
    },
    {
      id: 3,
      type: "short_answer",
      subject: "English",
      topic: "Grammar",
      question: "What is the past tense of 'run'?",
      difficulty: "easy",
    },
    {
      id: 4,
      type: "essay",
      subject: "English",
      topic: "Writing",
      question:
        "Explain the difference between 'your' and 'you're' with examples.",
      difficulty: "medium",
    },
    {
      id: 5,
      type: "multiple_choice",
      subject: "Mathematics",
      topic: "Arithmetic",
      question: "What is 15% of 200?",
      options: ["15", "20", "30", "35"],
      difficulty: "easy",
    },
  ];

  const handleAnswer = (questionId, answer) => {
    setAnswers({ ...answers, [questionId]: answer });
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
    setLoading(true);

    try {
      // In real app, submit to API: POST /api/assessments/initial/submit
      // const result = await assessmentService.submitInitial(answers);

      setTimeout(() => {
        // Navigate to results or dashboard after AI evaluation
        navigate("/dashboard");
      }, 2000);
    } catch (error) {
      console.error("Failed to submit assessment:", error);
      setLoading(false);
    }
  };

  const question = questions[currentQuestion];
  const progress = ((currentQuestion + 1) / questions.length) * 100;

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-purple-50 p-4 sm:p-6">
      <div className="max-w-3xl mx-auto">
        {/* Header */}
        <div className="text-center mb-6">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">
            Initial Assessment
          </h1>
          <p className="text-gray-600">
            Help us understand your current level in Math and English
          </p>
        </div>

        {/* Progress Bar */}
        <div className="mb-6">
          <div className="flex justify-between text-sm text-gray-600 mb-2">
            <span>
              Question {currentQuestion + 1} of {questions.length}
            </span>
            <span>{Math.round(progress)}% Complete</span>
          </div>
          <div className="w-full bg-gray-200 rounded-full h-3">
            <div
              className="bg-gradient-to-r from-blue-500 to-purple-500 h-3 rounded-full transition-all duration-300"
              style={{ width: `${progress}%` }}
            />
          </div>
        </div>

        {/* Question Card */}
        <Card className="mb-6">
          <div className="mb-4">
            <div className="flex items-center justify-between mb-3">
              <span className="px-3 py-1 bg-blue-100 text-blue-700 rounded-full text-sm font-medium">
                {question.subject}
              </span>
              <span className="px-3 py-1 bg-purple-100 text-purple-700 rounded-full text-sm font-medium">
                {question.topic}
              </span>
            </div>
            <h2 className="text-xl font-semibold text-gray-900 mb-4">
              {question.question}
            </h2>
          </div>

          <AnswerInput
            question={question}
            value={answers[question.id] || ""}
            onChange={(answer) => handleAnswer(question.id, answer)}
          />
        </Card>

        {/* Navigation Buttons */}
        <div className="flex justify-between items-center">
          <Button
            variant="secondary"
            onClick={handlePrevious}
            disabled={currentQuestion === 0}
          >
            ← Previous
          </Button>

          <div className="text-sm text-gray-500">
            {Object.keys(answers).length} / {questions.length} answered
          </div>

          {currentQuestion === questions.length - 1 ? (
            <Button
              onClick={handleSubmit}
              loading={loading}
              disabled={Object.keys(answers).length < questions.length}
            >
              Submit Assessment
            </Button>
          ) : (
            <Button onClick={handleNext} disabled={!answers[question.id]}>
              Next →
            </Button>
          )}
        </div>

        {/* Info Box */}
        <div className="mt-6 p-4 bg-yellow-50 border border-yellow-200 rounded-lg">
          <p className="text-sm text-yellow-800">
            <strong>💡 Tip:</strong> Answer all questions to the best of your
            ability. Our AI will evaluate your responses and match you with peer
            tutors who can help with your weak areas, and identify peers you can
            help!
          </p>
        </div>
      </div>
    </div>
  );
};

export default InitialAssessmentPage;
