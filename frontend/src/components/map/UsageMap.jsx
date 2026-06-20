import { useEffect, useState } from "react";
import api from "../../services/api";

/**
 * UsageMap Component
 * Displays a visual map showing the distribution of users accessing the service
 */
const UsageMap = () => {
  const [userLocations, setUserLocations] = useState([]);
  const [loading, setLoading] = useState(true);
  const [mapInitialized, setMapInitialized] = useState(false);

  useEffect(() => {
    fetchUserLocations();
  }, []);

  const fetchUserLocations = async () => {
    try {
      const response = await api.get("/api/users/locations");
      setUserLocations(response.data.locations || []);
    } catch (error) {
      console.error("Failed to fetch user locations:", error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (!loading && userLocations.length > 0 && !mapInitialized) {
      initializeMap();
    }
  }, [loading, userLocations, mapInitialized]);

  const initializeMap = () => {
    if (!window.L) {
      console.error("Leaflet not loaded");
      return;
    }

    // Initialize map centered on average of all locations
    const avgLat =
      userLocations.reduce((sum, loc) => sum + loc.latitude, 0) /
      userLocations.length;
    const avgLng =
      userLocations.reduce((sum, loc) => sum + loc.longitude, 0) /
      userLocations.length;

    const map = window.L.map("usage-map").setView([avgLat, avgLng], 6);

    // Add OpenStreetMap tiles
    window.L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
      attribution:
        '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
      maxZoom: 19,
    }).addTo(map);

    // Group locations by city to show counts
    const locationCounts = {};
    userLocations.forEach((loc) => {
      const key = `${loc.latitude.toFixed(2)},${loc.longitude.toFixed(2)}`;
      if (!locationCounts[key]) {
        locationCounts[key] = {
          latitude: loc.latitude,
          longitude: loc.longitude,
          location: loc.location,
          count: 0,
        };
      }
      locationCounts[key].count += 1;
    });

    // Add markers for each location with user count
    Object.values(locationCounts).forEach((loc) => {
      const marker = window.L.marker([loc.latitude, loc.longitude]).addTo(map);

      const popupContent = `
        <div style="text-align: center;">
          <strong style="color: #323232;">${loc.location}</strong><br/>
          <span style="color: #5A5A5A; font-size: 12px;">${loc.count} ${
        loc.count === 1 ? "user" : "users"
      }</span>
        </div>
      `;

      marker.bindPopup(popupContent);
    });

    setMapInitialized(true);
  };

  if (loading) {
    return (
      <div className="text-center py-8">
        <div
          className="inline-block animate-spin rounded-full h-8 w-8 border-b-2"
          style={{ borderColor: "#323232" }}
        ></div>
      </div>
    );
  }

  if (userLocations.length === 0) {
    return (
      <div className="text-center py-8">
        <p className="text-sm" style={{ color: "#5A5A5A" }}>
          No user location data available yet
        </p>
      </div>
    );
  }

  return (
    <div>
      <p className="text-sm mb-4" style={{ color: "#5A5A5A" }}>
        See where students are using our service across different locations
      </p>
      <div
        id="usage-map"
        className="h-64 rounded-lg border"
        style={{ borderColor: "#C9BDB3" }}
      ></div>
      <div className="mt-3 text-xs text-center" style={{ color: "#5A5A5A" }}>
        Total active users: {userLocations.length}
      </div>
    </div>
  );
};

export default UsageMap;
