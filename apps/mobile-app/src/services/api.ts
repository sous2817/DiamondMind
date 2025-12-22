import { Platform } from 'react-native';

// 10.0.2.2 is required for Android Emulator to see Windows localhost
const DEV_URL = 'http://10.0.2.2:8000';

export const API_BASE_URL = DEV_URL;

export interface HealthResponse {
  status: string;
  message?: string;
}

export const ApiService = {
  checkHealth: async (): Promise<HealthResponse | null> => {
    try {
      console.log(`[DiamondMind] Connecting to: ${API_BASE_URL}/health`);
      const response = await fetch(`${API_BASE_URL}/health`);
      if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
      return await response.json();
    } catch (error) {
      console.error('[DiamondMind] Connection Failed:', error);
      return null;
    }
  },
};