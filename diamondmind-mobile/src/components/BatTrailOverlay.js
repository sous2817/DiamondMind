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

    // Extract ALL bat positions from frames (show complete trail)
    const batPositions = frames
        .map(frame => frame.bat_position)
        .filter(pos => pos !== null && pos !== undefined);

    // DEBUG: Log bat detection stats (only once)
    if (currentFrameIndex === 0 && batPositions.length > 0) {
        console.log(`🏏 Bat Trail: ${batPositions.length}/${frames.length} frames (${((batPositions.length / frames.length) * 100).toFixed(1)}%)`);
    }

    if (batPositions.length === 0) {
        // No bat positions detected at all
        return null;
    }

    // Convert normalized coordinates to screen pixels
    const points = batPositions.map(pos => {
        const x = offsetX + (pos.x * displayWidth);
        const y = offsetY + (pos.y * displayHeight);
        return `${x},${y}`;
    }).join(' ');

    // Get current bat position for highlighting
    const currentBatPos = frames[currentFrameIndex]?.bat_position;

    return (
        <View style={StyleSheet.absoluteFill} pointerEvents="none">
            <Svg
                height="100%"
                width="100%"
                viewBox={`0 0 ${containerWidth} ${containerHeight}`}
            >
                {/* Bat trail (polyline) - show if we have at least 2 points */}
                {batPositions.length >= 2 && (
                    <Polyline
                        points={points}
                        fill="none"
                        stroke="#FFD700"
                        strokeWidth="4"
                        strokeOpacity="0.9"
                        strokeLinecap="round"
                        strokeLinejoin="round"
                    />
                )}

                {/* Draw all bat positions as circles for visibility */}
                {batPositions.map((pos, index) => (
                    <Circle
                        key={index}
                        cx={offsetX + (pos.x * displayWidth)}
                        cy={offsetY + (pos.y * displayHeight)}
                        r="6"
                        fill="#FFD700"
                        opacity="0.6"
                    />
                ))}

                {/* Current bat position (highlighted - larger and red) */}
                {currentBatPos && (
                    <Circle
                        cx={offsetX + (currentBatPos.x * displayWidth)}
                        cy={offsetY + (currentBatPos.y * displayHeight)}
                        r="12"
                        fill="#FF0000"
                        opacity="1"
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
