import AsyncStorage from '@react-native-async-storage/async-storage';
import axios from 'axios';
import { Config } from '../config';

const USER_SESSION_KEY = 'user_session';

export const AuthService = {
    /**
     * Sign up a new user
     * @param {string} email - User email
     * @param {string} username - User username
     * @returns {Promise<Object>} User object
     */
    async signup(email, username) {
        try {
            const response = await axios.post(
                `${Config.API_BASE_URL}/api/users`,
                null,
                { params: { email, username } }
            );

            const user = response.data;
            await this.saveUserSession(user);
            console.log('✅ Signup successful:', user);
            return user;
        } catch (error) {
            console.error('❌ Signup failed:', error.response?.data || error.message);
            throw error;
        }
    },

    /**
     * Login existing user by email
     * @param {string} email - User email
     * @returns {Promise<Object>} User object
     */
    async login(email) {
        try {
            const response = await axios.get(
                `${Config.API_BASE_URL}/api/auth/login`,
                { params: { email } }
            );

            const user = response.data;
            await this.saveUserSession(user);
            console.log('✅ Login successful:', user);
            return user;
        } catch (error) {
            console.error('❌ Login failed:', error.response?.data || error.message);
            throw error;
        }
    },

    /**
     * Logout current user
     */
    async logout() {
        try {
            await AsyncStorage.removeItem(USER_SESSION_KEY);
            console.log('✅ Logout successful');
        } catch (error) {
            console.error('❌ Logout failed:', error);
            throw error;
        }
    },

    /**
     * Get current user from AsyncStorage
     * @returns {Promise<Object|null>} User object or null
     */
    async getCurrentUser() {
        try {
            const userData = await AsyncStorage.getItem(USER_SESSION_KEY);
            if (userData) {
                const user = JSON.parse(userData);
                console.log('📱 Loaded user from storage:', user.username);
                return user;
            }
            console.log('📱 No user session found');
            return null;
        } catch (error) {
            console.error('❌ Failed to load user:', error);
            return null;
        }
    },

    /**
     * Save user session to AsyncStorage
     * @param {Object} user - User object
     */
    async saveUserSession(user) {
        try {
            await AsyncStorage.setItem(USER_SESSION_KEY, JSON.stringify(user));
            console.log('💾 User session saved');
        } catch (error) {
            console.error('❌ Failed to save user session:', error);
            throw error;
        }
    }
};
