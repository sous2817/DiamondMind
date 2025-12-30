import * as FileSystem from 'expo-file-system/legacy';
import { Config } from '../config.js';

const UploadService = {
    uploadSwingVideo: async (fileUri, jobId, signal) => {
        const url = `${Config.API_BASE_URL}/api/videos/upload?job_id=${jobId}`;

        // 🚀 RESTORED: Terminal notification for start
        console.log(`📤 Starting upload for Job ID: ${jobId}`);

        try {
            const response = await FileSystem.uploadAsync(url, fileUri, {
                fieldName: 'file',
                httpMethod: 'POST',
                uploadType: 1, // Tribal Knowledge: Must be Integer 1
                timeout: 120000,
            });

            if (response.status >= 200 && response.status < 300) {
                const result = JSON.parse(response.body);

                // ✅ RESTORED: Terminal notification for success (matches Sec 14)
                console.log(`✅ Analysis complete: { totalFrames: ${result.total_frames}, framesWithPerson: ${result.frames_with_person} }`);

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