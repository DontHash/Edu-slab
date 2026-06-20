import Badge from "../common/Badge";
import Card from "../common/Card";

const TeacherDashboard = ({ teacher }) => {
  const stats = [
    {
      label: "Total Students",
      value: teacher?.totalStudents || 0,
      icon: "👥",
      color: "bg-blue-500",
    },
    {
      label: "Active Assessments",
      value: teacher?.activeAssessments || 0,
      icon: "📝",
      color: "bg-green-500",
    },
    {
      label: "Avg Performance",
      value: `${teacher?.avgPerformance || 0}%`,
      icon: "📊",
      color: "bg-purple-500",
    },
    {
      label: "Pending Reviews",
      value: teacher?.pendingReviews || 0,
      icon: "⏳",
      color: "bg-orange-500",
    },
  ];

  const recentStudents = teacher?.recentStudents || [];
  const upcomingClasses = teacher?.upcomingClasses || [];
  const assignedStudents = teacher?.assignedStudents || [];
  const teachingSubjects = teacher?.teachingSubjects || [];

  return (
    <div className="space-y-4 sm:space-y-6">
      {/* Welcome Section */}
      <div className="bg-gradient-to-r from-green-500 to-green-600 rounded-lg p-4 sm:p-6 text-white">
        <h1 className="text-xl sm:text-2xl lg:text-3xl font-bold mb-2">
          Welcome, {teacher?.name}!
        </h1>
        <p className="text-green-100 mb-3">
          You can teach Math & English to students in your assigned grade range.
        </p>
        <div className="flex flex-wrap gap-3">
          <div className="bg-white/20 px-4 py-2 rounded-lg">
            <span className="text-xs text-green-100">
              Primary Teaching Grade
            </span>
            <div className="text-xl font-bold">
              Grade {teacher?.teachingLevel || "N/A"}
            </div>
          </div>
          <div className="bg-white/20 px-4 py-2 rounded-lg">
            <span className="text-xs text-green-100">Can Teach Grades</span>
            <div className="text-xl font-bold">
              {teacher?.canTeachGrades || "N/A"}
            </div>
          </div>
          <div className="bg-white/20 px-4 py-2 rounded-lg">
            <span className="text-xs text-green-100">Qualification</span>
            <div className="text-sm font-semibold">
              {teacher?.qualification || "Not Set"}
            </div>
          </div>
          <div className="bg-white/20 px-4 py-2 rounded-lg">
            <span className="text-xs text-green-100">Evaluation Score</span>
            <div className="text-xl font-bold">
              {teacher?.evaluationScore || "N/A"}%
            </div>
          </div>
        </div>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-2 md:grid-cols-2 lg:grid-cols-4 gap-3 sm:gap-4 lg:gap-6">
        {stats.map((stat, index) => (
          <Card key={index}>
            <div className="flex items-center space-x-4">
              <div
                className={`w-12 h-12 ${stat.color} rounded-lg flex items-center justify-center text-2xl`}
              >
                {stat.icon}
              </div>
              <div>
                <div className="text-2xl font-bold text-gray-900">
                  {stat.value}
                </div>
                <div className="text-sm text-gray-600">{stat.label}</div>
              </div>
            </div>
          </Card>
        ))}
      </div>

      {/* Teaching Subjects & Specializations */}
      <Card title="📚 Your Teaching Subjects (Math & English Only)">
        {teachingSubjects.length > 0 ? (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {teachingSubjects.map((subject, index) => (
              <div
                key={index}
                className="p-4 bg-gradient-to-br from-green-50 to-emerald-50 border border-green-200 rounded-lg"
              >
                <div className="flex items-start justify-between mb-2">
                  <h4 className="font-semibold text-gray-900">
                    {subject.name}
                  </h4>
                  <Badge variant="success">{subject.proficiency}%</Badge>
                </div>
                <div className="mb-2">
                  <p className="text-xs text-gray-600 mb-1">
                    Teaching grades: {subject.assignedGrades?.join(", ")}
                  </p>
                </div>
                <div className="flex flex-wrap gap-1 mb-2">
                  {subject.topics.map((topic, idx) => (
                    <span
                      key={idx}
                      className="px-2 py-0.5 bg-green-100 text-green-700 text-xs rounded"
                    >
                      {topic}
                    </span>
                  ))}
                </div>
                <p className="text-xs text-gray-500">
                  {subject.studentsCount} students assigned
                </p>
              </div>
            ))}
          </div>
        ) : (
          <div className="text-center py-8">
            <p className="text-gray-500 mb-2">
              No teaching subjects assigned yet.
            </p>
            <p className="text-sm text-gray-400">
              Complete your Math & English evaluation to get assigned students!
            </p>
          </div>
        )}
      </Card>

      {/* Assigned Students */}
      <Card title="👨‍🎓 Your Assigned Students">
        <p className="text-sm text-gray-600 mb-4">
          Students matched to you based on their weak areas and grade level
          compatibility
        </p>
        {assignedStudents.length > 0 ? (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {assignedStudents.map((student, index) => (
              <div
                key={index}
                className="p-4 border border-gray-200 rounded-lg hover:border-green-300 transition"
              >
                <div className="flex items-start space-x-3 mb-3">
                  <div className="w-12 h-12 rounded-full bg-gradient-to-br from-blue-500 to-indigo-500 flex items-center justify-center text-white font-bold text-lg">
                    {student.name.charAt(0)}
                  </div>
                  <div className="flex-1">
                    <h4 className="font-semibold text-gray-900">
                      {student.name}
                    </h4>
                    <p className="text-sm text-gray-600">
                      Grade {student.grade}
                    </p>
                  </div>
                  <Badge
                    variant={
                      student.status === "active" ? "success" : "warning"
                    }
                  >
                    {student.status}
                  </Badge>
                </div>
                {student.matchReason && (
                  <div className="mb-2 p-2 bg-blue-50 border border-blue-200 rounded">
                    <p className="text-xs text-blue-700">
                      <strong>Match reason:</strong> {student.matchReason}
                    </p>
                  </div>
                )}
                <div className="mb-2">
                  <p className="text-sm font-medium text-gray-700 mb-1">
                    Weak areas (Math & English):
                  </p>
                  <div className="flex flex-wrap gap-2">
                    {student.weakAreas.map((area, idx) => (
                      <span
                        key={idx}
                        className="px-2 py-1 bg-red-100 text-red-700 text-xs rounded-full"
                      >
                        {area}
                      </span>
                    ))}
                  </div>
                </div>
                <div className="flex gap-2 mt-3">
                  <button className="flex-1 px-3 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition text-sm font-medium">
                    View Progress
                  </button>
                  <button className="flex-1 px-3 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition text-sm font-medium">
                    Schedule Session
                  </button>
                </div>
              </div>
            ))}
          </div>
        ) : (
          <div className="text-center py-8">
            <p className="text-gray-500 mb-2">No students assigned yet.</p>
            <p className="text-sm text-gray-400">
              Students will be matched to you based on their weak areas and your
              specializations.
            </p>
          </div>
        )}
      </Card>

      {/* Main Content Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Recent Students Activity */}
        <Card title="Recent Student Activity">
          {recentStudents.length > 0 ? (
            <div className="space-y-4">
              {recentStudents.map((student, index) => (
                <div
                  key={index}
                  className="flex items-center justify-between p-3 bg-gray-50 rounded-lg"
                >
                  <div className="flex items-center space-x-3">
                    <div className="w-10 h-10 rounded-full bg-blue-500 flex items-center justify-center text-white font-semibold">
                      {student.name.charAt(0)}
                    </div>
                    <div>
                      <p className="font-medium text-gray-900">
                        {student.name}
                      </p>
                      <p className="text-sm text-gray-500">
                        {student.activity}
                      </p>
                    </div>
                  </div>
                  <Badge
                    variant={
                      student.status === "completed" ? "success" : "warning"
                    }
                  >
                    {student.status}
                  </Badge>
                </div>
              ))}
            </div>
          ) : (
            <p className="text-gray-500 text-center py-8">No recent activity</p>
          )}
        </Card>

        {/* Upcoming Classes */}
        <Card title="Upcoming Classes">
          {upcomingClasses.length > 0 ? (
            <div className="space-y-4">
              {upcomingClasses.map((classItem, index) => (
                <div
                  key={index}
                  className="p-4 border border-gray-200 rounded-lg"
                >
                  <div className="flex justify-between items-start mb-2">
                    <h4 className="font-medium text-gray-900">
                      {classItem.subject}
                    </h4>
                    <Badge variant="info">{classItem.time}</Badge>
                  </div>
                  <p className="text-sm text-gray-600">
                    Grade {classItem.grade}
                  </p>
                  <p className="text-xs text-gray-500 mt-1">
                    {classItem.students} students
                  </p>
                </div>
              ))}
            </div>
          ) : (
            <p className="text-gray-500 text-center py-8">
              No upcoming classes
            </p>
          )}
        </Card>
      </div>
    </div>
  );
};

export default TeacherDashboard;
