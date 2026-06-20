import Badge from "../common/Badge";
import Button from "../common/Button";
import Card from "../common/Card";

const ResultsView = ({ results, onRetake, onViewDetails }) => {
  const {
    score,
    totalQuestions,
    correctAnswers,
    timeSpent,
    level,
    recommendations,
  } = results;

  const getScoreColor = (score) => {
    if (score >= 80) return "text-green-600";
    if (score >= 60) return "text-yellow-600";
    return "text-red-600";
  };

  const getPerformanceBadge = (score) => {
    if (score >= 90) return { text: "Excellent", variant: "success" };
    if (score >= 80) return { text: "Very Good", variant: "success" };
    if (score >= 70) return { text: "Good", variant: "primary" };
    if (score >= 60) return { text: "Average", variant: "warning" };
    return { text: "Needs Improvement", variant: "danger" };
  };

  const performance = getPerformanceBadge(score);

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      {/* Score Card */}
      <Card>
        <div className="text-center py-8">
          <div className="mb-4">
            <div className={`text-6xl font-bold ${getScoreColor(score)} mb-2`}>
              {score}%
            </div>
            <Badge variant={performance.variant} size="lg">
              {performance.text}
            </Badge>
          </div>

          <div className="grid grid-cols-3 gap-6 mt-8 pt-6 border-t">
            <div>
              <div className="text-2xl font-semibold text-gray-900">
                {correctAnswers}
              </div>
              <div className="text-sm text-gray-600">Correct Answers</div>
            </div>
            <div>
              <div className="text-2xl font-semibold text-gray-900">
                {totalQuestions}
              </div>
              <div className="text-sm text-gray-600">Total Questions</div>
            </div>
            <div>
              <div className="text-2xl font-semibold text-gray-900">
                {timeSpent}
              </div>
              <div className="text-sm text-gray-600">Time Spent</div>
            </div>
          </div>
        </div>
      </Card>

      {/* Level Assessment */}
      <Card title="Your Assessment">
        <div className="space-y-4">
          <div className="p-4 bg-[#F5EDE5] rounded-lg border border-[#C9BDB3]">
            <h4 className="font-semibold text-[#323232] mb-2">
              Determined Level
            </h4>
            <p className="text-[#323232]">
              Based on your performance, your current level is assessed as{" "}
              <span className="font-bold text-[#323232]">Grade {level}</span>
            </p>
          </div>

          {results.breakdown && (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="p-4 bg-gray-50 rounded-lg">
                <h5 className="text-sm font-medium text-gray-600 mb-2">
                  Strengths
                </h5>
                <ul className="space-y-1">
                  {results.breakdown.strengths?.map((strength, index) => (
                    <li
                      key={index}
                      className="text-sm text-green-600 flex items-start"
                    >
                      <span className="mr-2">✓</span>
                      <span>{strength}</span>
                    </li>
                  ))}
                </ul>
              </div>

              <div className="p-4 bg-gray-50 rounded-lg">
                <h5 className="text-sm font-medium text-gray-600 mb-2">
                  Areas to Improve
                </h5>
                <ul className="space-y-1">
                  {results.breakdown.weaknesses?.map((weakness, index) => (
                    <li
                      key={index}
                      className="text-sm text-orange-600 flex items-start"
                    >
                      <span className="mr-2">⚠</span>
                      <span>{weakness}</span>
                    </li>
                  ))}
                </ul>
              </div>
            </div>
          )}
        </div>
      </Card>

      {/* Recommendations */}
      {recommendations && recommendations.length > 0 && (
        <Card title="Recommended Resources">
          <div className="space-y-3">
            {recommendations.map((resource, index) => (
              <div
                key={index}
                className="p-4 border border-gray-200 rounded-lg hover:border-blue-300 transition-colors"
              >
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <h4 className="font-medium text-gray-900 mb-1">
                      {resource.title}
                    </h4>
                    <p className="text-sm text-gray-600">
                      {resource.description}
                    </p>
                  </div>
                  <Badge variant="info" size="sm">
                    {resource.type}
                  </Badge>
                </div>
              </div>
            ))}
          </div>
        </Card>
      )}

      {/* Actions */}
      <Card>
        <div className="flex flex-col md:flex-row gap-4">
          <Button onClick={onViewDetails} variant="primary" fullWidth>
            View Detailed Report
          </Button>
          <Button onClick={onRetake} variant="outline" fullWidth>
            Retake Assessment
          </Button>
        </div>
      </Card>
    </div>
  );
};

export default ResultsView;
