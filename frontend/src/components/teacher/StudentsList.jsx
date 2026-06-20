import React, { useState } from "react";
import Card from "../common/Card";
import Button from "../common/Button";
import Input from "../common/Input";
import Badge from "../common/Badge";
import Modal from "../common/Modal";

const StudentsList = ({ students = [] }) => {
  const [searchTerm, setSearchTerm] = useState("");
  const [selectedStudent, setSelectedStudent] = useState(null);
  const [filterGrade, setFilterGrade] = useState("all");

  const filteredStudents = students.filter((student) => {
    const matchesSearch = student.name
      .toLowerCase()
      .includes(searchTerm.toLowerCase());
    const matchesGrade = filterGrade === "all" || student.grade === filterGrade;
    return matchesSearch && matchesGrade;
  });

  return (
    <div className="space-y-6">
      {/* Filters */}
      <Card>
        <div className="flex flex-col md:flex-row gap-4">
          <div className="flex-1">
            <Input
              placeholder="Search students..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
            />
          </div>
          <div className="flex gap-2">
            <Button
              variant={filterGrade === "all" ? "primary" : "ghost"}
              size="sm"
              onClick={() => setFilterGrade("all")}
            >
              All Grades
            </Button>
            {[5, 6, 7, 8, 9, 10].map((grade) => (
              <Button
                key={grade}
                variant={filterGrade === grade ? "primary" : "ghost"}
                size="sm"
                onClick={() => setFilterGrade(grade)}
              >
                Grade {grade}
              </Button>
            ))}
          </div>
        </div>
      </Card>

      {/* Students Table */}
      <Card title={`Students (${filteredStudents.length})`}>
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-4 py-3 text-left text-sm font-semibold text-gray-900">
                  Name
                </th>
                <th className="px-4 py-3 text-left text-sm font-semibold text-gray-900">
                  Grade
                </th>
                <th className="px-4 py-3 text-left text-sm font-semibold text-gray-900">
                  Level
                </th>
                <th className="px-4 py-3 text-left text-sm font-semibold text-gray-900">
                  Progress
                </th>
                <th className="px-4 py-3 text-left text-sm font-semibold text-gray-900">
                  Status
                </th>
                <th className="px-4 py-3 text-left text-sm font-semibold text-gray-900">
                  Actions
                </th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-200">
              {filteredStudents.length > 0 ? (
                filteredStudents.map((student, index) => (
                  <tr key={index} className="hover:bg-gray-50">
                    <td className="px-4 py-3">
                      <div className="flex items-center space-x-3">
                        <div className="w-8 h-8 rounded-full bg-blue-500 flex items-center justify-center text-white text-sm font-semibold">
                          {student.name.charAt(0)}
                        </div>
                        <span className="font-medium text-gray-900">
                          {student.name}
                        </span>
                      </div>
                    </td>
                    <td className="px-4 py-3 text-gray-700">{student.grade}</td>
                    <td className="px-4 py-3 text-gray-700">
                      Grade {student.currentLevel}
                    </td>
                    <td className="px-4 py-3">
                      <div className="flex items-center space-x-2">
                        <div className="flex-1 bg-gray-200 rounded-full h-2 w-20">
                          <div
                            className="bg-green-500 h-2 rounded-full"
                            style={{ width: `${student.progress}%` }}
                          ></div>
                        </div>
                        <span className="text-sm text-gray-600">
                          {student.progress}%
                        </span>
                      </div>
                    </td>
                    <td className="px-4 py-3">
                      <Badge
                        variant={
                          student.status === "active" ? "success" : "warning"
                        }
                      >
                        {student.status}
                      </Badge>
                    </td>
                    <td className="px-4 py-3">
                      <Button
                        size="sm"
                        variant="ghost"
                        onClick={() => setSelectedStudent(student)}
                      >
                        View Details
                      </Button>
                    </td>
                  </tr>
                ))
              ) : (
                <tr>
                  <td
                    colSpan="6"
                    className="px-4 py-8 text-center text-gray-500"
                  >
                    No students found
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </Card>

      {/* Student Detail Modal */}
      <Modal
        isOpen={!!selectedStudent}
        onClose={() => setSelectedStudent(null)}
        title={selectedStudent?.name}
        size="lg"
      >
        {selectedStudent && (
          <div className="space-y-6">
            <div className="grid grid-cols-2 gap-4">
              <div>
                <p className="text-sm text-gray-600">Grade</p>
                <p className="font-semibold text-gray-900">
                  {selectedStudent.grade}
                </p>
              </div>
              <div>
                <p className="text-sm text-gray-600">Current Level</p>
                <p className="font-semibold text-gray-900">
                  Grade {selectedStudent.currentLevel}
                </p>
              </div>
              <div>
                <p className="text-sm text-gray-600">Reading Level</p>
                <p className="font-semibold text-gray-900">
                  Grade {selectedStudent.readingLevel}
                </p>
              </div>
              <div>
                <p className="text-sm text-gray-600">Writing Level</p>
                <p className="font-semibold text-gray-900">
                  Grade {selectedStudent.writingLevel}
                </p>
              </div>
            </div>

            <div>
              <h4 className="font-semibold text-gray-900 mb-2">
                Progress Overview
              </h4>
              <div className="bg-gray-50 p-4 rounded-lg">
                <div className="flex justify-between mb-2">
                  <span className="text-sm text-gray-600">
                    Overall Progress
                  </span>
                  <span className="font-semibold">
                    {selectedStudent.progress}%
                  </span>
                </div>
                <div className="w-full bg-gray-200 rounded-full h-3">
                  <div
                    className="bg-blue-600 h-3 rounded-full"
                    style={{ width: `${selectedStudent.progress}%` }}
                  ></div>
                </div>
              </div>
            </div>

            <div>
              <h4 className="font-semibold text-gray-900 mb-2">
                Recent Activity
              </h4>
              <div className="space-y-2">
                {selectedStudent.recentActivities?.map((activity, index) => (
                  <div
                    key={index}
                    className="flex justify-between items-center p-2 bg-gray-50 rounded"
                  >
                    <span className="text-sm text-gray-700">
                      {activity.title}
                    </span>
                    <span className="text-xs text-gray-500">
                      {activity.date}
                    </span>
                  </div>
                )) || (
                  <p className="text-gray-500 text-sm">No recent activities</p>
                )}
              </div>
            </div>

            <div className="flex gap-2">
              <Button fullWidth variant="primary">
                Assign Assessment
              </Button>
              <Button fullWidth variant="outline">
                View Full Report
              </Button>
            </div>
          </div>
        )}
      </Modal>
    </div>
  );
};

export default StudentsList;
