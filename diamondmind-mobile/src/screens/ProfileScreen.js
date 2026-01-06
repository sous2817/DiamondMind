import React, { useState, useEffect, useContext } from 'react';
import { View, Text, TouchableOpacity, StyleSheet, FlatList, ActivityIndicator, RefreshControl } from 'react-native';
import { UserContext } from '../context/UserContext';
import { SwingService } from '../services/SwingService';
import { LogOut, Video, Calendar } from 'lucide-react-native';

const THEME = {
    bg: '#F8F9FA',
    card: '#FFFFFF',
    primary: '#0F172A',
    accent: '#2563EB',
    error: '#EF4444',
    subtext: '#64748B',
    border: '#E2E8F0'
};

export default function ProfileScreen() {
    const { user, logout } = useContext(UserContext);
    const [swings, setSwings] = useState([]);
    const [loading, setLoading] = useState(true);
    const [refreshing, setRefreshing] = useState(false);

    useEffect(() => {
        loadSwings();
    }, []);

    const loadSwings = async () => {
        if (!user?.id) return;

        try {
            setLoading(true);
            const userSwings = await SwingService.getUserSwings(user.id);
            setSwings(userSwings);
        } catch (error) {
            console.error('Failed to load swings:', error);
        } finally {
            setLoading(false);
        }
    };

    const onRefresh = async () => {
        setRefreshing(true);
        await loadSwings();
        setRefreshing(false);
    };

    const formatDate = (dateString) => {
        const date = new Date(dateString);
        return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' });
    };

    const handleSwingPress = (swing) => {
        navigation.navigate('SwingDetail', { swingId: swing.id });
    };
    console.log(`📹 Loading swing ${swing.id}: ${swing.filename}`);
    // Fetch the analysis for this swing
    const analysis = await SwingService.getSwingAnalysis(swing.id);
    console.log(`✅ Analysis loaded for swing ${swing.id}`);

    // TODO: Navigate to Upload tab and display this analysis
    // For now, just log it
    console.log('Analysis data:', analysis);
    alert(`Swing: ${swing.filename}\nFrames: ${analysis.frames?.length || 0}\nFPS: ${analysis.fps || 'N/A'}`);
} catch (error) {
    console.error('Failed to load swing analysis:', error);
    alert('Failed to load swing analysis. Please try again.');
}
    };

const renderSwingItem = ({ item }) => (
    <TouchableOpacity style={styles.swingCard} onPress={() => handleSwingPress(item)}>
        <View style={styles.swingIcon}>
            <Video size={24} color={THEME.accent} />
        </View>
        <View style={styles.swingInfo}>
            <Text style={styles.swingFilename}>{item.filename}</Text>
            <View style={styles.swingMeta}>
                <Calendar size={12} color={THEME.subtext} />
                <Text style={styles.swingDate}>{formatDate(item.created_at)}</Text>
            </View>
        </View>
    </TouchableOpacity>
);

const renderEmptyState = () => (
    <View style={styles.emptyState}>
        <View style={styles.emptyIcon}>
            <Video size={48} color={THEME.subtext} />
        </View>
        <Text style={styles.emptyTitle}>No Swings Yet</Text>
        <Text style={styles.emptySubtitle}>Upload your first swing to get started!</Text>
    </View>
);

return (
    <View style={styles.container}>
        {/* Header */}
        <View style={styles.header}>
            <View style={styles.userInfo}>
                <View style={styles.avatar}>
                    <Text style={styles.avatarText}>{user?.username?.charAt(0).toUpperCase()}</Text>
                </View>
                <View style={styles.userDetails}>
                    <Text style={styles.username}>{user?.username}</Text>
                    <Text style={styles.email}>{user?.email}</Text>
                </View>
            </View>
            <TouchableOpacity style={styles.logoutButton} onPress={logout}>
                <LogOut size={20} color={THEME.error} />
                <Text style={styles.logoutText}>Logout</Text>
            </TouchableOpacity>
        </View>

        {/* Swing History */}
        <View style={styles.section}>
            <Text style={styles.sectionTitle}>Swing History</Text>
            <Text style={styles.sectionSubtitle}>{swings.length} total swings</Text>
        </View>

        {loading ? (
            <View style={styles.loadingContainer}>
                <ActivityIndicator size="large" color={THEME.accent} />
            </View>
        ) : (
            <FlatList
                data={swings}
                renderItem={renderSwingItem}
                keyExtractor={(item) => item.id.toString()}
                contentContainerStyle={styles.listContainer}
                ListEmptyComponent={renderEmptyState}
                refreshControl={
                    <RefreshControl refreshing={refreshing} onRefresh={onRefresh} tintColor={THEME.accent} />
                }
            />
        )}
    </View>
);
}

