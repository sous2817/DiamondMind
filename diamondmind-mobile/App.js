import React, { useState, useRef } from 'react';
import { StyleSheet, Text, View, TouchableOpacity, ActivityIndicator, ScrollView } from 'react-native';
// Fixed: Using the modern Safe Area library
import { SafeAreaProvider, SafeAreaView } from 'react-native-safe-area-context';
import * as ImagePicker from 'expo-image-picker';
import { CheckCircle2, AlertCircle, UploadCloud, XCircle } from 'lucide-react-native';
import UploadService from './src/services/UploadService.js';

export default function App() {
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);
  const [selectedFile, setSelectedFile] = useState(null);
  const abortControllerRef = useRef(null);
  const [progress, setProgress] = useState(0);

  
  const pickVideo = async () => {
    let pickerResult = await ImagePicker.launchImageLibraryAsync({
      mediaTypes: ['videos'],
      allowsEditing: true,
      quality: 1,
    });

    if (pickerResult.canceled) return;

    const asset = pickerResult.assets[0];
    setSelectedFile(asset.fileName || "swing_video.mp4");
    handleUpload(asset.uri);
  };

  const handleUpload = async (uri) => {
  setLoading(true);
  setProgress(0); // Reset progress
  const jobId = Math.random().toString(36).substring(7); // Simple unique ID

  // 1. Open the WebSocket to listen for progress
  const ws = new WebSocket(`wss://diamondmind-vg35.onrender.com/ws/progress/${jobId}`);
  
  ws.onmessage = (e) => {
    const data = JSON.parse(e.data);
    setProgress(data.progress); // Update the bar!
  };

  try {
    // 2. Start the upload (pass the jobId so the AI knows who to update)
    const data = await UploadService.uploadSwingVideo(uri, jobId, abortControllerRef.current.signal);
    if (data) setResult(data);
  } finally {
    setLoading(false);
    ws.close();
  }
  };  

  const cancelAnalysis = () => {
    if (abortControllerRef.current) {
      abortControllerRef.current.abort();
    }
    setLoading(false);
    setSelectedFile(null);
    setResult(null);
  };

  return (
    <SafeAreaProvider>
      <SafeAreaView style={styles.container}>
        <View style={styles.header}>
          <Text style={styles.title}>DiamondMind</Text>
          <Text style={styles.subtitle}>Pro-Grade Swing Analysis</Text>
        </View>

        {/* 1. INITIAL STATE: The missing Upload Card */}
        {!loading && !result && (
          <TouchableOpacity style={styles.uploadCard} onPress={pickVideo}>
            <UploadCloud size={48} color="#007AFF" />
            <Text style={styles.uploadText}>Select Swing from Gallery</Text>
            <Text style={styles.uploadSubtext}>Max 50MB • MP4 or MOV</Text>
          </TouchableOpacity>
        )}

        {/* 2. LOADING STATE: Combined with Cancel button */}
        {loading && (
          <View style={styles.statusCard}>
            <ActivityIndicator size="large" color="#007AFF" />
            <Text style={styles.loadingText}>Analyzing: {selectedFile}</Text>
            <Text style={styles.waitingText}>Our AI is mapping 33 body points...</Text>

            <TouchableOpacity style={styles.cancelButton} onPress={cancelAnalysis}>
              <XCircle size={20} color="#FF3B30" />
              <Text style={styles.cancelButtonText}>Cancel Analysis</Text>
            </TouchableOpacity>
          </View>
        )}

        {/* 3. SUCCESS STATE */}
        {result && (
          <View style={styles.successCard}>
            <View style={styles.row}>
              <CheckCircle2 size={24} color="#34C759" />
              <Text style={styles.successTitle}>Analysis Ready</Text>
            </View>
            <Text style={styles.fileLabel}>File: {selectedFile}</Text>

            <ScrollView style={styles.jsonPreview}>
              <Text style={styles.dataPoint}>Total Frames: {result.metadata?.total_frames}</Text>
              <Text style={styles.dataPoint}>FPS: {result.metadata?.fps?.toFixed(2)}</Text>
              <Text style={styles.jsonCode}>{JSON.stringify(result.frames[0]?.landmarks[0], null, 2)}</Text>
            </ScrollView>

            <TouchableOpacity style={styles.resetButton} onPress={() => { setResult(null); setSelectedFile(null); }}>
              <Text style={styles.resetButtonText}>Analyze Another Swing</Text>
            </TouchableOpacity>
          </View>
        )}

        {/* 4. ERROR STATE */}
        {error && (
          <View style={styles.errorCard}>
            <AlertCircle size={24} color="#FF3B30" />
            <Text style={styles.errorText}>{error}</Text>
            <TouchableOpacity style={styles.retryButton} onPress={pickVideo}>
              <Text style={styles.retryText}>Try Again</Text>
            </TouchableOpacity>
          </View>
        )}
      </SafeAreaView>
    </SafeAreaProvider>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: '#F2F2F7', padding: 20 },
  header: { alignItems: 'center', marginTop: 20, marginBottom: 40 },
  title: { fontSize: 32, fontWeight: '900', color: '#1C1C1E', letterSpacing: -1 },
  subtitle: { fontSize: 16, color: '#8E8E93', fontWeight: '500' },
  uploadCard: {
    backgroundColor: '#FFF',
    borderRadius: 20,
    padding: 40,
    alignItems: 'center',
    borderStyle: 'dashed',
    borderWidth: 2,
    borderColor: '#007AFF'
  },
  uploadText: { marginTop: 15, fontSize: 18, fontWeight: '600', color: '#1C1C1E' },
  uploadSubtext: { marginTop: 5, fontSize: 14, color: '#8E8E93' },
  statusCard: { backgroundColor: '#FFF', borderRadius: 20, padding: 30, alignItems: 'center', elevation: 5, shadowColor: '#000', shadowOffset: { width: 0, height: 2 }, shadowOpacity: 0.1, shadowRadius: 10 },
  loadingText: { marginTop: 20, fontSize: 16, fontWeight: '700', textAlign: 'center' },
  waitingText: { marginTop: 8, fontSize: 14, color: '#8E8E93', marginBottom: 10 },
  cancelButton: { flexDirection: 'row', alignItems: 'center', marginTop: 15, padding: 10, backgroundColor: '#FFF5F5', borderRadius: 8, borderWidth: 1, borderColor: '#FFE5E5' },
  cancelButtonText: { color: '#FF3B30', fontWeight: '600', marginLeft: 8 },
  successCard: { backgroundColor: '#FFF', borderRadius: 20, padding: 20, width: '100%' },
  row: { flexDirection: 'row', alignItems: 'center', marginBottom: 10 },
  successTitle: { fontSize: 18, fontWeight: '700', color: '#34C759', marginLeft: 8 },
  fileLabel: { fontSize: 14, color: '#8E8E93', marginBottom: 15 },
  jsonPreview: { backgroundColor: '#F2F2F7', borderRadius: 12, padding: 15, maxHeight: 300 },
  dataPoint: { fontSize: 15, fontWeight: '600', marginBottom: 5 },
  jsonCode: { fontFamily: 'monospace', fontSize: 12, color: '#444', marginTop: 10 },
  resetButton: { marginTop: 20, backgroundColor: '#007AFF', padding: 15, borderRadius: 12, alignItems: 'center' },
  resetButtonText: { color: '#FFF', fontWeight: '700' },
  errorCard: { backgroundColor: '#FFF', borderRadius: 20, padding: 20, alignItems: 'center', borderLeftWidth: 5, borderLeftColor: '#FF3B30' },
  errorText: { color: '#1C1C1E', fontWeight: '600', marginVertical: 10 },
  retryButton: { backgroundColor: '#F2F2F7', padding: 10, borderRadius: 8 },
  retryText: { color: '#007AFF', fontWeight: '700' },
});