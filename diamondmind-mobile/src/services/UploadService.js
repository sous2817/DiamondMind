import * as FileSystem from 'expo-file-system/legacy';

const API_URL = "https://diamondmind-backend-yalf.onrender.com"; 

const UploadService = {
    uploadSwingVideo: async (fileUri, jobId, signal) => {
        const url = `${API_URL}/api/videos/upload?job_id=${jobId}`;
        
        try {
            const response = await FileSystem.uploadAsync(url, fileUri, {
                fieldName: 'file',
                httpMethod: 'POST',
                uploadType: 1, // Multipart
            });

            if (response.status >= 200 && response.status < 300) {
                return JSON.parse(response.body);
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