const styles = StyleSheet.create({
    container: {
        flex: 1,
        backgroundColor: THEME.bg,
    },
    header: {
        backgroundColor: THEME.card,
        padding: 24,
        paddingTop: 60,
        borderBottomWidth: 1,
        borderBottomColor: THEME.border,
    },
    userInfo: {
        flexDirection: 'row',
        alignItems: 'center',
        marginBottom: 16,
    },
    avatar: {
        width: 60,
        height: 60,
        borderRadius: 30,
        backgroundColor: THEME.accent,
        alignItems: 'center',
        justifyContent: 'center',
        marginRight: 16,
    },
    avatarText: {
        fontSize: 24,
        fontWeight: 'bold',
        color: '#FFF',
    },
    userDetails: {
        flex: 1,
    },
    username: {
        fontSize: 20,
        fontWeight: 'bold',
        color: THEME.primary,
        marginBottom: 4,
    },
    email: {
        fontSize: 14,
        color: THEME.subtext,
    },
    logoutButton: {
        flexDirection: 'row',
        alignItems: 'center',
        backgroundColor: '#FEE2E2',
        paddingVertical: 12,
        paddingHorizontal: 16,
        borderRadius: 12,
        justifyContent: 'center',
    },
    logoutText: {
        color: THEME.error,
        fontSize: 16,
        fontWeight: '600',
        marginLeft: 8,
    },
    section: {
        padding: 24,
        paddingBottom: 12,
    },
    sectionTitle: {
        fontSize: 18,
        fontWeight: 'bold',
        color: THEME.primary,
        marginBottom: 4,
    },
    sectionSubtitle: {
        fontSize: 14,
        color: THEME.subtext,
    },
    listContainer: {
        paddingHorizontal: 24,
        paddingBottom: 24,
    },
    swingCard: {
        backgroundColor: THEME.card,
        borderRadius: 12,
        padding: 16,
        marginBottom: 12,
        flexDirection: 'row',
        alignItems: 'center',
        shadowColor: '#000',
        shadowOffset: { width: 0, height: 2 },
        shadowOpacity: 0.05,
        shadowRadius: 4,
        elevation: 2,
    },
    swingIcon: {
        width: 48,
        height: 48,
        borderRadius: 24,
        backgroundColor: '#EFF6FF',
        alignItems: 'center',
        justifyContent: 'center',
        marginRight: 16,
    },
    swingInfo: {
        flex: 1,
    },
    swingFilename: {
        fontSize: 16,
        fontWeight: '600',
        color: THEME.primary,
        marginBottom: 4,
    },
    swingMeta: {
        flexDirection: 'row',
        alignItems: 'center',
    },
    swingDate: {
        fontSize: 12,
        color: THEME.subtext,
        marginLeft: 4,
    },
    loadingContainer: {
        flex: 1,
        justifyContent: 'center',
        alignItems: 'center',
    },
    emptyState: {
        alignItems: 'center',
        paddingVertical: 60,
    },
    emptyIcon: {
        width: 80,
        height: 80,
        borderRadius: 40,
        backgroundColor: '#F1F5F9',
        alignItems: 'center',
        justifyContent: 'center',
        marginBottom: 16,
    },
    emptyTitle: {
        fontSize: 18,
        fontWeight: 'bold',
        color: THEME.primary,
        marginBottom: 8,
    },
    emptySubtitle: {
        fontSize: 14,
        color: THEME.subtext,
        textAlign: 'center',
    },
});
