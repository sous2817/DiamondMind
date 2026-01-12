import React, { useState, useRef, useEffect, useContext } from 'react';
import { StyleSheet, Text, View, TouchableOpacity, ActivityIndicator, StatusBar } from 'react-native';
import { SafeAreaProvider, SafeAreaView } from 'react-native-safe-area-context';
import * as ImagePicker from 'expo-image-picker';
import { UploadCloud, Maximize2, Minimize2, AlertCircle, X, Zap, ChevronRight, ChevronLeft, Eye, EyeOff } from 'lucide-react-native';
import { useVideoPlayer, VideoView } from 'expo-video';
import UploadService from '../services/UploadService.js';
import { VideoCompressionService } from '../services/VideoCompressionService';
import SkeletonOverlay from './SkeletonOverlay';
import BatTrailOverlay from './BatTrailOverlay';
import Slider from '@react-native-community/slider';
import { Config } from '../config.js';
import { UserContext } from '../context/UserContext';
import { THEME } from '../styles/theme';
import { styles } from './MainApp.styles';

function MainApp() {
    const { logout, user } = useContext(UserContext);
    const [loading, setLoading] = useState(false);
    const [result, setResult] = useState(null);
    const [error, setError] = useState(null);
    const [selectedFile, setSelectedFile] = useState(null);
    const [progress, setProgress] = useState(0);
    const [videoUri, setVideoUri] = useState(null);
    const [currentFrameData, setCurrentFrameData] = useState(null);
    const [isFullscreen, setIsFullscreen] = useState(false);
    const abortControllerRef = useRef(null);
    const [videoDimensions, setVideoDimensions] = useState({ width: 0, height: 0 });
    const [containerDimensions, setContainerDimensions] = useState({ width: 0, height: 0 });
    const [fullscreenDimensions, setFullscreenDimensions] = useState({ width: 0, height: 0 });
    const [showOverlay, setShowOverlay] = useState(true);
    const [showBatTrail, setShowBatTrail] = useState(true);
    const [showSkeleton, setShowSkeleton] = useState(true);
    const [isCompressing, setIsCompressing] = useState(false);
    const [compressionProgress, setCompressionProgress] = useState(0);
    const [isScrubbing, setIsScrubbing] = useState(false);
    const [scrubPosition, setScrubPosition] = useState(0); // 0-1 range

    // ⚡️ PERFORMANCE: Track current frame index to avoid redundant state updates
    const currentFrameIndexRef = useRef(-1);

    // ⚡️ FIX: Logic moved inside the hook to avoid race conditions
    const player = useVideoPlayer(videoUri, (p) => {
        p.loop = true;
        p.timeUpdateEventInterval = 0.016;
        if (videoUri) {
            p.play();
        }
    });

    useEffect(() => {
        if (!player || !videoUri || !result) return;
        const sub = player.addListener('timeUpdate', (payload) => {
            // DM-59: Only update frames automatically when video is playing
            // This allows manual stepping to work without interference
            if (!player.playing) return;

            if (result?.frames && result.fps) {
                // ⚡️ OPTIMIZATION: Use O(1) direct index access instead of O(N) .find()
                // This eliminates the "loop over all frames" jitter
                const frameIndex = Math.floor(payload.currentTime * result.fps);

                // ⚡️ PERFORMANCE FIX: Only update state if frame actually changed
                // This reduces state updates from 60/sec to video FPS (~30/sec)
                if (frameIndex !== currentFrameIndexRef.current && frameIndex < result.frames.length) {
                    currentFrameIndexRef.current = frameIndex;
                    const frame = result.frames[frameIndex];

                    if (frame) {
                        setCurrentFrameData(frame.landmarks);
                    }

                    // DM-59: Update scrub position
                    const position = payload.currentTime / (player.duration || 1);
                    setScrubPosition(position);
                }
            }
        });
        return () => sub.remove();
    }, [player, videoUri, result]);

    // DM-59: Scrubbing functions
    const handleScrubChange = (value) => {
        setScrubPosition(value);

        if (player && result) {
            const targetTime = value * (player.duration || 0);
            player.currentTime = targetTime;

            // Update frame data immediately
            const frameIndex = Math.floor(targetTime * result.fps);
            if (frameIndex >= 0 && frameIndex < result.frames.length) {
                currentFrameIndexRef.current = frameIndex;
                const frame = result.frames[frameIndex];
                if (frame) {
                    setCurrentFrameData(frame.landmarks);
                }
            }
        }
    };

    const handleScrubComplete = () => {
        setIsScrubbing(false);
    };

    const stepForward = () => {
        if (!player || !result) return;

        const currentFrame = currentFrameIndexRef.current;
        const nextFrame = Math.min(currentFrame + 1, result.total_frames - 1);

        // Pause video to prevent automatic playback
        player.pause();

        // Seek to target frame
        const targetTime = nextFrame / result.fps;
        player.currentTime = targetTime;

        // Update scrub position
        const position = targetTime / (player.duration || 1);
        setScrubPosition(position);

        // Update frame data immediately
        if (nextFrame < result.frames.length) {
            currentFrameIndexRef.current = nextFrame;
            const frame = result.frames[nextFrame];
            if (frame) {
                setCurrentFrameData(frame.landmarks);
            }
        }
    };

    const stepBackward = () => {
        if (!player || !result) return;

        const currentFrame = currentFrameIndexRef.current;
        const prevFrame = Math.max(currentFrame - 1, 0);

        // Pause video to prevent automatic playback
        player.pause();

        // Seek to target frame
        const targetTime = prevFrame / result.fps;
        player.currentTime = targetTime;

        // Update scrub position
        const position = targetTime / (player.duration || 1);
        setScrubPosition(position);

        // Update frame data immediately
        if (prevFrame >= 0 && prevFrame < result.frames.length) {
            currentFrameIndexRef.current = prevFrame;
            const frame = result.frames[prevFrame];
            if (frame) {
                setCurrentFrameData(frame.landmarks);
            }
        }
    };

    const formatTime = (seconds) => {
        if (!seconds || isNaN(seconds)) return '0:00';
        const mins = Math.floor(seconds / 60);
        const secs = Math.floor(seconds % 60);
        return `${mins}:${secs.toString().padStart(2, '0')}`;
    };

    // ✅ ALIGNMENT FIX: Update video dimensions from player source
    // This ensures we use the EXACT dimensions MediaPipe analyzed
    useEffect(() => {
        if (player?.src?.width && player?.src?.height) {
            setVideoDimensions({
                width: player.src.width,
                height: player.src.height
            });
        }
    }, [player]);

    // Calculate attack angle from bat trail data
    const calculateAttackAngle = () => {
        if (!result?.frames) return null;

        const batPositions = result.frames
            .map((frame, idx) => ({ ...frame.bat_position, frameIndex: idx }))
            .filter(pos => pos.x !== undefined && pos.y !== undefined);

        if (batPositions.length < 15) return null; // Need enough data points

        // Find contact point (lowest Y value, highest point in screen coords)
        const contactIdx = batPositions.reduce((minIdx, pos, idx) =>
            pos.y < batPositions[minIdx].y ? idx : minIdx, 0);

        const contactFrame = batPositions[contactIdx];

        // Get positions 5 frames before and after contact
        const beforeIdx = Math.max(0, contactIdx - 5);
        const afterIdx = Math.min(batPositions.length - 1, contactIdx + 5);

        const beforePos = batPositions[beforeIdx];
        const afterPos = batPositions[afterIdx];

        // Calculate angle (in degrees)
        // Positive angle = upward swing, Negative = downward
        const deltaY = afterPos.y - beforePos.y;
        const deltaX = afterPos.x - beforePos.x;
        const angleRad = Math.atan2(deltaY, deltaX);
        const angleDeg = angleRad * (180 / Math.PI);

        return Math.round(angleDeg);
    };

    const attackAngle = result ? calculateAttackAngle() : null;

    const handleUpload = async (uri) => {
        setLoading(true);
        setError(null);
        setProgress(0);

        abortControllerRef.current = new AbortController();
        const jobId = Math.random().toString(36).substring(7);

        // ✅ LOG: Connection Attempt (Section 14)
        console.log(`📡 WebSocket connecting to job: ${jobId}`);

        // Use centralized config
        const ws = new WebSocket(`${Config.WS_BASE_URL}/ws/progress/${jobId}`);

        // ✅ HEARTBEAT: Send a ping every 25s to keep the Read timeout from triggering on the LB
        // Render/Nginx closes connections if no data flows from Client -> Server for 60-100s.
        const pingInterval = setInterval(() => {
            if (ws.readyState === WebSocket.OPEN) {
                console.log("💓 Sending Ping...");
                ws.send(JSON.stringify({ type: "ping" }));
            }
        }, 25000);

        // ✅ LOG: Connection Success (Section 14)
        ws.onopen = () => {
            console.log("✅ WebSocket connected");
        };

        ws.onmessage = (e) => {
            const data = JSON.parse(e.data);
            if (data.progress) {
                // ✅ LOG: Progress Update (Section 14)
                console.log(`📊 Progress update: ${data.progress}%`);
                setProgress(data.progress);
            }

            // ⚡️ ASYNC Handling: Result comes via WebSocket now
            if (data.result) {
                console.log("✅ Received Result via WebSocket");
                setResult(data.result);
                setLoading(false);
                clearInterval(pingInterval);
                ws.close();
            }

            // ⚡️ ASYNC Handling: Errors via WebSocket
            if (data.error) {
                console.error("❌ Received Error via WebSocket:", data.error);
                setError(data.error);
                setLoading(false);
                clearInterval(pingInterval);
                ws.close();
            }
        };

        ws.onclose = () => {
            console.log("🔌 WebSocket closed");
            clearInterval(pingInterval);
        };

        try {
            // Note: "Starting upload..." log is handled inside UploadService.js
            const data = await UploadService.uploadSwingVideo(uri, jobId, user?.id, abortControllerRef.current.signal);

            // If sync response contains result (legacy behavior or fast response)
            if (data && data.frames) {
                setResult(data);
                setLoading(false);
                clearInterval(pingInterval);
                ws.close();
            } else {
                // ⏳ Async Mode: Server said "Processing", so we wait.
                // Do NOT set loading to false here.
                console.log("⏳ Upload accepted, waiting for AI processing...");
            }

        } catch (err) {
            console.error("❌ UPLOAD FAILED:", err);
            if (err.message !== 'canceled') {
                const msg = err.response?.data?.detail || err.message || "Connection timed out. Check server status.";
                setError(msg);
            }
            setLoading(false);
            clearInterval(pingInterval);
            ws.close();
        }
    };

    const pickVideo = async () => {
        try {
            let res = await ImagePicker.launchImageLibraryAsync({ mediaTypes: ['videos'], quality: 1 });
            if (res.canceled) return;
            const asset = res.assets[0];

            // Reset state
            setResult(null);
            setError(null);

            const originalUri = asset.uri;
            console.log('📹 Video selected:', originalUri);

            // Show compression UI
            setIsCompressing(true);
            setCompressionProgress(0);

            // Compress video
            const compressedUri = await VideoCompressionService.compressVideo(
                originalUri,
                (progress) => setCompressionProgress(progress)
            );

            setIsCompressing(false);

            // Set initial dimensions from asset (will be updated by player when loaded)
            setVideoDimensions({ width: asset.width, height: asset.height });
            setSelectedFile(asset.fileName || "swing.mp4");

            // ⚡️ FIX: Only set state here. The useVideoPlayer hook handles the play command.
            setVideoUri(compressedUri);

            handleUpload(compressedUri);

            // Cleanup old temp files (non-blocking)
            VideoCompressionService.cleanupTempFiles();

        } catch (error) {
            console.error('❌ Video processing failed:', error);
            setIsCompressing(false);
            setError('Failed to process video. Please try again.');
        }
    };

    const handleReset = () => {
        setResult(null);
        setVideoUri(null);
        setProgress(0);
        setCurrentFrameData(null);
        setIsFullscreen(false);
        setError(null);
        setShowOverlay(true); // Reset overlay to visible
        setShowBatTrail(true); // Reset bat trail to visible
        currentFrameIndexRef.current = -1; // Reset frame tracking
    };

    const videoRatio = player.src?.width ? player.src.width / player.src.height : 1.77;

    return (
        <SafeAreaProvider>
            <StatusBar barStyle="dark-content" backgroundColor={THEME.bg} />

            {/* --- Fullscreen Mode --- */}
            {result && isFullscreen && (
                <View style={styles.fullscreenContainer}>
                    <View style={{ flex: 1 }} onLayout={(e) => setFullscreenDimensions(e.nativeEvent.layout)}>
                        <VideoView player={player} style={StyleSheet.absoluteFill} contentMode="contain" />
                        <View style={StyleSheet.absoluteFill} pointerEvents="none">
                            {showOverlay && (
                                <SkeletonOverlay
                                    landmarks={currentFrameData}
                                    videoWidth={videoDimensions.width}
                                    videoHeight={videoDimensions.height}
                                    containerWidth={fullscreenDimensions.width}
                                    containerHeight={fullscreenDimensions.height}
                                />
                            )}
                        </View>
                        {showBatTrail && (
                            <BatTrailOverlay
                                frames={result.frames}
                                currentFrameIndex={currentFrameIndexRef.current}
                                videoWidth={videoDimensions.width}
                                videoHeight={videoDimensions.height}
                                containerWidth={fullscreenDimensions.width}
                                containerHeight={fullscreenDimensions.height}
                            />
                        )}
                        <TouchableOpacity style={styles.closeFab} onPress={() => setIsFullscreen(false)}>
                            <Minimize2 size={24} color="#FFF" />
                        </TouchableOpacity>
                        <TouchableOpacity
                            style={{ position: 'absolute', top: 60, left: 24, backgroundColor: 'rgba(255,255,255,0.2)', width: 44, height: 44, borderRadius: 22, alignItems: 'center', justifyContent: 'center' }}
                            onPress={() => setShowOverlay(!showOverlay)}
                        >
                            {showOverlay ? <Eye size={24} color="#FFF" /> : <EyeOff size={24} color="#FFF" />}
                        </TouchableOpacity>
                        <TouchableOpacity
                            style={{ position: 'absolute', top: 110, left: 24, backgroundColor: 'rgba(255,255,255,0.2)', width: 44, height: 44, borderRadius: 22, alignItems: 'center', justifyContent: 'center' }}
                            onPress={() => setShowBatTrail(!showBatTrail)}
                        >
                            <Text style={{ color: '#FFF', fontSize: 20, fontWeight: 'bold' }}>🏏</Text>
                        </TouchableOpacity>
                    </View>
                </View>
            )}

            {/* --- Main Interface --- */}
            {!isFullscreen && (
                <SafeAreaView style={styles.container}>

                    {/* Header */}
                    <View style={styles.headerContainer}>
                        <View style={styles.badge}>
                            <Zap size={12} color={THEME.accent} fill={THEME.accent} />
                            <Text style={styles.badgeText}>AI POWERED</Text>
                        </View>
                        <Text style={styles.title}>DiamondMind</Text>
                        <Text style={styles.subtitle}>Pro-Level Swing Analysis</Text>
                    </View>

                    {/* Content Area */}
                    <View style={{ flex: 1 }}>

                        {/* 1. Upload Card (Empty State) */}
                        {!loading && !result && (
                            <View style={styles.uploadCard}>
                                <View style={styles.iconCircle}>
                                    <UploadCloud size={32} color={THEME.accent} />
                                </View>
                                <Text style={styles.ctaText}>Analyze a Swing</Text>
                                <Text style={styles.ctaSubtext}>Select a video from your gallery to generate a skeletal frame analysis.</Text>

                                <TouchableOpacity style={styles.primaryButton} onPress={pickVideo}>
                                    <Text style={styles.primaryButtonText}>Open Gallery</Text>
                                    <ChevronRight size={20} color="#FFF" />
                                </TouchableOpacity>
                            </View>
                        )}

                        {/* 2. Loading State */}
                        {loading && (
                            <View style={styles.statusCard}>
                                <ActivityIndicator size="large" color={THEME.accent} />
                                <Text style={styles.loadingText}>Analyzing Swing...</Text>
                                <View style={styles.progressTrack}>
                                    <View style={[styles.progressBar, { width: `${progress}%` }]} />
                                </View>
                                <Text style={{ marginTop: 8, color: THEME.subtext, fontSize: 12 }}>
                                    Uploading & Processing: {progress}%
                                </Text>

                                <TouchableOpacity style={styles.cancelBtn} onPress={() => { abortControllerRef.current?.abort(); setLoading(false); }}>
                                    <Text style={styles.cancelText}>Cancel</Text>
                                </TouchableOpacity>
                            </View>
                        )}

                        {/* 3. Success / Results View */}
                        {result && (
                            <View style={styles.resultsContainer}>
                                <View
                                    style={[styles.videoFrame, { aspectRatio: videoRatio }]}
                                    onLayout={(e) => setContainerDimensions(e.nativeEvent.layout)}
                                >
                                    <VideoView player={player} style={StyleSheet.absoluteFill} contentMode="contain" />
                                    <View style={StyleSheet.absoluteFill} pointerEvents="none">
                                        {showOverlay && (
                                            <SkeletonOverlay
                                                landmarks={currentFrameData}
                                                videoWidth={videoDimensions.width}
                                                videoHeight={videoDimensions.height}
                                                containerWidth={containerDimensions.width}
                                                containerHeight={containerDimensions.height}
                                            />
                                        )}
                                    </View>
                                    {showBatTrail && (
                                        <BatTrailOverlay
                                            frames={result.frames}
                                            currentFrameIndex={currentFrameIndexRef.current}
                                            videoWidth={videoDimensions.width}
                                            videoHeight={videoDimensions.height}
                                            containerWidth={containerDimensions.width}
                                            containerHeight={containerDimensions.height}
                                        />
                                    )}
                                    <TouchableOpacity
                                        style={{ position: 'absolute', bottom: 16, left: 16, backgroundColor: 'rgba(0,0,0,0.6)', padding: 8, borderRadius: 20 }}
                                        onPress={() => setShowOverlay(!showOverlay)}
                                    >
                                        {showOverlay ? <Eye size={20} color="#FFF" /> : <EyeOff size={20} color="#FFF" />}
                                    </TouchableOpacity>
                                    <TouchableOpacity
                                        style={{ position: 'absolute', bottom: 16, left: 60, backgroundColor: 'rgba(0,0,0,0.6)', padding: 8, borderRadius: 20 }}
                                        onPress={() => setShowBatTrail(!showBatTrail)}
                                    >
                                        <Text style={{ color: '#FFF', fontSize: 16, fontWeight: 'bold' }}>🏏</Text>
                                    </TouchableOpacity>
                                    <TouchableOpacity
                                        style={{ position: 'absolute', bottom: 16, right: 16, backgroundColor: 'rgba(0,0,0,0.6)', padding: 8, borderRadius: 20 }}
                                        onPress={() => setIsFullscreen(true)}
                                    >
                                        <Maximize2 size={20} color="#FFF" />
                                    </TouchableOpacity>
                                </View>

                                {/* DM-59: Video Scrubbing Controls */}
                                {videoUri && player && (
                                    <View style={styles.scrubControls}>
                                        {/* Frame Info */}
                                        <View style={styles.frameInfo}>
                                            <Text style={styles.frameText}>
                                                Frame {currentFrameIndexRef.current + 1} / {result.total_frames}
                                            </Text>
                                            <Text style={styles.timeText}>
                                                {formatTime(player.currentTime)} / {formatTime(player.duration)}
                                            </Text>
                                        </View>

                                        {/* Step Controls + Slider */}
                                        <View style={styles.scrubRow}>
                                            {/* Step Backward */}
                                            <TouchableOpacity
                                                style={styles.stepButton}
                                                onPress={stepBackward}
                                            >
                                                <ChevronLeft size={24} color={THEME.primary} />
                                            </TouchableOpacity>

                                            {/* Slider */}
                                            <Slider
                                                style={styles.scrubSlider}
                                                minimumValue={0}
                                                maximumValue={1}
                                                value={scrubPosition}
                                                onValueChange={handleScrubChange}
                                                onSlidingStart={() => {
                                                    setIsScrubbing(true);
                                                    player.pause();
                                                }}
                                                onSlidingComplete={handleScrubComplete}
                                                minimumTrackTintColor={THEME.accent}
                                                maximumTrackTintColor={THEME.border}
                                                thumbTintColor={THEME.accent}
                                            />

                                            {/* Step Forward */}
                                            <TouchableOpacity
                                                style={styles.stepButton}
                                                onPress={stepForward}
                                            >
                                                <ChevronRight size={24} color={THEME.primary} />
                                            </TouchableOpacity>
                                        </View>
                                    </View>
                                )}

                                {/* Attack Angle Metric */}
                                {attackAngle !== null && (
                                    <View style={{ marginTop: 16, backgroundColor: THEME.card, padding: 16, borderRadius: 16, shadowColor: '#000', shadowOffset: { width: 0, height: 2 }, shadowOpacity: 0.05, shadowRadius: 4, elevation: 2 }}>
                                        <Text style={{ fontSize: 14, color: THEME.subtext, fontWeight: '600', marginBottom: 4 }}>Attack Angle</Text>
                                        <Text style={{ fontSize: 28, color: THEME.primary, fontWeight: 'bold' }}>{attackAngle}°</Text>
                                        <Text style={{ fontSize: 12, color: THEME.subtext, marginTop: 4 }}>
                                            {attackAngle > 0 ? '↗ Upward swing' : attackAngle < 0 ? '↘ Downward swing' : '→ Level swing'}
                                        </Text>
                                    </View>
                                )}

                                {/* Action Buttons */}
                                <View style={styles.actionBar}>
                                    <TouchableOpacity style={styles.actionBtn} onPress={handleReset}>
                                        <X size={20} color={THEME.primary} />
                                        <Text style={styles.actionBtnText}>New Swing</Text>
                                    </TouchableOpacity>
                                    {/* Download button removed as requested */}
                                </View>
                            </View>
                        )}
                    </View>

                    {/* --- Unified Floating Error Toast (Bottom) --- */}
                    {error && (
                        <View style={styles.errorToast}>
                            <AlertCircle size={24} color="#EF4444" />
                            <View style={styles.errorTextContent}>
                                <Text style={styles.errorTitle}>Analysis Failed</Text>
                                <Text style={styles.errorMsg} numberOfLines={1}>{error}</Text>
                            </View>
                            <TouchableOpacity style={styles.retryPill} onPress={pickVideo}>
                                <Text style={styles.retryText}>RETRY</Text>
                            </TouchableOpacity>
                            <TouchableOpacity style={{ marginLeft: 12 }} onPress={() => setError(null)}>
                                <X size={18} color="#64748B" />
                            </TouchableOpacity>
                        </View>
                    )}

                    {/* Compression Progress Overlay */}
                    {isCompressing && (
                        <View style={styles.compressionOverlay}>
                            <View style={styles.compressionModal}>
                                <ActivityIndicator size="large" color={THEME.accent} />
                                <Text style={styles.compressionText}>
                                    Optimizing Video...
                                </Text>
                                <Text style={styles.compressionProgress}>
                                    {compressionProgress}%
                                </Text>
                                <Text style={styles.compressionSubtext}>
                                    Preparing for upload
                                </Text>
                            </View>
                        </View>
                    )}

                </SafeAreaView>
            )}
        </SafeAreaProvider>
    );
}

export default MainApp;