import React, { useState } from "react";
import Card from "../common/Card";
import Button from "../common/Button";
import Input from "../common/Input";
import Select from "../common/Select";
import Modal from "../common/Modal";
import Badge from "../common/Badge";

const UserManagement = ({ users = [] }) => {
  const [searchTerm, setSearchTerm] = useState("");
  const [filterRole, setFilterRole] = useState("all");
  const [showAddModal, setShowAddModal] = useState(false);
  const [selectedUser, setSelectedUser] = useState(null);
  const [newUser, setNewUser] = useState({
    name: "",
    email: "",
    role: "student",
    schoolId: "",
  });

  const filteredUsers = users.filter((user) => {
    const matchesSearch =
      user.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      user.email.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesRole = filterRole === "all" || user.role === filterRole;
    return matchesSearch && matchesRole;
  });

  const handleAddUser = () => {
    // API call to add user
    console.log("Adding user:", newUser);
    setShowAddModal(false);
    setNewUser({ name: "", email: "", role: "student", schoolId: "" });
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <h2 className="text-2xl font-bold text-gray-900">User Management</h2>
        <Button onClick={() => setShowAddModal(true)}>Add New User</Button>
      </div>

      {/* Filters */}
      <Card>
        <div className="flex flex-col md:flex-row gap-4">
          <div className="flex-1">
            <Input
              placeholder="Search users..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
            />
          </div>
          <div className="flex gap-2">
            <Button
              variant={filterRole === "all" ? "primary" : "ghost"}
              size="sm"
              onClick={() => setFilterRole("all")}
            >
              All
            </Button>
            <Button
              variant={filterRole === "student" ? "primary" : "ghost"}
              size="sm"
              onClick={() => setFilterRole("student")}
            >
              Students
            </Button>
            <Button
              variant={filterRole === "teacher" ? "primary" : "ghost"}
              size="sm"
              onClick={() => setFilterRole("teacher")}
            >
              Teachers
            </Button>
            <Button
              variant={filterRole === "admin" ? "primary" : "ghost"}
              size="sm"
              onClick={() => setFilterRole("admin")}
            >
              Admins
            </Button>
          </div>
        </div>
      </Card>

      {/* Users Table */}
      <Card title={`Users (${filteredUsers.length})`}>
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-4 py-3 text-left text-sm font-semibold text-gray-900">
                  Name
                </th>
                <th className="px-4 py-3 text-left text-sm font-semibold text-gray-900">
                  Email
                </th>
                <th className="px-4 py-3 text-left text-sm font-semibold text-gray-900">
                  Role
                </th>
                <th className="px-4 py-3 text-left text-sm font-semibold text-gray-900">
                  School
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
              {filteredUsers.length > 0 ? (
                filteredUsers.map((user, index) => (
                  <tr key={index} className="hover:bg-gray-50">
                    <td className="px-4 py-3">
                      <div className="flex items-center space-x-3">
                        <div className="w-8 h-8 rounded-full bg-blue-500 flex items-center justify-center text-white text-sm font-semibold">
                          {user.name.charAt(0)}
                        </div>
                        <span className="font-medium text-gray-900">
                          {user.name}
                        </span>
                      </div>
                    </td>
                    <td className="px-4 py-3 text-gray-700">{user.email}</td>
                    <td className="px-4 py-3">
                      <Badge
                        variant={
                          user.role === "admin"
                            ? "danger"
                            : user.role === "teacher"
                            ? "primary"
                            : "success"
                        }
                      >
                        {user.role}
                      </Badge>
                    </td>
                    <td className="px-4 py-3 text-gray-700">
                      {user.schoolName || "-"}
                    </td>
                    <td className="px-4 py-3">
                      <Badge
                        variant={
                          user.status === "active" ? "success" : "warning"
                        }
                      >
                        {user.status}
                      </Badge>
                    </td>
                    <td className="px-4 py-3">
                      <Button
                        size="sm"
                        variant="ghost"
                        onClick={() => setSelectedUser(user)}
                      >
                        View
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
                    No users found
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </Card>

      {/* Add User Modal */}
      <Modal
        isOpen={showAddModal}
        onClose={() => setShowAddModal(false)}
        title="Add New User"
        size="md"
      >
        <div className="space-y-4">
          <Input
            label="Full Name"
            value={newUser.name}
            onChange={(e) => setNewUser({ ...newUser, name: e.target.value })}
            required
          />
          <Input
            label="Email"
            type="email"
            value={newUser.email}
            onChange={(e) => setNewUser({ ...newUser, email: e.target.value })}
            required
          />
          <Select
            label="Role"
            value={newUser.role}
            onChange={(e) => setNewUser({ ...newUser, role: e.target.value })}
            options={[
              { value: "student", label: "Student" },
              { value: "teacher", label: "Teacher" },
              { value: "admin", label: "Admin" },
            ]}
            required
          />
          <Input
            label="School ID"
            value={newUser.schoolId}
            onChange={(e) =>
              setNewUser({ ...newUser, schoolId: e.target.value })
            }
            placeholder="Optional"
          />
          <div className="flex gap-2 pt-4">
            <Button
              variant="outline"
              onClick={() => setShowAddModal(false)}
              fullWidth
            >
              Cancel
            </Button>
            <Button onClick={handleAddUser} fullWidth>
              Add User
            </Button>
          </div>
        </div>
      </Modal>

      {/* User Details Modal */}
      <Modal
        isOpen={!!selectedUser}
        onClose={() => setSelectedUser(null)}
        title="User Details"
        size="lg"
      >
        {selectedUser && (
          <div className="space-y-6">
            <div className="grid grid-cols-2 gap-4">
              <div>
                <p className="text-sm text-gray-600">Name</p>
                <p className="font-semibold text-gray-900">
                  {selectedUser.name}
                </p>
              </div>
              <div>
                <p className="text-sm text-gray-600">Email</p>
                <p className="font-semibold text-gray-900">
                  {selectedUser.email}
                </p>
              </div>
              <div>
                <p className="text-sm text-gray-600">Role</p>
                <Badge
                  variant={
                    selectedUser.role === "admin"
                      ? "danger"
                      : selectedUser.role === "teacher"
                      ? "primary"
                      : "success"
                  }
                >
                  {selectedUser.role}
                </Badge>
              </div>
              <div>
                <p className="text-sm text-gray-600">Status</p>
                <Badge
                  variant={
                    selectedUser.status === "active" ? "success" : "warning"
                  }
                >
                  {selectedUser.status}
                </Badge>
              </div>
              <div>
                <p className="text-sm text-gray-600">School</p>
                <p className="font-semibold text-gray-900">
                  {selectedUser.schoolName || "Not assigned"}
                </p>
              </div>
              <div>
                <p className="text-sm text-gray-600">Joined Date</p>
                <p className="font-semibold text-gray-900">
                  {selectedUser.joinedDate || "-"}
                </p>
              </div>
            </div>

            <div className="flex gap-2">
              <Button fullWidth variant="primary">
                Edit User
              </Button>
              <Button fullWidth variant="outline">
                Reset Password
              </Button>
              <Button fullWidth variant="danger">
                {selectedUser.status === "active" ? "Deactivate" : "Activate"}
              </Button>
            </div>
          </div>
        )}
      </Modal>
    </div>
  );
};

export default UserManagement;
