import React, { useState, useEffect } from 'react';
import {
    View,
    Text,
    StyleSheet,
    ScrollView,
    TextInput,
    TouchableOpacity,
    Alert,
    ActivityIndicator,
} from 'react-native';
import { SwingService } from '../services/SwingService';

export default function SwingDetailScreen({ route, navigation }) {
    const { swingId } = route.params;

    const [loading, setLoading] = useState(true);
    const [saving, setSaving] = useState(false);
    const [swing, setSwing] = useState(null);
    const [analysis, setAnalysis] = useState(null);
    const [isEditing, setIsEditing] = useState(false);

    // Editable fields
    const [title, setTitle] = useState('');
    const [notes, setNotes] = useState('');

    useEffect(() => {
        loadSwingData();
    }, [swingId]);

    // Reload data when screen comes into focus
    useEffect(() => {
        const unsubscribe = navigation.addListener('focus', () => {
            loadSwingData();
        });
        return unsubscribe;
    }, [navigation]);

    const loadSwingData = async () => {
        try {
            setLoading(true);
            const analysisData = await SwingService.getSwingAnalysis(swingId);
            setAnalysis(analysisData);

            // Initialize editable fields
            setTitle(analysisData.title || '');
            setNotes(analysisData.notes || '');

            setLoading(false);
        } catch (error) {
            setLoading(false);
            Alert.alert('Error', 'Failed to load swing details');
            navigation.goBack();
        }
    };

    const handleSave = async () => {
        try {
            setSaving(true);
            await SwingService.updateSwing(swingId, title, notes);

            // Update local state
            setAnalysis({ ...analysis, title, notes });
            setIsEditing(false);
            setSaving(false);

            Alert.alert('Success', 'Swing updated successfully');
        } catch (error) {
            setSaving(false);
            Alert.alert('Error', 'Failed to update swing');
        }
    };

    const handleDelete = () => {
        Alert.alert(
            'Delete Swing',
            'Are you sure you want to delete this swing? This action cannot be undone.',
            [
                { text: 'Cancel', style: 'cancel' },
                {
                    text: 'Delete',
                    style: 'destructive',
                    onPress: async () => {
                        try {
                            await SwingService.deleteSwing(swingId);
                            Alert.alert('Success', 'Swing deleted successfully');
                            navigation.goBack();
                        } catch (error) {
                            Alert.alert('Error', 'Failed to delete swing');
                        }
                    },
                },
            ]
        );
    };

    const handleCancel = () => {
        // Reset to original values
        setTitle(analysis.title || '');
        setNotes(analysis.notes || '');
        setIsEditing(false);
    };

    if (loading) {
        return (
            <View style={styles.loadingContainer}>
                <ActivityIndicator size="large" color="#007AFF" />
                <Text style={styles.loadingText}>Loading swing details...</Text>
            </View>
        );
    }

    if (!analysis) {
        return (
            <View style={styles.errorContainer}>
                <Text style={styles.errorText}>Swing not found</Text>
            </View>
        );
    }

    return (
        <ScrollView style={styles.container}>
            {/* Header Section */}
            <View style={styles.header}>
                <Text style={styles.headerTitle}>
                    {analysis.title || `Swing #${swingId}`}
                </Text>
                <Text style={styles.headerDate}>
                    {new Date(analysis.created_at).toLocaleDateString()}
                </Text>
            </View>

            {/* Edit/Delete Actions */}
            <View style={styles.actions}>
                {!isEditing ? (
                    <>
                        <TouchableOpacity
                            style={[styles.button, styles.editButton]}
                            onPress={() => setIsEditing(true)}
                        >
                            <Text style={styles.buttonText}>Edit</Text>
                        </TouchableOpacity>
                        <TouchableOpacity
                            style={[styles.button, styles.deleteButton]}
                            onPress={handleDelete}
                        >
                            <Text style={styles.buttonText}>Delete</Text>
                        </TouchableOpacity>
                    </>
                ) : (
                    <>
                        <TouchableOpacity
                            style={[styles.button, styles.saveButton]}
                            onPress={handleSave}
                            disabled={saving}
                        >
                            {saving ? (
                                <ActivityIndicator size="small" color="#fff" />
                            ) : (
                                <Text style={styles.buttonText}>Save</Text>
                            )}
                        </TouchableOpacity>
                        <TouchableOpacity
                            style={[styles.button, styles.cancelButton]}
                            onPress={handleCancel}
                            disabled={saving}
                        >
                            <Text style={styles.buttonText}>Cancel</Text>
                        </TouchableOpacity>
                    </>
                )}
            </View>

            {/* Editable Fields */}
            <View style={styles.section}>
                <Text style={styles.sectionTitle}>Title</Text>
                <TextInput
                    style={[styles.input, !isEditing && styles.inputDisabled]}
                    value={title}
                    onChangeText={setTitle}
                    placeholder="Add a title..."
                    editable={isEditing}
                />
            </View>

            <View style={styles.section}>
                <Text style={styles.sectionTitle}>Notes</Text>
                <TextInput
                    style={[styles.textArea, !isEditing && styles.inputDisabled]}
                    value={notes}
                    onChangeText={setNotes}
                    placeholder="Add notes about this swing..."
                    multiline
                    numberOfLines={4}
                    editable={isEditing}
                />
            </View>

            {/* Analysis Results */}
            <View style={styles.section}>
                <Text style={styles.sectionTitle}>Analysis</Text>

                {analysis.phase && (
                    <View style={styles.analysisRow}>
                        <Text style={styles.analysisLabel}>Phase:</Text>
                        <Text style={styles.analysisValue}>{analysis.phase}</Text>
                    </View>
                )}

                {analysis.score !== null && (
                    <View style={styles.analysisRow}>
                        <Text style={styles.analysisLabel}>Score:</Text>
                        <Text style={styles.analysisValue}>{analysis.score}/100</Text>
                    </View>
                )}

                {analysis.feedback && (
                    <View style={styles.analysisRow}>
                        <Text style={styles.analysisLabel}>Feedback:</Text>
                        <Text style={styles.analysisValue}>{analysis.feedback}</Text>
                    </View>
                )}

                {analysis.drill && (
                    <View style={styles.analysisRow}>
                        <Text style={styles.analysisLabel}>Recommended Drill:</Text>
                        <Text style={styles.analysisValue}>{analysis.drill}</Text>
                    </View>
                )}

                {analysis.drill_explanation && (
                    <View style={styles.analysisRow}>
                        <Text style={styles.analysisLabel}>Drill Explanation:</Text>
                        <Text style={styles.analysisValue}>{analysis.drill_explanation}</Text>
                    </View>
                )}
            </View>

            {/* Technical Details */}
            <View style={styles.section}>
                <Text style={styles.sectionTitle}>Technical Details</Text>
                <View style={styles.analysisRow}>
                    <Text style={styles.analysisLabel}>Total Frames:</Text>
                    <Text style={styles.analysisValue}>{analysis.total_frames}</Text>
                </View>
                <View style={styles.analysisRow}>
                    <Text style={styles.analysisLabel}>Frames with Person:</Text>
                    <Text style={styles.analysisValue}>{analysis.frames_with_person}</Text>
                </View>
                <View style={styles.analysisRow}>
                    <Text style={styles.analysisLabel}>FPS:</Text>
                    <Text style={styles.analysisValue}>{analysis.fps}</Text>
                </View>
            </View>
        </ScrollView>
    );
}

