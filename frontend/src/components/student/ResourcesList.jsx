import { useState } from "react";
import Modal from "../common/Modal";

const ResourcesList = ({ resources = [] }) => {
  const [selectedResource, setSelectedResource] = useState(null);
  const [filter, setFilter] = useState("all");

  const filteredResources =
    filter === "all" ? resources : resources.filter((r) => r.type === filter);

  return (
    <div className="space-y-4 sm:space-y-6">
      {/* Filters */}
      <div
        className="rounded-2xl p-4 shadow-sm border"
        style={{ backgroundColor: "#F5EDE5", borderColor: "#C9BDB3" }}
      >
        <div className="flex flex-wrap gap-2">
          {[
            { id: "all", label: "All Resources" },
            { id: "video", label: "Videos" },
            { id: "article", label: "Articles" },
            { id: "exercise", label: "Exercises" },
          ].map((btn) => (
            <button
              key={btn.id}
              onClick={() => setFilter(btn.id)}
              className="px-4 py-2 rounded-lg font-medium transition-all text-xs sm:text-sm shadow-sm"
              style={
                filter === btn.id
                  ? {
                      backgroundColor: "#323232",
                      color: "#DDD0C8",
                    }
                  : {
                      backgroundColor: "#E8DDD3",
                      color: "#5A5A5A",
                      border: "1px solid #C9BDB3",
                    }
              }
            >
              {btn.label}
            </button>
          ))}
        </div>
      </div>

      {/* Resources Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4 sm:gap-6">
        {filteredResources.length > 0 ? (
          filteredResources.map((resource, index) => (
            <div
              key={index}
              onClick={() => setSelectedResource(resource)}
              className="rounded-2xl p-5 shadow-sm border transition-all hover:shadow-md cursor-pointer"
              style={{ backgroundColor: "#F5EDE5", borderColor: "#C9BDB3" }}
            >
              <div className="mb-4 flex gap-2">
                <span
                  className="px-3 py-1 rounded-full text-xs font-semibold"
                  style={{ backgroundColor: "#E8DDD3", color: "#323232" }}
                >
                  {resource.type}
                </span>
                {resource.difficulty && (
                  <span
                    className="px-3 py-1 rounded-full text-xs font-semibold"
                    style={{ backgroundColor: "#DDD0C8", color: "#323232" }}
                  >
                    {resource.difficulty}
                  </span>
                )}
              </div>
              <h3
                className="text-lg font-semibold mb-2"
                style={{ color: "#323232" }}
              >
                {resource.title}
              </h3>
              <p className="text-sm mb-4" style={{ color: "#5A5A5A" }}>
                {resource.description}
              </p>
              <div
                className="flex items-center justify-between text-sm"
                style={{ color: "#5A5A5A" }}
              >
                <span>⏱ {resource.duration}</span>
                <span>📚 {resource.subject}</span>
              </div>
            </div>
          ))
        ) : (
          <div className="col-span-full">
            <div
              className="rounded-2xl p-8 text-center shadow-sm border"
              style={{ backgroundColor: "#F5EDE5", borderColor: "#C9BDB3" }}
            >
              <p style={{ color: "#5A5A5A" }}>No resources found</p>
            </div>
          </div>
        )}
      </div>

      {/* Resource Detail Modal */}
      <Modal
        isOpen={!!selectedResource}
        onClose={() => setSelectedResource(null)}
        title={selectedResource?.title}
        size="lg"
      >
        {selectedResource && (
          <div className="space-y-4">
            <div className="flex gap-2">
              <span
                className="px-3 py-1 rounded-full text-xs font-semibold"
                style={{ backgroundColor: "#E8DDD3", color: "#323232" }}
              >
                {selectedResource.type}
              </span>
              <span
                className="px-3 py-1 rounded-full text-xs font-semibold"
                style={{ backgroundColor: "#DDD0C8", color: "#323232" }}
              >
                {selectedResource.difficulty}
              </span>
            </div>
            <p style={{ color: "#323232" }}>{selectedResource.description}</p>
            <div className="pt-4 border-t" style={{ borderColor: "#C9BDB3" }}>
              <p className="text-sm mb-2" style={{ color: "#5A5A5A" }}>
                <strong style={{ color: "#323232" }}>Subject:</strong>{" "}
                {selectedResource.subject}
              </p>
              <p className="text-sm mb-2" style={{ color: "#5A5A5A" }}>
                <strong style={{ color: "#323232" }}>Duration:</strong>{" "}
                {selectedResource.duration}
              </p>
              <p className="text-sm" style={{ color: "#5A5A5A" }}>
                <strong style={{ color: "#323232" }}>Level:</strong> Grade{" "}
                {selectedResource.level}
              </p>
            </div>
            <button
              className="w-full px-6 py-3 rounded-lg font-medium transition-all shadow-sm hover:shadow-md"
              style={{ backgroundColor: "#323232", color: "#DDD0C8" }}
            >
              Start Learning
            </button>
          </div>
        )}
      </Modal>
    </div>
  );
};

export default ResourcesList;
