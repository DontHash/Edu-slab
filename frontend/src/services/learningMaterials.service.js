import api from "./api";

const learningMaterialsService = {
  /**
   * Generate personalized learning materials for a subject
   */
  async generateMaterials(subject, forceRegenerate = false) {
    const response = await api.post(
      `/learning-materials/generate/${subject}`,
      null,
      {
        params: { force_regenerate: forceRegenerate },
      }
    );
    return response.data;
  },

  /**
   * Get all learning materials for current user
   */
  async getMyMaterials(subject = null) {
    const params = subject ? { subject } : {};
    const response = await api.get("/learning-materials/my-materials", {
      params,
    });
    return response.data;
  },

  /**
   * Get specific learning material by ID
   */
  async getMaterialById(materialId) {
    const response = await api.get(
      `/learning-materials/materials/${materialId}`
    );
    return response.data;
  },

  /**
   * Archive a learning material
   */
  async archiveMaterial(materialId) {
    const response = await api.delete(
      `/learning-materials/materials/${materialId}`
    );
    return response.data;
  },
};

export default learningMaterialsService;
