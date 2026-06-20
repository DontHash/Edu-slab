import React from "react";
import Card from "../common/Card";

const Analytics = ({ analyticsData }) => {
  const overallStats = analyticsData?.overallStats || {};
  const performanceByGrade = analyticsData?.performanceByGrade || [];
  const subjectPerformance = analyticsData?.subjectPerformance || [];

  return (
    <div className="space-y-6">
      <Card title="Overall Statistics">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
          <div className="text-center">
            <div className="text-3xl font-bold text-blue-600">
              {overallStats.totalAssessments || 0}
            </div>
            <div className="text-sm text-gray-600 mt-1">Total Assessments</div>
          </div>
          <div className="text-center">
            <div className="text-3xl font-bold text-green-600">
              {overallStats.avgCompletionRate || 0}%
            </div>
            <div className="text-sm text-gray-600 mt-1">
              Avg Completion Rate
            </div>
          </div>
          <div className="text-center">
            <div className="text-3xl font-bold text-purple-600">
              {overallStats.avgScore || 0}%
            </div>
            <div className="text-sm text-gray-600 mt-1">Average Score</div>
          </div>
          <div className="text-center">
            <div className="text-3xl font-bold text-orange-600">
              {overallStats.activeStudents || 0}
            </div>
            <div className="text-sm text-gray-600 mt-1">Active Students</div>
          </div>
        </div>
      </Card>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Performance by Grade */}
        <Card title="Performance by Grade">
          <div className="space-y-4">
            {performanceByGrade.length > 0 ? (
              performanceByGrade.map((grade, index) => (
                <div key={index}>
                  <div className="flex justify-between text-sm mb-2">
                    <span className="font-medium text-gray-700">
                      Grade {grade.grade}
                    </span>
                    <span className="text-gray-600">{grade.avgScore}%</span>
                  </div>
                  <div className="w-full bg-gray-200 rounded-full h-3">
                    <div
                      className={`h-3 rounded-full ${
                        grade.avgScore >= 80
                          ? "bg-green-500"
                          : grade.avgScore >= 60
                          ? "bg-yellow-500"
                          : "bg-red-500"
                      }`}
                      style={{ width: `${grade.avgScore}%` }}
                    ></div>
                  </div>
                  <div className="flex justify-between text-xs text-gray-500 mt-1">
                    <span>{grade.totalStudents} students</span>
                    <span>{grade.completedTests} tests</span>
                  </div>
                </div>
              ))
            ) : (
              <p className="text-gray-500 text-center py-8">
                No data available
              </p>
            )}
          </div>
        </Card>

        {/* Subject Performance */}
        <Card title="Subject Performance">
          <div className="space-y-4">
            {subjectPerformance.length > 0 ? (
              subjectPerformance.map((subject, index) => (
                <div key={index}>
                  <div className="flex justify-between text-sm mb-2">
                    <span className="font-medium text-gray-700">
                      {subject.name}
                    </span>
                    <span className="text-gray-600">{subject.avgScore}%</span>
                  </div>
                  <div className="w-full bg-gray-200 rounded-full h-3">
                    <div
                      className={`h-3 rounded-full ${
                        subject.avgScore >= 80
                          ? "bg-blue-500"
                          : subject.avgScore >= 60
                          ? "bg-yellow-500"
                          : "bg-red-500"
                      }`}
                      style={{ width: `${subject.avgScore}%` }}
                    ></div>
                  </div>
                  <div className="flex justify-between text-xs text-gray-500 mt-1">
                    <span>{subject.totalAssessments} assessments</span>
                    <span>{subject.avgCompletionTime} avg time</span>
                  </div>
                </div>
              ))
            ) : (
              <p className="text-gray-500 text-center py-8">
                No data available
              </p>
            )}
          </div>
        </Card>
      </div>

      {/* Attendance Overview */}
      <Card title="Attendance Overview">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="p-4 bg-green-50 rounded-lg text-center">
            <div className="text-2xl font-bold text-green-600">
              {analyticsData?.attendance?.present || 0}%
            </div>
            <div className="text-sm text-gray-600 mt-1">Present</div>
          </div>
          <div className="p-4 bg-yellow-50 rounded-lg text-center">
            <div className="text-2xl font-bold text-yellow-600">
              {analyticsData?.attendance?.late || 0}%
            </div>
            <div className="text-sm text-gray-600 mt-1">Late</div>
          </div>
          <div className="p-4 bg-red-50 rounded-lg text-center">
            <div className="text-2xl font-bold text-red-600">
              {analyticsData?.attendance?.absent || 0}%
            </div>
            <div className="text-sm text-gray-600 mt-1">Absent</div>
          </div>
        </div>
      </Card>

      {/* Weekly Trends */}
      <Card title="Weekly Activity Trends">
        <div className="space-y-4">
          <div className="flex items-end justify-between h-48 gap-2">
            {analyticsData?.weeklyTrends?.map((day, index) => (
              <div key={index} className="flex-1 flex flex-col items-center">
                <div
                  className="w-full bg-blue-500 rounded-t hover:bg-blue-600 transition-colors cursor-pointer"
                  style={{
                    height: `${
                      (day.value /
                        Math.max(
                          ...analyticsData.weeklyTrends.map((d) => d.value)
                        )) *
                      100
                    }%`,
                  }}
                  title={`${day.value} activities`}
                ></div>
                <span className="text-xs text-gray-600 mt-2">{day.day}</span>
              </div>
            )) ||
              Array(7)
                .fill(0)
                .map((_, i) => (
                  <div key={i} className="flex-1 flex flex-col items-center">
                    <div
                      className="w-full bg-gray-200 rounded-t"
                      style={{ height: "20%" }}
                    ></div>
                    <span className="text-xs text-gray-400 mt-2">
                      Day {i + 1}
                    </span>
                  </div>
                ))}
          </div>
        </div>
      </Card>
    </div>
  );
};

export default Analytics;
