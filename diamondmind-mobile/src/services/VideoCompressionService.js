import * as FileSystem from 'expo-file-system';
import * as MediaLibrary from 'expo-media-library';

export class VideoCompressionService {
    /**
     * Compress video to 720p using expo-av
     * Note: Expo Go has limited compression capabilities
     * For production, consider using expo-video-thumbnails or custom dev client
     * 
     * @param {string} sourceUri - Original video URI
     * @param {function} onProgress - Progress callback (0-100)
     * @returns {Promise<string>} - Compressed video URI (or original if skipped)
     */
    static async compressVideo(sourceUri, onProgress = () => { }) {
        try {
            console.log('🎬 Starting video compression check:', sourceUri);

            // Get file info
            const fileInfo = await FileSystem.getInfoAsync(sourceUri);
            const fileSizeMB = fileInfo.size / (1024 * 1024);

            console.log(`📊 Original file size: ${fileSizeMB.toFixed(2)} MB`);

            // EXPO GO LIMITATION: We can't actually compress in Expo Go
            // For now, we'll just skip large files or return original
            // In production (with custom dev client), we'd use FFmpeg or native compression

            if (fileSizeMB < 50) {
                console.log('✅ File size acceptable for Expo Go, proceeding with original');
                onProgress(100); // Instant "compression"
                return sourceUri;
            }

            // For files > 50MB, warn but still proceed
            console.warn('⚠️ Large file detected. Compression not available in Expo Go.');
            console.warn('💡 For production, build with EAS or use custom dev client for compression.');
            onProgress(100);
            return sourceUri;

        } catch (error) {
            console.error('❌ Compression check failed:', error);
            onProgress(100);
            return sourceUri;
        }
    }

    /**
     * Clean up temporary compressed files
     */
    static async cleanupTempFiles() {
        try {
            const cacheDir = FileSystem.cacheDirectory;
            const files = await FileSystem.readDirectoryAsync(cacheDir);

            // Delete old compressed videos (older than 1 hour)
            const oneHourAgo = Date.now() - (60 * 60 * 1000);

            for (const file of files) {
                if (file.startsWith('compressed_') || file.startsWith('video_')) {
                    const filePath = `${cacheDir}${file}`;
                    const info = await FileSystem.getInfoAsync(filePath);

                    if (info.modificationTime * 1000 < oneHourAgo) {
                        await FileSystem.deleteAsync(filePath, { idempotent: true });
                        console.log('🗑️ Cleaned up old file:', file);
                    }
                }
            }
        } catch (error) {
            console.error('⚠️ Cleanup failed:', error);
            // Non-critical, don't throw
        }
    }
}
