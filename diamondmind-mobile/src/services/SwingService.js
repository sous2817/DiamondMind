import axios from 'axios';
import { Config } from '../config';
import { AuthService } from './AuthService';

export const SwingService = {
    /**
     * Get all swings for the authenticated user
     * @returns {Promise<Array>} Array of swing objects
     */
    async getUserSwings() {
        try {
            const accessToken = await AuthService.getAccessToken();

            const response = await axios.get(
                `${Config.API_BASE_URL}/api/swings`,
                {
                    headers: {
                        'Authorization': `Bearer ${accessToken}`
                    }
                }
            );
            console.log(`✅ Fetched ${response.data.length} swings`);
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
    },

    /**
     * Update swing title and/or notes (DM-57)
     * @param {number} swingId - Swing ID
     * @param {string} title - New title (optional)
     * @param {string} notes - New notes (optional)
     * @returns {Promise<Object>} Updated swing object
     */
    async updateSwing(swingId, title, notes) {
        try {
            const params = new URLSearchParams();
            if (title !== undefined && title !== null) {
                params.append('title', title);
            }
            if (notes !== undefined && notes !== null) {
                params.append('notes', notes);
            }

            const response = await axios.patch(
                `${Config.API_BASE_URL}/api/swings/${swingId}?${params.toString()}`
            );
            console.log(`✅ Updated swing ${swingId}`);
            return response.data;
        } catch (error) {
            console.error('❌ Failed to update swing:', error.response?.data || error.message);
            throw error;
        }
    },

    /**
     * Delete a swing (DM-57)
     * @param {number} swingId - Swing ID
     * @returns {Promise<Object>} Delete confirmation
     */
    async deleteSwing(swingId) {
        try {
            const response = await axios.delete(
                `${Config.API_BASE_URL}/api/swings/${swingId}`
            );
            console.log(`✅ Deleted swing ${swingId}`);
            return response.data;
        } catch (error) {
            console.error('❌ Failed to delete swing:', error.response?.data || error.message);
            throw error;
        }
    }
};
