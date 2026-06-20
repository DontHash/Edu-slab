import api from "./api";

const diagnosticService = {
  getInfo: async () => {
    const response = await api.get("/diagnostic/info");
    return response.data;
  },

  getBlueprint: async () => {
    const response = await api.get("/diagnostic/blueprint");
    return response.data;
  },

  startSession: async () => {
    const response = await api.post("/diagnostic/session/start");
    return response.data;
  },

  getCurrentSession: async () => {
    const response = await api.get("/diagnostic/session/current");
    return response.data;
  },

  getTopics: async (skillArea) => {
    const url = skillArea
      ? `/diagnostic/topics/${skillArea}`
      : "/diagnostic/topics";
    const response = await api.get(url);
    return response.data;
  },
};

export default diagnosticService;
