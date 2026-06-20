import Badge from "../common/Badge";
import Button from "../common/Button";
import Card from "../common/Card";

const WeeklyTests = ({ tests = [] }) => {
  return (
    <div className="space-y-4 sm:space-y-6">
      <Card title="Weekly Tests">
        <p className="text-sm sm:text-base text-gray-600 mb-4 sm:mb-6">
          Complete weekly tests to track your progress and reinforce your
          learning.
        </p>

        <div className="space-y-3 sm:space-y-4">
          {tests.length > 0 ? (
            tests.map((test, index) => (
              <div
                key={index}
                className="p-3 sm:p-4 border rounded-lg hover:shadow-sm transition-all"
                style={{ backgroundColor: "#F5EDE5", borderColor: "#C9BDB3" }}
              >
                <div className="flex flex-col sm:flex-row sm:justify-between sm:items-start mb-3 gap-2">
                  <div className="flex-1">
                    <h4 className="font-semibold text-gray-900 mb-1 text-sm sm:text-base">
                      {test.title}
                    </h4>
                    <p className="text-xs sm:text-sm text-gray-600">
                      {test.description}
                    </p>
                  </div>
                  <Badge
                    variant={
                      test.status === "completed"
                        ? "success"
                        : test.status === "in-progress"
                        ? "warning"
                        : "default"
                    }
                  >
                    {test.status}
                  </Badge>
                </div>

                <div className="flex items-center justify-between flex-wrap gap-4">
                  <div className="flex items-center space-x-6 text-sm text-gray-600">
                    <span className="flex items-center gap-2">
                      📅 <span className="font-medium">{test.dueDate}</span>
                    </span>
                    <span className="flex items-center gap-2">
                      ⏱ <span className="font-medium">{test.duration}</span>
                    </span>
                    <span className="flex items-center gap-2">
                      📝{" "}
                      <span className="font-medium">
                        {test.questions} questions
                      </span>
                    </span>
                  </div>

                  <div className="flex gap-2">
                    {test.status === "not-started" && (
                      <Button size="sm">Start Test</Button>
                    )}
                    {test.status === "in-progress" && (
                      <Button size="sm" variant="secondary">
                        Continue
                      </Button>
                    )}
                    {test.status === "completed" && (
                      <Button size="sm" variant="ghost">
                        View Results
                      </Button>
                    )}
                  </div>
                </div>

                {test.score && (
                  <div className="mt-4 pt-4 border-t-2 border-gray-200">
                    <div className="flex justify-between items-center">
                      <span className="text-sm font-semibold text-gray-600">
                        Your Score:
                      </span>
                      <span className="text-2xl font-bold bg-gradient-to-r from-green-600 to-emerald-600 bg-clip-text text-transparent">
                        {test.score}%
                      </span>
                    </div>
                  </div>
                )}
              </div>
            ))
          ) : (
            <div className="text-center py-16">
              <div className="text-6xl mb-4">📝</div>
              <p className="text-gray-500 text-lg">
                No tests available at the moment
              </p>
            </div>
          )}
        </div>
      </Card>
    </div>
  );
};

export default WeeklyTests;
