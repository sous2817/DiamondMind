import React from 'react';
import { View, StyleSheet } from 'react-native';
import Svg, { Polyline, Circle } from 'react-native-svg';

const BatTrailOverlay = ({
    frames,
    currentFrameIndex,
    videoWidth,
    videoHeight,
    containerWidth,
    containerHeight
}) => {
    if (!frames || !frames.length || !videoWidth || !videoHeight || !containerWidth || !containerHeight) {
        return null;
    }

    // Calculate video aspect ratios
    const videoAspect = videoWidth / videoHeight;
    const containerAspect = containerWidth / containerHeight;

    // Calculate the actual video display dimensions when using contentMode="contain"
    let displayWidth, displayHeight, offsetX, offsetY;

    if (videoAspect > containerAspect) {
        // Video is wider - letterbox top/bottom
        displayWidth = containerWidth;
        displayHeight = containerWidth / videoAspect;
        offsetX = 0;
        offsetY = (containerHeight - displayHeight) / 2;
    } else {
        // Video is taller - letterbox left/right
        displayHeight = containerHeight;
        displayWidth = containerHeight * videoAspect;
        offsetX = (containerWidth - displayWidth) / 2;
        offsetY = 0;
    }

    // Extract bat positions up to current frame (show trail behind current position)
    // Only show last 40 frames for cleaner visualization
    const trailLength = 40;
    const startIndex = Math.max(0, currentFrameIndex - trailLength);
    const endIndex = currentFrameIndex + 1; // Include current frame

    const batPositions = frames
        .slice(startIndex, endIndex)
        .map((frame, relativeIndex) => ({
            pos: frame.bat_position,
            frameIndex: startIndex + relativeIndex,
            confidence: frame.bat_position?.confidence // YOLO confidence if available
        }))
        .filter(item => item.pos !== null && item.pos !== undefined);

    // DEBUG: Log bat detection stats (only once)
    if (currentFrameIndex === 0 && batPositions.length > 0) {
        const totalBatFrames = frames.filter(f => f.bat_position).length;
        console.log(`🏏 Bat Trail: ${totalBatFrames}/${frames.length} frames (${((totalBatFrames / frames.length) * 100).toFixed(1)}%)`);
    }

    if (batPositions.length === 0) {
        // No bat positions detected at all
        return null;
    }

    // Get current bat position for highlighting
    const currentBatPos = frames[currentFrameIndex]?.bat_position;

    return (
        <View style={StyleSheet.absoluteFill} pointerEvents="none">
            <Svg
                height="100%"
                width="100%"
                viewBox={`0 0 ${containerWidth} ${containerHeight}`}
            >
                {/* Bat trail as fading dots - recent = bright, old = transparent */}
                {batPositions.map((item, index) => {
                    // Calculate opacity: newest dots are bright (1.0), oldest fade to 0.2
                    const age = batPositions.length - index - 1; // 0 = newest, length-1 = oldest
                    const opacity = 1.0 - (age / batPositions.length) * 0.8; // Range: 1.0 → 0.2

                    // Calculate size: newer dots slightly larger (reduced by 50%)
                    const size = 4 - (age / batPositions.length) * 1.5; // Range: 4 → 2.5

                    // Color based on confidence (if available from YOLO)
                    // High confidence = yellow, low confidence = orange
                    const color = item.confidence
                        ? (item.confidence > 0.5 ? '#FFD700' : '#FFA500')
                        : '#FFD700';

                    return (
                        <Circle
                            key={item.frameIndex}
                            cx={offsetX + (item.pos.x * displayWidth)}
                            cy={offsetY + (item.pos.y * displayHeight)}
                            r={size}
                            fill={color}
                            opacity={opacity}
                        />
                    );
                })}

                {/* Current bat position (highlighted - larger and bright red) */}
                {currentBatPos && (
                    <Circle
                        cx={offsetX + (currentBatPos.x * displayWidth)}
                        cy={offsetY + (currentBatPos.y * displayHeight)}
                        r="5"
                        fill="#FF0000"
                        opacity="1"
                        stroke="#FFFFFF"
                        strokeWidth="1"
                    />
                )}
            </Svg>
        </View>
    );
};

// Memoize to prevent unnecessary re-renders
export default React.memo(BatTrailOverlay, (prevProps, nextProps) => {
    return prevProps.currentFrameIndex === nextProps.currentFrameIndex &&
        prevProps.containerWidth === nextProps.containerWidth &&
        prevProps.containerHeight === nextProps.containerHeight;
});
