import axios from 'axios';

const API_URL = "https://diamondmind-vg35.onrender.com";

const UploadService = {
    uploadSwingVideo: async (fileUri, jobId, signal) => {
        const formData = new FormData();
        const filename = fileUri.split('/').pop();
        const match = /\.(\w+)$/.exec(filename);
        const type = match ? `video/${match[1]}` : `video/mp4`;

        formData.append('file', {
            uri: fileUri,
            name: filename,
            type: type,
        });

        try {
            // Send the jobId as a query parameter so the backend knows who to pulse
            const response = await axios.post(`${API_URL}/api/videos/upload?job_id=${jobId}`, formData, {
                headers: { 'Content-Type': 'multipart/form-data' },
                timeout: 120000,
                signal: signal,
            });
            return response.data;
        } catch (error) {
            if (axios.isCancel(error)) return null;
            throw error;
        }
    }
};

export default UploadService;