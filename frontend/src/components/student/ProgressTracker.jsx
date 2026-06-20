import React from "react";
import Card from "../common/Card";

const ProgressTracker = ({ progressData }) => {
  const subjects = progressData?.subjects || [];

  return (
    <div className="space-y-4 sm:space-y-6">
      <Card title="Overall Progress">
        <div className="space-y-3 sm:space-y-4">
          <div className="flex justify-between items-center">
            <span className="text-sm sm:text-base text-gray-700">
              Overall Completion
            </span>
            <span className="font-semibold text-blue-600 text-sm sm:text-base">
              {progressData?.overallProgress || 0}%
            </span>
          </div>
          <div className="w-full bg-gray-200 rounded-full h-3 sm:h-4">
            <div
              className="bg-gradient-to-r from-blue-500 to-blue-600 h-3 sm:h-4 rounded-full transition-all"
              style={{ width: `${progressData?.overallProgress || 0}%` }}
            ></div>
          </div>
        </div>
      </Card>

      <Card title="Subject Progress">
        <div className="space-y-4 sm:space-y-6">
          {subjects.map((subject, index) => (
            <div key={index}>
              <div className="flex justify-between items-center mb-2">
                <div>
                  <h4 className="font-medium text-gray-900 text-sm sm:text-base">
                    {subject.name}
                  </h4>
                  <p className="text-xs sm:text-sm text-gray-500">
                    Current Level: Grade {subject.level}
                  </p>
                </div>
                <span className="font-semibold text-gray-700 text-sm sm:text-base">
                  {subject.progress}%
                </span>
              </div>
              <div className="w-full bg-gray-200 rounded-full h-2 sm:h-3">
                <div
                  className="bg-green-500 h-2 sm:h-3 rounded-full transition-all"
                  style={{ width: `${subject.progress}%` }}
                ></div>
              </div>
              <div className="mt-2 flex items-center space-x-3 sm:space-x-4 text-xs sm:text-sm text-gray-600">
                <span>📚 {subject.completedLessons} lessons</span>
                <span>✅ {subject.completedTests} tests</span>
              </div>
            </div>
          ))}
        </div>
      </Card>

      <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-4 sm:gap-6">
        <Card title="Strengths">
          <ul className="space-y-2">
            {progressData?.strengths?.map((strength, index) => (
              <li key={index} className="flex items-center text-green-600">
                <span className="mr-2">✓</span>
                {strength}
              </li>
            )) || <p className="text-gray-500">No data yet</p>}
          </ul>
        </Card>

        <Card title="Areas to Improve">
          <ul className="space-y-2">
            {progressData?.weaknesses?.map((weakness, index) => (
              <li key={index} className="flex items-center text-orange-600">
                <span className="mr-2">⚠</span>
                {weakness}
              </li>
            )) || <p className="text-gray-500">No data yet</p>}
          </ul>
        </Card>

        <Card title="Achievements">
          <div className="space-y-2">
            {progressData?.achievements?.map((achievement, index) => (
              <div key={index} className="flex items-center space-x-2">
                <span className="text-2xl">{achievement.icon}</span>
                <span className="text-sm">{achievement.name}</span>
              </div>
            )) || <p className="text-gray-500">No achievements yet</p>}
          </div>
        </Card>
      </div>
    </div>
  );
};

export default ProgressTracker;
