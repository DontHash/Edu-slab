import { useEffect, useRef, useState } from "react";

const LocationMap = ({ onLocationSelect, initialLocation }) => {
  const mapRef = useRef(null);
  const [map, setMap] = useState(null);
  const [marker, setMarker] = useState(null);
  const [searchQuery, setSearchQuery] = useState("");
  const [isSearching, setIsSearching] = useState(false);

  useEffect(() => {
    // Load Leaflet CSS and JS dynamically
    if (!document.getElementById("leaflet-css")) {
      const link = document.createElement("link");
      link.id = "leaflet-css";
      link.rel = "stylesheet";
      link.href = "https://unpkg.com/leaflet@1.9.4/dist/leaflet.css";
      document.head.appendChild(link);
    }

    const loadMap = async () => {
      // Wait for Leaflet to load
      if (!window.L) {
        const script = document.createElement("script");
        script.src = "https://unpkg.com/leaflet@1.9.4/dist/leaflet.js";
        script.async = true;
        document.body.appendChild(script);
        await new Promise((resolve) => {
          script.onload = resolve;
        });
      }

      if (mapRef.current && !map) {
        // Default to India center
        const defaultLat = initialLocation?.lat || 20.5937;
        const defaultLng = initialLocation?.lng || 78.9629;

        const newMap = window.L.map(mapRef.current).setView(
          [defaultLat, defaultLng],
          initialLocation ? 13 : 5
        );

        window.L.tileLayer(
          "https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png",
          {
            attribution: "© OpenStreetMap contributors",
            maxZoom: 19,
          }
        ).addTo(newMap);

        // Add click handler
        newMap.on("click", (e) => {
          const { lat, lng } = e.latlng;
          updateMarker(newMap, lat, lng);

          // Reverse geocode to get city name
          fetch(
            `https://nominatim.openstreetmap.org/reverse?format=json&lat=${lat}&lon=${lng}`
          )
            .then((res) => res.json())
            .then((data) => {
              const city =
                data.address.city ||
                data.address.town ||
                data.address.village ||
                data.address.state;
              onLocationSelect({
                latitude: lat,
                longitude: lng,
                location: city || `${lat.toFixed(4)}, ${lng.toFixed(4)}`,
              });
            })
            .catch(() => {
              onLocationSelect({
                latitude: lat,
                longitude: lng,
                location: `${lat.toFixed(4)}, ${lng.toFixed(4)}`,
              });
            });
        });

        // Add initial marker if location provided
        if (initialLocation?.lat && initialLocation?.lng) {
          const newMarker = window.L.marker([
            initialLocation.lat,
            initialLocation.lng,
          ]).addTo(newMap);
          setMarker(newMarker);
        }

        setMap(newMap);
      }
    };

    loadMap();

    return () => {
      if (map) {
        map.remove();
      }
    };
  }, []);

  const updateMarker = (mapInstance, lat, lng) => {
    if (marker) {
      marker.setLatLng([lat, lng]);
    } else {
      const newMarker = window.L.marker([lat, lng]).addTo(mapInstance);
      setMarker(newMarker);
    }
  };

  const handleSearch = async () => {
    if (!searchQuery.trim() || !map) return;

    setIsSearching(true);
    try {
      const response = await fetch(
        `https://nominatim.openstreetmap.org/search?format=json&q=${encodeURIComponent(
          searchQuery
        )}`
      );
      const data = await response.json();

      if (data && data.length > 0) {
        const { lat, lon, display_name } = data[0];
        const latitude = parseFloat(lat);
        const longitude = parseFloat(lon);

        map.setView([latitude, longitude], 13);
        updateMarker(map, latitude, longitude);

        onLocationSelect({
          latitude,
          longitude,
          location: display_name.split(",")[0] || searchQuery,
        });
      } else {
        alert("Location not found. Try a different search.");
      }
    } catch (error) {
      console.error("Search error:", error);
      alert("Failed to search location. Try again.");
    } finally {
      setIsSearching(false);
    }
  };

  return (
    <div className="space-y-3">
      {/* Search Bar */}
      <div className="flex gap-2">
        <input
          type="text"
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          onKeyPress={(e) => e.key === "Enter" && handleSearch()}
          placeholder="Search city or location..."
          className="flex-1 px-4 py-2 border rounded-lg focus:ring-2 focus:border-transparent"
          style={{ borderColor: "#C9BDB3", backgroundColor: "#F5EDE5" }}
        />
        <button
          onClick={handleSearch}
          disabled={isSearching}
          className="px-6 py-2 text-white rounded-lg font-medium transition-colors disabled:opacity-50 hover:opacity-90"
          style={{ backgroundColor: "#323232" }}
        >
          {isSearching ? "..." : "Search"}
        </button>
      </div>

      {/* Map Container */}
      <div
        ref={mapRef}
        className="w-full h-64 rounded-xl border-2 border-gray-300 overflow-hidden"
        style={{ minHeight: "256px" }}
      />

      <p className="text-sm text-gray-600">
        🗺️ Click anywhere on the map to set your location, or search for your
        city above
      </p>
    </div>
  );
};

export default LocationMap;