const styles = StyleSheet.create({
    container: {
        flex: 1,
        backgroundColor: '#f5f5f5',
    },
    loadingContainer: {
        flex: 1,
        justifyContent: 'center',
        alignItems: 'center',
        backgroundColor: '#f5f5f5',
    },
    loadingText: {
        marginTop: 10,
        fontSize: 16,
        color: '#666',
    },
    errorContainer: {
        flex: 1,
        justifyContent: 'center',
        alignItems: 'center',
        backgroundColor: '#f5f5f5',
    },
    errorText: {
        fontSize: 18,
        color: '#ff3b30',
    },
    header: {
        backgroundColor: '#fff',
        padding: 20,
        borderBottomWidth: 1,
        borderBottomColor: '#e0e0e0',
    },
    headerTitle: {
        fontSize: 24,
        fontWeight: 'bold',
        color: '#333',
    },
    headerDate: {
        fontSize: 14,
        color: '#666',
        marginTop: 5,
    },
    actions: {
        flexDirection: 'row',
        padding: 15,
        gap: 10,
    },
    button: {
        flex: 1,
        padding: 12,
        borderRadius: 8,
        alignItems: 'center',
    },
    editButton: {
        backgroundColor: '#007AFF',
    },
    deleteButton: {
        backgroundColor: '#ff3b30',
    },
    saveButton: {
        backgroundColor: '#34c759',
    },
    cancelButton: {
        backgroundColor: '#8e8e93',
    },
    buttonText: {
        color: '#fff',
        fontSize: 16,
        fontWeight: '600',
    },
    section: {
        backgroundColor: '#fff',
        padding: 15,
        marginTop: 10,
    },
    sectionTitle: {
        fontSize: 18,
        fontWeight: '600',
        color: '#333',
        marginBottom: 10,
    },
    input: {
        borderWidth: 1,
        borderColor: '#ddd',
        borderRadius: 8,
        padding: 12,
        fontSize: 16,
        backgroundColor: '#fff',
    },
    textArea: {
        borderWidth: 1,
        borderColor: '#ddd',
        borderRadius: 8,
        padding: 12,
        fontSize: 16,
        backgroundColor: '#fff',
        minHeight: 100,
        textAlignVertical: 'top',
    },
    inputDisabled: {
        backgroundColor: '#f9f9f9',
        color: '#666',
    },
    analysisRow: {
        marginBottom: 12,
    },
    analysisLabel: {
        fontSize: 14,
        fontWeight: '600',
        color: '#666',
        marginBottom: 4,
    },
    analysisValue: {
        fontSize: 16,
        color: '#333',
    },
});
