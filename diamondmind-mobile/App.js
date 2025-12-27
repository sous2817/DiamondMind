import React, { useState, useRef } from 'react';
import { StyleSheet, Text, View, TouchableOpacity, ActivityIndicator, LogBox } from 'react-native';
import { SafeAreaProvider, SafeAreaView } from 'react-native-safe-area-context';
import * as ImagePicker from 'expo-image-picker';
import { CheckCircle2, AlertCircle, UploadCloud, XCircle, Maximize2, Minimize2 } from 'lucide-react-native';
import UploadService from './src/services/UploadService.js';
import { Video } from 'expo-av';
import SkeletonOverlay from './src/components/SkeletonOverlay';

// Silence the deprecation warning while we use the stable version
LogBox.ignoreLogs(['[expo-av]: Expo AV has been deprecated']);

export default function App() {
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);
  const [selectedFile, setSelectedFile] = useState(null);
  const [progress, setProgress] = useState(0);
  const abortControllerRef = useRef(null);
  const [currentFrameData, setCurrentFrameData] = useState(null);
  const [videoUri, setVideoUri] = useState(null);
  const [videoLayout, setVideoLayout] = useState({ width: 0, height: 0 });
  const [naturalSize, setNaturalSize] = useState(null);
  const [isFullscreen, setIsFullscreen] = useState(false);

  const pickVideo = async () => {
    let pickerResult = await ImagePicker.launchImageLibraryAsync({
      mediaTypes: ['videos'],
      allowsEditing: true,
      quality: 1,
    });

    if (pickerResult.canceled) return;

    const asset = pickerResult.assets[0];
    setSelectedFile(asset.fileName || "swing_video.mp4");
    setVideoUri(asset.uri);
    handleUpload(asset.uri);
  };

  const handleUpload = async (uri) => {
    setLoading(true);
    setError(null);
    setProgress(0);
    abortControllerRef.current = new AbortController();
    const jobId = Math.random().toString(36).substring(7);
    const ws = new WebSocket(`wss://diamondmind-vg35.onrender.com/ws/progress/${jobId}`);

    ws.onmessage = (e) => {
      try {
        const data = JSON.parse(e.data);
        if (data.progress) setProgress(data.progress);
      } catch (err) {
        console.error("WS Message Error:", err);
      }
    };

    try {
      const data = await UploadService.uploadSwingVideo(uri, jobId, abortControllerRef.current.signal);
      if (data) setResult(data);
    } catch (err) {
      if (err.message !== 'canceled') setError("Analysis failed or timed out.");
    } finally {
      setLoading(false);
      ws.close();
    }
  };

  const handlePlaybackStatusUpdate = (status) => {
    if (status.positionMillis && result?.frames) {
      const currentTimeMs = status.positionMillis;
      const frame = result.frames.find(f => f.timestamp >= currentTimeMs);
      if (frame) {
        setCurrentFrameData(frame.landmarks);
      }
    }
  };

  const handleReset = () => {
    setResult(null);
    setSelectedFile(null);
    setProgress(0);
    setCurrentFrameData(null);
    setVideoUri(null);
    setVideoLayout({ width: 0, height: 0 });
    setNaturalSize(null);
    setIsFullscreen(false);
  };

  return (
    <SafeAreaProvider>
      <SafeAreaView style={styles.container}>
        <View style={styles.header}>
          <Text style={styles.title}>DiamondMind</Text>
          <Text style={styles.subtitle}>Baseball Swing Analysis</Text>
        </View>

        {!loading && !result && (
          <TouchableOpacity style={styles.uploadCard} onPress={pickVideo}>
            <UploadCloud size={48} color="#007AFF" />
            <Text style={styles.uploadText}>Select Swing from Gallery</Text>
          </TouchableOpacity>
        )}

        {loading && (
          <View style={styles.statusCard}>
            <ActivityIndicator size="large" color="#007AFF" />
            <Text style={styles.loadingText}>Analyzing: {selectedFile}</Text>
            <View style={styles.progressContainer}>
              <View style={[styles.progressBar, { width: `${progress}%` }]} />
            </View>
            <Text style={styles.progressText}>{progress}% Complete</Text>
            <Text style={styles.waitingText}>Our AI is mapping 33 body points...</Text>
            <TouchableOpacity
              style={styles.cancelButton}
              onPress={() => abortControllerRef.current?.abort()}
            >
              <XCircle size={20} color="#FF3B30" />
              <Text style={styles.cancelButtonText}>Cancel Analysis</Text>
            </TouchableOpacity>
          </View>
        )}

        {result && (
          <View style={isFullscreen ? styles.fullscreenContainer : styles.successCard}>
            {isFullscreen && <SafeAreaView style={{ flex: 0, backgroundColor: '#000' }} />}
            <View
              style={isFullscreen ? styles.fullscreenVideoWrapper : styles.videoWrapper}
              onLayout={(e) => setVideoLayout(e.nativeEvent.layout)}
            >
              <Video
                source={{ uri: videoUri }}
                style={styles.videoPlayer}
                resizeMode="contain"
                useNativeControls={false}
                isLooping
                shouldPlay
                progressUpdateIntervalMillis={16}
                onReadyForDisplay={(event) => setNaturalSize(event.naturalSize)}
                onPlaybackStatusUpdate={handlePlaybackStatusUpdate}
              />

              <SkeletonOverlay
                landmarks={currentFrameData}
                width={videoLayout.width}
                height={videoLayout.height}
                naturalSize={naturalSize || { width: videoLayout.width, height: videoLayout.height }}
              />

              <TouchableOpacity
                style={[styles.modernExpandButton, { bottom: isFullscreen ? 60 : 24 }]}
                onPress={() => setIsFullscreen(!isFullscreen)}
                activeOpacity={0.7}
              >
                {isFullscreen ? (
                  <Minimize2 size={22} color="#FFF" />
                ) : (
                  <Maximize2 size={22} color="#FFF" />
                )}
              </TouchableOpacity>
            </View>

            {!isFullscreen && (
              <TouchableOpacity style={styles.resetButton} onPress={handleReset}>
                <Text style={styles.resetButtonText}>Analyze New Swing</Text>
              </TouchableOpacity>
            )}
          </View>
        )}

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
  title: { fontSize: 32, fontWeight: '900', color: '#1C1C1E' },
  subtitle: { fontSize: 16, color: '#8E8E93' },
  uploadCard: { backgroundColor: '#FFF', borderRadius: 20, padding: 40, alignItems: 'center', borderStyle: 'dashed', borderWidth: 2, borderColor: '#007AFF' },
  uploadText: { marginTop: 15, fontSize: 18, fontWeight: '600' },
  statusCard: { backgroundColor: '#FFF', borderRadius: 20, padding: 30, alignItems: 'center' },
  loadingText: { marginTop: 20, fontSize: 16, fontWeight: '700' },
  progressContainer: { width: '100%', height: 10, backgroundColor: '#E5E5EA', borderRadius: 5, overflow: 'hidden', marginVertical: 15 },
  progressBar: { height: '100%', backgroundColor: '#007AFF' },
  progressText: { fontSize: 14, fontWeight: '600', color: '#007AFF', marginBottom: 5 },
  waitingText: { fontSize: 14, color: '#8E8E93', marginBottom: 10 },
  cancelButton: { flexDirection: 'row', alignItems: 'center', marginTop: 15, padding: 10, backgroundColor: '#FFF5F5', borderRadius: 8, borderWidth: 1, borderColor: '#FFE5E5' },
  cancelButtonText: { color: '#FF3B30', fontWeight: '600', marginLeft: 8 },
  successCard: { backgroundColor: '#FFF', borderRadius: 20, padding: 20 },
  videoWrapper: { width: '100%', aspectRatio: 16 / 9, backgroundColor: '#000', borderRadius: 15, overflow: 'hidden', position: 'relative' },
  videoPlayer: { flex: 1 },
  resetButton: { marginTop: 20, backgroundColor: '#007AFF', padding: 15, borderRadius: 12, alignItems: 'center' },
  resetButtonText: { color: '#FFF', fontWeight: '700' },
  fullscreenContainer: { ...StyleSheet.absoluteFillObject, backgroundColor: '#000', zIndex: 1000 },
  fullscreenVideoWrapper: { flex: 1, width: '100%', height: '100%', justifyContent: 'center' },
  modernExpandButton: {
    position: 'absolute',
    right: 20,
    backgroundColor: 'rgba(28, 28, 30, 0.8)',
    width: 50,
    height: 50,
    borderRadius: 25,
    alignItems: 'center',
    justifyContent: 'center',
    borderWidth: 1,
    borderColor: 'rgba(255, 255, 255, 0.3)',
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.3,
    shadowRadius: 5,
    elevation: 5,
    zIndex: 1001,
  },
  errorCard: { backgroundColor: '#FFF', borderRadius: 20, padding: 20, alignItems: 'center', borderLeftWidth: 5, borderLeftColor: '#FF3B30' },
  errorText: { color: '#1C1C1E', fontWeight: '600', marginVertical: 10 },
  retryButton: { backgroundColor: '#F2F2F7', padding: 10, borderRadius: 8 },
  retryText: { color: '#007AFF', fontWeight: '700' },
});