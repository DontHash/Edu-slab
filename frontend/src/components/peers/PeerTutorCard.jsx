import Badge from "../common/Badge";

const PeerTutorCard = ({ peer, onRequestHelp }) => {
  return (
    <div className="p-4 border border-[#C9BDB3] rounded-lg hover:border-[#5A5A5A] hover:shadow-sm transition">
      <div className="flex items-start space-x-3 mb-3">
        {/* Avatar */}
        <div className="w-12 h-12 rounded-full bg-[#E8DDD3] flex items-center justify-center text-[#323232] font-bold text-lg flex-shrink-0 border border-[#C9BDB3]">
          {peer.name.charAt(0)}
        </div>

        {/* Info */}
        <div className="flex-1 min-w-0">
          <h4 className="font-semibold text-gray-900 truncate">{peer.name}</h4>
          <p className="text-sm text-gray-600">Grade {peer.grade}</p>
          {peer.email && (
            <a
              href={`mailto:${peer.email}`}
              className="text-xs text-blue-600 hover:text-blue-800 truncate block"
              title={peer.email}
            >
              ✉️ {peer.email}
            </a>
          )}
          {peer.location && (
            <p className="text-xs text-gray-500 mt-1">📍 {peer.location}</p>
          )}
        </div>

        {/* Status Badge */}
        <Badge
          variant={peer.availability === "Online now" ? "success" : "secondary"}
        >
          {peer.availability || "Offline"}
        </Badge>
      </div>

      {/* Can Help With */}
      <div className="mb-3">
        <p className="text-xs font-medium text-gray-600 mb-2">Can help with:</p>
        <div className="flex flex-wrap gap-2">
          {peer.can_help_with?.map((topic, idx) => (
            <span
              key={idx}
              className="px-2 py-1 bg-[#F5EDE5] text-[#323232] text-xs rounded-full border border-[#C9BDB3]"
            >
              {topic}
            </span>
          ))}
        </div>
      </div>

      {/* Scores */}
      {peer.their_scores && (
        <div className="mb-3 p-2 bg-[#F5EDE5] border border-[#C9BDB3] rounded">
          <p className="text-xs text-[#323232]">
            <strong>Their scores:</strong>{" "}
            {Object.entries(peer.their_scores).map(([topic, score], idx) => (
              <span key={idx}>
                {topic}: {score}%
                {idx < Object.entries(peer.their_scores).length - 1 ? ", " : ""}
              </span>
            ))}
          </p>
        </div>
      )}

      {/* Match Reason */}
      {peer.match_reason && (
        <div className="mb-3 p-2 bg-[#E8DDD3] border border-[#C9BDB3] rounded">
          <p className="text-xs text-[#323232]">
            <strong>Why matched:</strong> {peer.match_reason}
          </p>
        </div>
      )}

      {/* Action Button */}
      <a
        href={`mailto:${peer.email}?subject=Request for Help - ${peer.subject}`}
        className="block w-full px-4 py-2 bg-[#323232] text-white rounded-lg hover:bg-[#5A5A5A] transition text-sm font-medium text-center"
      >
        Send Email
      </a>
    </div>
  );
};

export default PeerTutorCard;
