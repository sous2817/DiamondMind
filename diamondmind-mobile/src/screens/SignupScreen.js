import React, { useState, useContext } from 'react';
import { View, Text, TextInput, TouchableOpacity, StyleSheet, ActivityIndicator, KeyboardAvoidingView, Platform } from 'react-native';
import { UserContext } from '../context/UserContext';
import { UserPlus } from 'lucide-react-native';

const THEME = {
    bg: '#F8F9FA',
    card: '#FFFFFF',
    primary: '#0F172A',
    accent: '#2563EB',
    error: '#EF4444',
    subtext: '#64748B',
    border: '#E2E8F0'
};

export default function SignupScreen({ navigation }) {
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [confirmPassword, setConfirmPassword] = useState('');
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState('');
    const { signup } = useContext(UserContext);

    const handleSignup = async () => {
        if (!email.trim() || !password || !confirmPassword) {
            setError('Please fill in all fields');
            return;
        }

        if (!email.includes('@')) {
            setError('Please enter a valid email');
            return;
        }

        if (password.length < 6) {
            setError('Password must be at least 6 characters');
            return;
        }

        if (password !== confirmPassword) {
            setError('Passwords do not match');
            return;
        }

        setLoading(true);
        setError('');

        try {
            await signup(email.trim().toLowerCase(), password);
            // Navigation handled by App.js conditional rendering
        } catch (err) {
            console.error('Signup error:', err);
            setError(err.message || 'Unable to create account. Please try again.');
        } finally {
            setLoading(false);
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
                        <UserPlus size={32} color={THEME.accent} />
                    </View>
                    <Text style={styles.title}>Create Account</Text>
                    <Text style={styles.subtitle}>Join DiamondMind to save your swing history</Text>
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

                    <TextInput
                        style={styles.input}
                        placeholder="Password (min 6 characters)"
                        placeholderTextColor={THEME.subtext}
                        value={password}
                        onChangeText={setPassword}
                        secureTextEntry
                        autoCapitalize="none"
                        editable={!loading}
                    />

                    <TextInput
                        style={styles.input}
                        placeholder="Confirm Password"
                        placeholderTextColor={THEME.subtext}
                        value={confirmPassword}
                        onChangeText={setConfirmPassword}
                        secureTextEntry
                        autoCapitalize="none"
                        editable={!loading}
                    />

                    {error ? (
                        <Text style={styles.errorText}>{error}</Text>
                    ) : null}

                    <TouchableOpacity
                        style={[styles.button, loading && styles.buttonDisabled]}
                        onPress={handleSignup}
                        disabled={loading}
                    >
                        {loading ? (
                            <ActivityIndicator color="#FFF" />
                        ) : (
                            <Text style={styles.buttonText}>Create Account</Text>
                        )}
                    </TouchableOpacity>

                    <TouchableOpacity
                        style={styles.linkButton}
                        onPress={() => navigation.navigate('Login')}
                        disabled={loading}
                    >
                        <Text style={styles.linkText}>
                            Already have an account? <Text style={styles.linkTextBold}>Sign in</Text>
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
        paddingHorizontal: 20,
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
