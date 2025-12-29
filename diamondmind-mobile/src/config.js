// Single Source of Truth for API URLs
// Change this ONE place to update both WebSocket and HTTP connections.

const LIVE_BACKEND_URL = "diamondmind-backend-yalf.onrender.com";

export const Config = {
    // HTTP URL (e.g., https://diamondmind-backend-yalf.onrender.com)
    API_BASE_URL: `https://${LIVE_BACKEND_URL}`,

    // WebSocket URL (e.g., wss://diamondmind-backend-yalf.onrender.com)
    WS_BASE_URL: `wss://${LIVE_BACKEND_URL}`,
};