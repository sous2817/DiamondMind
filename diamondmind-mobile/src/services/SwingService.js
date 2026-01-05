import axios from 'axios';
import { Config } from '../config';

export const SwingService = {
    /**
     * Get all swings for a user
     * @param {number} userId - User ID
     * @returns {Promise<Array>} Array of swing objects
     */
    async getUserSwings(userId) {
        try {
            const response = await axios.get(
                `${Config.API_BASE_URL}/api/users/${userId}/swings`
            );
            console.log(`✅ Fetched ${response.data.length} swings for user ${userId}`);
            return response.data;
        } catch (error) {
            console.error('❌ Failed to fetch swings:', error.response?.data || error.message);
            throw error;
        }
    },

    /**
     * Get analysis result for a swing
     * @param {number} swingId - Swing ID
     * @returns {Promise<Object>} Analysis result object
     */
    async getSwingAnalysis(swingId) {
        try {
            const response = await axios.get(
                `${Config.API_BASE_URL}/api/swings/${swingId}/analysis`
            );
            console.log(`✅ Fetched analysis for swing ${swingId}`);
            return response.data;
        } catch (error) {
            console.error('❌ Failed to fetch analysis:', error.response?.data || error.message);
            throw error;
        }
    }
};
