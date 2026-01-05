import * as FileSystem from 'expo-file-system/legacy';
import { Config } from '../config.js';

const UploadService = {
    uploadSwingVideo: async (fileUri, jobId, userId, signal) => {
        // Build URL with job_id and optional user_id
        let url = `${Config.API_BASE_URL}/api/videos/upload?job_id=${jobId}`;
        if (userId) {
            url += `&user_id=${userId}`;
            console.log(`📤 Starting upload for Job ID: ${jobId}, User ID: ${userId}`);
        } else {
            console.log(`📤 Starting upload for Job ID: ${jobId} (no user)`);
        }



        try {
            const response = await FileSystem.uploadAsync(url, fileUri, {
                fieldName: 'file',
                httpMethod: 'POST',
                uploadType: 1, // Tribal Knowledge: Must be Integer 1
                timeout: 600000,
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