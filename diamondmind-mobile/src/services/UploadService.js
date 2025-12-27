import axios from 'axios';

const API_URL = "https://diamondmind-vg35.onrender.com";

const UploadService = {
    // Add an optional 'signal' parameter
    uploadSwingVideo: async (fileUri, signal) => {
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
            const response = await axios.post(`${API_URL}/api/videos/upload`, formData, {
                headers: { 'Content-Type': 'multipart/form-data' },
                timeout: 120000,
                signal: signal, // Pass the cancel signal here
            });
            return response.data;
        } catch (error) {
            if (axios.isCancel(error)) {
                console.log("Request canceled by user");
                return null;
            }
            throw error;
        }
    }
};

export default UploadService;