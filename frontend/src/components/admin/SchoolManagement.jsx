import React, { useState } from "react";
import Card from "../common/Card";
import Button from "../common/Button";
import Input from "../common/Input";
import Modal from "../common/Modal";
import Badge from "../common/Badge";

const SchoolManagement = ({ schools = [] }) => {
  const [searchTerm, setSearchTerm] = useState("");
  const [showAddModal, setShowAddModal] = useState(false);
  const [selectedSchool, setSelectedSchool] = useState(null);
  const [newSchool, setNewSchool] = useState({
    name: "",
    address: "",
    contactEmail: "",
    contactPhone: "",
    principalName: "",
  });

  const filteredSchools = schools.filter((school) =>
    school.name.toLowerCase().includes(searchTerm.toLowerCase())
  );

  const handleAddSchool = () => {
    // API call to add school
    console.log("Adding school:", newSchool);
    setShowAddModal(false);
    setNewSchool({
      name: "",
      address: "",
      contactEmail: "",
      contactPhone: "",
      principalName: "",
    });
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <h2 className="text-2xl font-bold text-gray-900">School Management</h2>
        <Button onClick={() => setShowAddModal(true)}>Add New School</Button>
      </div>

      {/* Search */}
      <Card>
        <Input
          placeholder="Search schools..."
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
        />
      </Card>

      {/* Schools Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {filteredSchools.length > 0 ? (
          filteredSchools.map((school, index) => (
            <Card
              key={index}
              hoverable
              onClick={() => setSelectedSchool(school)}
            >
              <div className="flex items-start justify-between mb-4">
                <div className="w-12 h-12 bg-blue-500 rounded-lg flex items-center justify-center text-2xl">
                  🏫
                </div>
                <Badge
                  variant={school.status === "active" ? "success" : "warning"}
                >
                  {school.status}
                </Badge>
              </div>
              <h3 className="text-lg font-semibold text-gray-900 mb-2">
                {school.name}
              </h3>
              <p className="text-sm text-gray-600 mb-4">{school.address}</p>
              <div className="space-y-2 text-sm text-gray-600">
                <div className="flex justify-between">
                  <span>Students:</span>
                  <span className="font-semibold">{school.totalStudents}</span>
                </div>
                <div className="flex justify-between">
                  <span>Teachers:</span>
                  <span className="font-semibold">{school.totalTeachers}</span>
                </div>
              </div>
            </Card>
          ))
        ) : (
          <div className="col-span-full">
            <Card>
              <p className="text-center text-gray-500 py-8">No schools found</p>
            </Card>
          </div>
        )}
      </div>

      {/* Add School Modal */}
      <Modal
        isOpen={showAddModal}
        onClose={() => setShowAddModal(false)}
        title="Add New School"
        size="md"
      >
        <div className="space-y-4">
          <Input
            label="School Name"
            value={newSchool.name}
            onChange={(e) =>
              setNewSchool({ ...newSchool, name: e.target.value })
            }
            required
          />
          <Input
            label="Address"
            value={newSchool.address}
            onChange={(e) =>
              setNewSchool({ ...newSchool, address: e.target.value })
            }
            required
          />
          <Input
            label="Contact Email"
            type="email"
            value={newSchool.contactEmail}
            onChange={(e) =>
              setNewSchool({ ...newSchool, contactEmail: e.target.value })
            }
            required
          />
          <Input
            label="Contact Phone"
            type="tel"
            value={newSchool.contactPhone}
            onChange={(e) =>
              setNewSchool({ ...newSchool, contactPhone: e.target.value })
            }
            required
          />
          <Input
            label="Principal Name"
            value={newSchool.principalName}
            onChange={(e) =>
              setNewSchool({ ...newSchool, principalName: e.target.value })
            }
            required
          />
          <div className="flex gap-2 pt-4">
            <Button
              variant="outline"
              onClick={() => setShowAddModal(false)}
              fullWidth
            >
              Cancel
            </Button>
            <Button onClick={handleAddSchool} fullWidth>
              Add School
            </Button>
          </div>
        </div>
      </Modal>

      {/* School Details Modal */}
      <Modal
        isOpen={!!selectedSchool}
        onClose={() => setSelectedSchool(null)}
        title={selectedSchool?.name}
        size="lg"
      >
        {selectedSchool && (
          <div className="space-y-6">
            <div className="grid grid-cols-2 gap-4">
              <div>
                <p className="text-sm text-gray-600">Address</p>
                <p className="font-semibold text-gray-900">
                  {selectedSchool.address}
                </p>
              </div>
              <div>
                <p className="text-sm text-gray-600">Status</p>
                <Badge
                  variant={
                    selectedSchool.status === "active" ? "success" : "warning"
                  }
                >
                  {selectedSchool.status}
                </Badge>
              </div>
              <div>
                <p className="text-sm text-gray-600">Total Students</p>
                <p className="font-semibold text-gray-900">
                  {selectedSchool.totalStudents}
                </p>
              </div>
              <div>
                <p className="text-sm text-gray-600">Total Teachers</p>
                <p className="font-semibold text-gray-900">
                  {selectedSchool.totalTeachers}
                </p>
              </div>
              <div>
                <p className="text-sm text-gray-600">Contact Email</p>
                <p className="font-semibold text-gray-900">
                  {selectedSchool.contactEmail}
                </p>
              </div>
              <div>
                <p className="text-sm text-gray-600">Contact Phone</p>
                <p className="font-semibold text-gray-900">
                  {selectedSchool.contactPhone}
                </p>
              </div>
            </div>

            <div className="flex gap-2">
              <Button fullWidth variant="primary">
                Edit School
              </Button>
              <Button fullWidth variant="outline">
                View Details
              </Button>
              <Button fullWidth variant="danger">
                Deactivate
              </Button>
            </div>
          </div>
        )}
      </Modal>
    </div>
  );
};

export default SchoolManagement;
