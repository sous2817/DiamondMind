/**
 * UploadService - Video upload with Supabase authentication (DM-15)
 * Handles video uploads to backend with JWT token authentication.
 */
import * as FileSystem from 'expo-file-system/legacy';
import { Config } from '../config.js';
import { AuthService } from './AuthService';

const UploadService = {
    uploadSwingVideo: async (fileUri, jobId, signal) => {
        // Get access token for authentication
        const accessToken = await AuthService.getAccessToken();

        // Build URL with job_id (user_id extracted from token by backend)
        const url = `${Config.API_BASE_URL}/api/videos/upload?job_id=${jobId}`;

        if (accessToken) {
            console.log(`📤 Starting authenticated upload for Job ID: ${jobId}`);
        } else {
            console.log(`⚠️ Starting upload without authentication for Job ID: ${jobId}`);
        }

        try {
            // Prepare headers with authentication
            const headers = {};
            if (accessToken) {
                headers['Authorization'] = `Bearer ${accessToken}`;
            }

            const response = await FileSystem.uploadAsync(url, fileUri, {
                fieldName: 'file',
                httpMethod: 'POST',
                uploadType: 1, // Tribal Knowledge: Must be Integer 1
                timeout: 600000,
                headers, // Include auth header
            });

            if (response.status >= 200 && response.status < 300) {
                const result = JSON.parse(response.body);

                // ✅ Async pattern: HTTP response confirms upload accepted, result comes via WebSocket
                console.log(`✅ Upload accepted: ${result.status} - Job ${result.job_id}`);

                return result;
            } else {
                // Keep this error throw, as it helps the UI show the specific error message
                throw new Error(`Server Error ${response.status}: ${response.body}`);
            }
        } catch (error) {
            // Keep error logging, but make it concise
            console.error("UploadService Error:", error.message);
            throw error;
        }
    }
};

export default UploadService;