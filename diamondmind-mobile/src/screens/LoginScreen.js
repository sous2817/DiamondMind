import React, { useState, useContext } from 'react';
import { View, Text, TextInput, TouchableOpacity, StyleSheet, ActivityIndicator, KeyboardAvoidingView, Platform, Alert } from 'react-native';
import { UserContext } from '../context/UserContext';
import { LogIn, Eye, EyeOff } from 'lucide-react-native';
import { supabase } from '../config/supabaseConfig';

const THEME = {
    bg: '#F8F9FA',
    card: '#FFFFFF',
    primary: '#0F172A',
    accent: '#2563EB',
    error: '#EF4444',
    subtext: '#64748B',
    border: '#E2E8F0'
};

export default function LoginScreen({ navigation }) {
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState('');
    const [showPassword, setShowPassword] = useState(false);
    const { login } = useContext(UserContext);

    const handleLogin = async () => {
        if (!email.trim()) {
            setError('Please enter your email');
            return;
        }

        if (!password) {
            setError('Please enter your password');
            return;
        }

        setLoading(true);
        setError('');

        try {
            await login(email.trim().toLowerCase(), password);
            // Navigation handled by App.js conditional rendering
        } catch (err) {
            console.error('Login error:', err);
            setError(err.message || 'Invalid email or password');
        } finally {
            setLoading(false);
        }
    };

    const handleForgotPassword = async () => {
        if (!email.trim()) {
            Alert.alert('Email Required', 'Please enter your email address to reset your password.');
            return;
        }

        try {
            const { error } = await supabase.auth.resetPasswordForEmail(email.trim().toLowerCase(), {
                redirectTo: 'https://diamondmind.app/reset-password', // Update with your actual URL
            });

            if (error) throw error;

            Alert.alert(
                'Check Your Email',
                `We've sent a password reset link to ${email.trim()}. Please check your inbox.`,
                [{ text: 'OK' }]
            );
        } catch (err) {
            console.error('Password reset error:', err);
            Alert.alert('Error', err.message || 'Failed to send reset email. Please try again.');
        }
    };

    return (
        <KeyboardAvoidingView
            style={styles.container}
            behavior={Platform.OS === 'ios' ? 'padding' : 'height'}
        >
            <View style={styles.content}>
                {/* Header */}
                <View style={styles.header}>
                    <View style={styles.iconCircle}>
                        <LogIn size={32} color={THEME.accent} />
                    </View>
                    <Text style={styles.title}>Welcome Back</Text>
                    <Text style={styles.subtitle}>Sign in to access your swing history</Text>
                </View>

                {/* Form */}
                <View style={styles.form}>
                    <TextInput
                        style={styles.input}
                        placeholder="Email"
                        placeholderTextColor={THEME.subtext}
                        value={email}
                        onChangeText={setEmail}
                        autoCapitalize="none"
                        keyboardType="email-address"
                        editable={!loading}
                    />

                    <View style={styles.passwordContainer}>
                        <TextInput
                            style={styles.passwordInput}
                            placeholder="Password"
                            placeholderTextColor={THEME.subtext}
                            value={password}
                            onChangeText={setPassword}
                            secureTextEntry={!showPassword}
                            autoCapitalize="none"
                            editable={!loading}
                        />
                        <TouchableOpacity
                            style={styles.eyeIcon}
                            onPress={() => setShowPassword(!showPassword)}
                        >
                            {showPassword ? (
                                <Eye size={20} color={THEME.subtext} />
                            ) : (
                                <EyeOff size={20} color={THEME.subtext} />
                            )}
                        </TouchableOpacity>
                    </View>

                    <TouchableOpacity
                        style={styles.forgotPasswordButton}
                        onPress={handleForgotPassword}
                        disabled={loading}
                    >
                        <Text style={styles.forgotPasswordText}>Forgot Password?</Text>
                    </TouchableOpacity>

                    {error ? (
                        <Text style={styles.errorText}>{error}</Text>
                    ) : null}

                    <TouchableOpacity
                        style={[styles.button, loading && styles.buttonDisabled]}
                        onPress={handleLogin}
                        disabled={loading}
                    >
                        {loading ? (
                            <ActivityIndicator color="#FFF" />
                        ) : (
                            <Text style={styles.buttonText}>Sign In</Text>
                        )}
                    </TouchableOpacity>

                    <TouchableOpacity
                        style={styles.linkButton}
                        onPress={() => navigation.navigate('Signup')}
                        disabled={loading}
                    >
                        <Text style={styles.linkText}>
                            Don't have an account? <Text style={styles.linkTextBold}>Create one</Text>
                        </Text>
                    </TouchableOpacity>
                </View>
            </View>
        </KeyboardAvoidingView>
    );
}

const styles = StyleSheet.create({
    container: {
        flex: 1,
        backgroundColor: THEME.bg,
    },
    content: {
        flex: 1,
        justifyContent: 'center',
        paddingHorizontal: 24,
    },
    header: {
        alignItems: 'center',
        marginBottom: 48,
    },
    iconCircle: {
        width: 80,
        height: 80,
        borderRadius: 40,
        backgroundColor: '#EFF6FF',
        alignItems: 'center',
        justifyContent: 'center',
        marginBottom: 24,
    },
    title: {
        fontSize: 32,
        fontWeight: 'bold',
        color: THEME.primary,
        marginBottom: 8,
    },
    subtitle: {
        fontSize: 16,
        color: THEME.subtext,
        textAlign: 'center',
    },
    form: {
        width: '100%',
    },
    input: {
        backgroundColor: THEME.card,
        borderWidth: 1,
        borderColor: THEME.border,
        borderRadius: 12,
        padding: 16,
        fontSize: 16,
        color: THEME.primary,
        marginBottom: 16,
    },
    passwordContainer: {
        position: 'relative',
        marginBottom: 8,
    },
    passwordInput: {
        backgroundColor: THEME.card,
        borderWidth: 1,
        borderColor: THEME.border,
        borderRadius: 12,
        padding: 16,
        paddingRight: 48,
        fontSize: 16,
        color: THEME.primary,
    },
    eyeIcon: {
        position: 'absolute',
        right: 16,
        top: 16,
        padding: 4,
    },
    forgotPasswordButton: {
        alignSelf: 'flex-end',
        marginBottom: 16,
    },
    forgotPasswordText: {
        color: THEME.accent,
        fontSize: 14,
        fontWeight: '600',
    },
    button: {
        backgroundColor: THEME.accent,
        borderRadius: 12,
        padding: 16,
        alignItems: 'center',
        marginTop: 8,
    },
    buttonDisabled: {
        opacity: 0.6,
    },
    buttonText: {
        color: '#FFF',
        fontSize: 16,
        fontWeight: '700',
    },
    linkButton: {
        marginTop: 24,
        alignItems: 'center',
    },
    linkText: {
        color: THEME.subtext,
        fontSize: 14,
    },
    linkTextBold: {
        color: THEME.accent,
        fontWeight: '700',
    },
    errorText: {
        color: THEME.error,
        fontSize: 14,
        marginBottom: 12,
        textAlign: 'center',
    },
});
