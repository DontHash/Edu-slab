import React, { useState } from "react";
import Card from "../common/Card";
import Button from "../common/Button";
import Input from "../common/Input";
import Select from "../common/Select";
import Textarea from "../common/Textarea";
import Alert from "../common/Alert";

const AssessmentCreator = ({ onSave }) => {
  const [assessment, setAssessment] = useState({
    title: "",
    subject: "",
    grade: "",
    difficulty: "medium",
    questions: [],
  });

  const [currentQuestion, setCurrentQuestion] = useState({
    question: "",
    type: "multiple-choice",
    options: ["", "", "", ""],
    correctAnswer: "",
    difficulty: "medium",
  });

  const [showSuccess, setShowSuccess] = useState(false);

  const handleAddQuestion = () => {
    if (currentQuestion.question && currentQuestion.correctAnswer) {
      setAssessment({
        ...assessment,
        questions: [...assessment.questions, currentQuestion],
      });
      setCurrentQuestion({
        question: "",
        type: "multiple-choice",
        options: ["", "", "", ""],
        correctAnswer: "",
        difficulty: "medium",
      });
      setShowSuccess(true);
      setTimeout(() => setShowSuccess(false), 3000);
    }
  };

  const handleRemoveQuestion = (index) => {
    const newQuestions = assessment.questions.filter((_, i) => i !== index);
    setAssessment({ ...assessment, questions: newQuestions });
  };

  const handleSaveAssessment = () => {
    if (assessment.title && assessment.questions.length > 0) {
      onSave?.(assessment);
      // Reset form
      setAssessment({
        title: "",
        subject: "",
        grade: "",
        difficulty: "medium",
        questions: [],
      });
    }
  };

  return (
    <div className="space-y-6">
      {/* Assessment Details */}
      <Card title="Assessment Details">
        <div className="space-y-4">
          <Input
            label="Assessment Title"
            value={assessment.title}
            onChange={(e) =>
              setAssessment({ ...assessment, title: e.target.value })
            }
            placeholder="Enter assessment title"
            required
          />

          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <Select
              label="Subject"
              value={assessment.subject}
              onChange={(e) =>
                setAssessment({ ...assessment, subject: e.target.value })
              }
              options={[
                { value: "math", label: "Mathematics" },
                { value: "english", label: "English" },
                { value: "science", label: "Science" },
                { value: "social", label: "Social Studies" },
              ]}
              required
            />

            <Select
              label="Grade Level"
              value={assessment.grade}
              onChange={(e) =>
                setAssessment({ ...assessment, grade: e.target.value })
              }
              options={[
                { value: "5", label: "Grade 5" },
                { value: "6", label: "Grade 6" },
                { value: "7", label: "Grade 7" },
                { value: "8", label: "Grade 8" },
                { value: "9", label: "Grade 9" },
                { value: "10", label: "Grade 10" },
              ]}
              required
            />

            <Select
              label="Overall Difficulty"
              value={assessment.difficulty}
              onChange={(e) =>
                setAssessment({ ...assessment, difficulty: e.target.value })
              }
              options={[
                { value: "easy", label: "Easy" },
                { value: "medium", label: "Medium" },
                { value: "hard", label: "Hard" },
              ]}
            />
          </div>
        </div>
      </Card>

      {/* Add Question */}
      <Card title="Add Question">
        {showSuccess && (
          <Alert
            type="success"
            message="Question added successfully!"
            onClose={() => setShowSuccess(false)}
          />
        )}

        <div className="space-y-4">
          <Textarea
            label="Question"
            value={currentQuestion.question}
            onChange={(e) =>
              setCurrentQuestion({
                ...currentQuestion,
                question: e.target.value,
              })
            }
            placeholder="Enter your question"
            rows={3}
            required
          />

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <Select
              label="Question Type"
              value={currentQuestion.type}
              onChange={(e) =>
                setCurrentQuestion({ ...currentQuestion, type: e.target.value })
              }
              options={[
                { value: "multiple-choice", label: "Multiple Choice" },
                { value: "true-false", label: "True/False" },
                { value: "short-answer", label: "Short Answer" },
              ]}
            />

            <Select
              label="Difficulty"
              value={currentQuestion.difficulty}
              onChange={(e) =>
                setCurrentQuestion({
                  ...currentQuestion,
                  difficulty: e.target.value,
                })
              }
              options={[
                { value: "easy", label: "Easy" },
                { value: "medium", label: "Medium" },
                { value: "hard", label: "Hard" },
              ]}
            />
          </div>

          {currentQuestion.type === "multiple-choice" && (
            <div className="space-y-2">
              <label className="block text-sm font-medium text-gray-700">
                Options
              </label>
              {currentQuestion.options.map((option, index) => (
                <Input
                  key={index}
                  placeholder={`Option ${index + 1}`}
                  value={option}
                  onChange={(e) => {
                    const newOptions = [...currentQuestion.options];
                    newOptions[index] = e.target.value;
                    setCurrentQuestion({
                      ...currentQuestion,
                      options: newOptions,
                    });
                  }}
                />
              ))}
            </div>
          )}

          <Input
            label="Correct Answer"
            value={currentQuestion.correctAnswer}
            onChange={(e) =>
              setCurrentQuestion({
                ...currentQuestion,
                correctAnswer: e.target.value,
              })
            }
            placeholder="Enter the correct answer"
            required
          />

          <Button onClick={handleAddQuestion} fullWidth>
            Add Question to Assessment
          </Button>
        </div>
      </Card>

      {/* Questions List */}
      {assessment.questions.length > 0 && (
        <Card title={`Questions (${assessment.questions.length})`}>
          <div className="space-y-4">
            {assessment.questions.map((q, index) => (
              <div
                key={index}
                className="p-4 border border-gray-200 rounded-lg"
              >
                <div className="flex justify-between items-start mb-2">
                  <h4 className="font-medium text-gray-900">
                    Question {index + 1}
                  </h4>
                  <Button
                    size="sm"
                    variant="danger"
                    onClick={() => handleRemoveQuestion(index)}
                  >
                    Remove
                  </Button>
                </div>
                <p className="text-gray-700 mb-2">{q.question}</p>
                <div className="flex gap-2 text-sm text-gray-600">
                  <span className="px-2 py-1 bg-gray-100 rounded">
                    Type: {q.type}
                  </span>
                  <span className="px-2 py-1 bg-gray-100 rounded">
                    Difficulty: {q.difficulty}
                  </span>
                </div>
              </div>
            ))}
          </div>

          <div className="mt-6">
            <Button
              onClick={handleSaveAssessment}
              fullWidth
              variant="success"
              disabled={!assessment.title || assessment.questions.length === 0}
            >
              Save Assessment
            </Button>
          </div>
        </Card>
      )}
    </div>
  );
};

export default AssessmentCreator;
