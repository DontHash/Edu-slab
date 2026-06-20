import { useState } from "react";
import Button from "../common/Button";
import Card from "../common/Card";

const Flashcard = ({ flashcard, onNext, onPrevious, currentIndex, total }) => {
  const [isFlipped, setIsFlipped] = useState(false);

  return (
    <div className="max-w-2xl mx-auto">
      <div className="flex justify-between items-center mb-4">
        <h3 className="text-lg font-semibold text-gray-700">
          {flashcard.topic}
        </h3>
        <span className="text-sm text-gray-500">
          {currentIndex + 1} / {total}
        </span>
      </div>

      <div
        className="relative h-96 cursor-pointer perspective-1000"
        onClick={() => setIsFlipped(!isFlipped)}
      >
        <div
          className={`absolute w-full h-full transition-transform duration-500 transform-style-3d ${
            isFlipped ? "rotate-y-180" : ""
          }`}
        >
          {/* Front of card */}
          <Card
            className={`absolute w-full h-full backface-hidden ${
              isFlipped ? "hidden" : "flex"
            } items-center justify-center`}
          >
            <div className="text-center p-8">
              <div className="text-6xl mb-6">❓</div>
              <h2 className="text-2xl font-bold text-gray-900 mb-4">
                {flashcard.question}
              </h2>
              <p className="text-sm text-gray-500 mt-8">
                Click to reveal answer
              </p>
            </div>
          </Card>

          {/* Back of card */}
          <Card
            className={`absolute w-full h-full backface-hidden ${
              isFlipped ? "flex" : "hidden"
            } items-center justify-center bg-gradient-to-br from-blue-50 to-purple-50`}
          >
            <div className="text-center p-8">
              <div className="text-6xl mb-6">✅</div>
              <h2 className="text-2xl font-bold text-gray-900 mb-4">
                {flashcard.answer}
              </h2>
              {flashcard.explanation && (
                <p className="text-gray-700 mt-4">{flashcard.explanation}</p>
              )}
              <p className="text-sm text-gray-500 mt-8">
                Click to see question again
              </p>
            </div>
          </Card>
        </div>
      </div>

      <div className="flex gap-4 mt-6">
        <Button
          onClick={onPrevious}
          disabled={currentIndex === 0}
          variant="secondary"
          fullWidth
        >
          ← Previous
        </Button>
        <Button
          onClick={onNext}
          disabled={currentIndex === total - 1}
          fullWidth
        >
          Next →
        </Button>
      </div>
    </div>
  );
};

const FlashcardsViewer = ({ topic, flashcards }) => {
  const [currentIndex, setCurrentIndex] = useState(0);

  const handleNext = () => {
    if (currentIndex < flashcards.length - 1) {
      setCurrentIndex(currentIndex + 1);
    }
  };

  const handlePrevious = () => {
    if (currentIndex > 0) {
      setCurrentIndex(currentIndex - 1);
    }
  };

  if (!flashcards || flashcards.length === 0) {
    return (
      <Card>
        <div className="text-center py-12">
          <div className="text-6xl mb-4">📚</div>
          <p className="text-gray-500">
            No flashcards available for this topic
          </p>
        </div>
      </Card>
    );
  }

  return (
    <div className="space-y-6">
      <div className="text-center">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">{topic}</h1>
        <p className="text-gray-600">
          Study with flashcards to improve your understanding
        </p>
      </div>

      <Flashcard
        flashcard={flashcards[currentIndex]}
        onNext={handleNext}
        onPrevious={handlePrevious}
        currentIndex={currentIndex}
        total={flashcards.length}
      />

      {/* Progress bar */}
      <div className="max-w-2xl mx-auto">
        <div className="w-full bg-gray-200 rounded-full h-2">
          <div
            className="bg-blue-600 h-2 rounded-full transition-all duration-300"
            style={{
              width: `${((currentIndex + 1) / flashcards.length) * 100}%`,
            }}
          ></div>
        </div>
      </div>
    </div>
  );
};

export default FlashcardsViewer;
