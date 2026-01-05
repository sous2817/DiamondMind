import React, { createContext, useState, useEffect } from 'react';
import { AuthService } from '../services/AuthService';

export const UserContext = createContext();

export const UserProvider = ({ children }) => {
    const [user, setUser] = useState(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        loadUser();
    }, []);

    const loadUser = async () => {
        console.log('🔄 Loading user session...');
        const savedUser = await AuthService.getCurrentUser();
        setUser(savedUser);
        setLoading(false);
        console.log('✅ User context initialized:', savedUser ? savedUser.username : 'No user');
    };

    const login = async (email) => {
        const user = await AuthService.login(email);
        setUser(user);
        return user;
    };

    const signup = async (email, username) => {
        const user = await AuthService.signup(email, username);
        setUser(user);
        return user;
    };

    const logout = async () => {
        await AuthService.logout();
        setUser(null);
    };

    return (
        <UserContext.Provider value={{ user, setUser, loading, login, signup, logout }}>
            {children}
        </UserContext.Provider>
    );
};
