import { useState } from "react";
import Button from "../common/Button";

const HelpRequestModal = ({ peer, type = "request", onClose, onSubmit }) => {
  const [message, setMessage] = useState("");
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);

    try {
      await onSubmit({ peer_id: peer.id, message });
      onClose();
    } catch (error) {
      console.error("Failed to send request:", error);
      setLoading(false);
    }
  };

  return (
    <div
      className="fixed inset-0 flex items-center justify-center p-4 z-50"
      style={{ backgroundColor: "rgba(50, 50, 50, 0.5)" }}
    >
      <div
        className="rounded-lg max-w-md w-full p-6"
        style={{ backgroundColor: "#F5EDE5", border: "1px solid #C9BDB3" }}
      >
        <h3 className="text-xl font-bold mb-4" style={{ color: "#323232" }}>
          {type === "request" ? "Request Help" : "Offer Help"} - {peer.name}
        </h3>

        <div className="mb-4">
          <div className="flex items-center space-x-3 mb-3">
            <div className="w-12 h-12 rounded-full bg-[#E8DDD3] flex items-center justify-center text-[#323232] font-bold text-lg border border-[#C9BDB3]">
              {peer.name.charAt(0)}
            </div>
            <div>
              <p className="font-semibold text-gray-900">{peer.name}</p>
              <p className="text-sm text-gray-600">Grade {peer.grade}</p>
            </div>
          </div>

          {type === "request" && peer.can_help_with && (
            <div className="p-3 bg-[#F5EDE5] border border-[#C9BDB3] rounded-lg mb-3">
              <p className="text-sm text-[#323232]">
                <strong>Can help with:</strong> {peer.can_help_with.join(", ")}
              </p>
            </div>
          )}

          {type === "offer" && peer.needs_help_with && (
            <div className="p-3 bg-[#F5EDE5] border border-[#C9BDB3] rounded-lg mb-3">
              <p className="text-sm text-[#323232]">
                <strong>Needs help with:</strong>{" "}
                {Array.isArray(peer.needs_help_with)
                  ? peer.needs_help_with.join(", ")
                  : peer.needs_help_with}
              </p>
            </div>
          )}
        </div>

        <form onSubmit={handleSubmit}>
          <div className="mb-4">
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Message (optional)
            </label>
            <textarea
              value={message}
              onChange={(e) => setMessage(e.target.value)}
              placeholder={
                type === "request"
                  ? "Hi! I need help with... Can you explain...?"
                  : "Hi! I'd be happy to help you with... Let me know when you're free!"
              }
              rows={4}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />
          </div>

          <div className="flex space-x-3">
            <Button
              type="button"
              variant="secondary"
              onClick={onClose}
              fullWidth
            >
              Cancel
            </Button>
            <Button type="submit" loading={loading} fullWidth>
              {type === "request" ? "Send Request" : "Send Offer"}
            </Button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default HelpRequestModal;
