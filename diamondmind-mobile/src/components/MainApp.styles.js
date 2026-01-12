import { StyleSheet } from 'react-native';
import { THEME } from '../styles/theme';

export const styles = StyleSheet.create({
    container: { flex: 1, backgroundColor: THEME.bg },

    // Header
    headerContainer: { paddingHorizontal: 24, paddingTop: 20, paddingBottom: 30 },
    badge: { flexDirection: 'row', alignItems: 'center', alignSelf: 'flex-start', backgroundColor: '#EFF6FF', paddingHorizontal: 10, paddingVertical: 4, borderRadius: 12, marginBottom: 12 },
    badgeText: { color: THEME.accent, fontSize: 12, fontWeight: '700', marginLeft: 6 },
    title: {
        fontSize: 34,
        fontWeight: 'bold',
        color: THEME.primary,
        letterSpacing: 0.5
    },
    subtitle: { fontSize: 17, color: THEME.subtext, marginTop: 4, fontWeight: '500' },

    // Upload Card
    uploadCard: {
        backgroundColor: THEME.card,
        borderRadius: 24,
        padding: 32,
        alignItems: 'center',
        marginHorizontal: 24,
        shadowColor: '#000',
        shadowOffset: { width: 0, height: 10 },
        shadowOpacity: 0.08,
        shadowRadius: 20,
        elevation: 6,
        borderWidth: 1,
        borderColor: 'rgba(255,255,255,0.5)'
    },
    iconCircle: { width: 80, height: 80, borderRadius: 40, backgroundColor: '#F1F5F9', alignItems: 'center', justifyContent: 'center', marginBottom: 20 },
    ctaText: { fontSize: 20, fontWeight: '700', color: THEME.primary, marginBottom: 8 },
    ctaSubtext: { fontSize: 14, color: THEME.subtext, textAlign: 'center', marginBottom: 24, lineHeight: 20 },
    primaryButton: { backgroundColor: THEME.primary, paddingVertical: 16, paddingHorizontal: 32, borderRadius: 16, flexDirection: 'row', alignItems: 'center', width: '100%', justifyContent: 'center' },
    primaryButtonText: { color: '#FFF', fontSize: 16, fontWeight: '700', marginRight: 8 },

    // Loading State
    statusCard: { flex: 1, justifyContent: 'center', alignItems: 'center', padding: 40 },
    loadingText: { marginTop: 24, fontSize: 18, fontWeight: '700', color: THEME.primary },
    progressTrack: { width: '100%', height: 8, backgroundColor: '#E2E8F0', borderRadius: 4, marginTop: 16, overflow: 'hidden' },
    progressBar: { height: '100%', backgroundColor: THEME.accent },
    cancelBtn: { marginTop: 32, paddingVertical: 10, paddingHorizontal: 20 },
    cancelText: { color: THEME.subtext, fontWeight: '600' },

    // Results View
    resultsContainer: { flex: 1, padding: 20 },
    videoFrame: {
        width: '100%',
        backgroundColor: '#000',
        borderRadius: 24,
        overflow: 'hidden',
        shadowColor: '#000',
        shadowOffset: { width: 0, height: 4 },
        shadowOpacity: 0.2,
        shadowRadius: 12,
        elevation: 8,
        borderWidth: 1,
        borderColor: '#333'
    },

    // Bottom Action Bar
    actionBar: { flexDirection: 'row', marginTop: 20, gap: 12 },
    actionBtn: { flex: 1, backgroundColor: THEME.card, padding: 16, borderRadius: 16, alignItems: 'center', flexDirection: 'row', justifyContent: 'center', shadowColor: '#000', shadowOffset: { width: 0, height: 2 }, shadowOpacity: 0.05, shadowRadius: 4, elevation: 2 },
    actionBtnText: { color: THEME.primary, fontWeight: '700', marginLeft: 8 },

    // Floating Error Toast
    errorToast: {
        position: 'absolute',
        bottom: 40,
        left: 20,
        right: 20,
        backgroundColor: '#1E293B',
        borderRadius: 16,
        padding: 16,
        flexDirection: 'row',
        alignItems: 'center',
        shadowColor: '#000',
        shadowOffset: { width: 0, height: 4 },
        shadowOpacity: 0.3,
        shadowRadius: 8,
        elevation: 10,
        zIndex: 999
    },
    errorTextContent: { flex: 1, marginLeft: 12 },
    errorTitle: { color: '#FFF', fontWeight: '700', fontSize: 14 },
    errorMsg: { color: '#94A3B8', fontSize: 12, marginTop: 2 },
    retryPill: { backgroundColor: THEME.accent, paddingVertical: 10, paddingHorizontal: 20, borderRadius: 12 },
    retryText: { color: '#FFF', fontWeight: '700', fontSize: 14 },

    // Compression Overlay
    compressionOverlay: {
        position: 'absolute',
        top: 0,
        left: 0,
        right: 0,
        bottom: 0,
        backgroundColor: 'rgba(0, 0, 0, 0.85)',
        justifyContent: 'center',
        alignItems: 'center',
        zIndex: 1000,
    },
    compressionModal: {
        backgroundColor: THEME.card,
        borderRadius: 24,
        padding: 40,
        alignItems: 'center',
        minWidth: 240,
        shadowColor: '#000',
        shadowOffset: { width: 0, height: 10 },
        shadowOpacity: 0.3,
        shadowRadius: 20,
        elevation: 10,
    },
    compressionText: {
        fontSize: 18,
        fontWeight: '700',
        color: THEME.primary,
        marginTop: 20,
    },
    compressionProgress: {
        fontSize: 32,
        fontWeight: '800',
        color: THEME.accent,
        marginTop: 12,
    },
    compressionSubtext: {
        fontSize: 14,
        color: THEME.subtext,
        marginTop: 8,
    },

    // Scrubbing Controls
    scrubControls: {
        backgroundColor: THEME.card,
        borderRadius: 16,
        padding: 16,
        marginHorizontal: 20,
        marginTop: 16,
        shadowColor: '#000',
        shadowOffset: { width: 0, height: 2 },
        shadowOpacity: 0.1,
        shadowRadius: 8,
        elevation: 3,
    },
    frameInfo: {
        flexDirection: 'row',
        justifyContent: 'space-between',
        marginBottom: 12,
    },
    frameText: {
        fontSize: 14,
        fontWeight: '600',
        color: THEME.primary,
    },
    timeText: {
        fontSize: 14,
        color: THEME.subtext,
    },
    scrubRow: {
        flexDirection: 'row',
        alignItems: 'center',
        gap: 12,
    },
    stepButton: {
        width: 40,
        height: 40,
        borderRadius: 20,
        backgroundColor: THEME.bg,
        justifyContent: 'center',
        alignItems: 'center',
        borderWidth: 1,
        borderColor: THEME.border,
    },
    scrubSlider: {
        flex: 1,
        height: 40,
    },

    // Fullscreen
    fullscreenContainer: { position: 'absolute', top: 0, left: 0, right: 0, bottom: 0, backgroundColor: '#000', zIndex: 1000 },
    closeFab: { position: 'absolute', top: 60, right: 24, backgroundColor: 'rgba(255,255,255,0.2)', width: 44, height: 44, borderRadius: 22, alignItems: 'center', justifyContent: 'center' }
});
