"""
Enhanced Video Analysis Module - Streaming & Batch Processing
Supports real-time streaming, batch processing, and comprehensive video analysis
"""

import cv2
import numpy as np
from pathlib import Path
from typing import List, Dict, Tuple, Optional, Generator, Callable
import tempfile
from concurrent.futures import ThreadPoolExecutor, as_completed
import logging
import time
import threading
from queue import Queue
import json
from datetime import datetime

logger = logging.getLogger(__name__)


class StreamingVideoAnalyzer:
    """Real-time streaming video analysis"""

    def __init__(self, buffer_size: int = 30, fps_target: int = 10):
        self.buffer_size = buffer_size
        self.fps_target = fps_target
        self.frame_buffer = []
        self.analysis_results = []
        self.is_streaming = False
        self.stream_thread = None
        self.callbacks = []

    def add_callback(self, callback: Callable):
        """Add callback for real-time results"""
        self.callbacks.append(callback)

    def start_stream_analysis(self, video_source: str) -> Generator[Dict, None, None]:
        """Start streaming analysis from video source"""
        self.is_streaming = True

        def analyze_stream():
            cap = cv2.VideoCapture(video_source)
            if not cap.isOpened():
                logger.error(f"Cannot open video source: {video_source}")
                return

            frame_count = 0
            fps = cap.get(cv2.CAP_PROP_FPS)
            frame_interval = int(fps / self.fps_target) if fps > 0 else 1

            while self.is_streaming and cap.isOpened():
                ret, frame = cap.read()
                if not ret:
                    break

                frame_count += 1

                # Process every nth frame based on target FPS
                if frame_count % frame_interval == 0:
                    result = self._analyze_frame(frame, frame_count)
                    self.analysis_results.append(result)

                    # Notify callbacks
                    for callback in self.callbacks:
                        try:
                            callback(result)
                        except Exception as e:
                            logger.error(f"Callback error: {e}")

                    yield result

                    # Maintain buffer size
                    if len(self.frame_buffer) >= self.buffer_size:
                        self.frame_buffer.pop(0)
                    self.frame_buffer.append(frame)

            cap.release()

        return analyze_stream()

    def _analyze_frame(self, frame: np.ndarray, frame_number: int) -> Dict:
        """Analyze individual frame for deepfakes"""
        try:
            # Convert to RGB for analysis
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

            # Basic analysis (expand this with actual ML models)
            analysis = {
                'frame_number': frame_number,
                'timestamp': datetime.now().isoformat(),
                'dimensions': frame.shape[:2],
                'analysis': {
                    'face_detected': self._detect_faces_basic(frame),
                    'motion_artifacts': self._detect_motion_artifacts(frame),
                    'color_consistency': self._check_color_consistency(frame),
                    'edge_artifacts': self._detect_edge_artifacts(frame),
                    'temporal_consistency': self._check_temporal_consistency(frame),
                    'compression_artifacts': self._detect_compression_artifacts(frame),
                    'lighting_consistency': self._check_lighting_consistency(frame),
                    'texture_analysis': self._analyze_texture_patterns(frame),
                    'frequency_domain': self._analyze_frequency_domain(frame),
                    'metadata_analysis': self._analyze_frame_metadata(frame)
                }
            }

            # Calculate overall confidence
            analysis['confidence_score'] = self._calculate_overall_confidence(analysis['analysis'])
            analysis['classification'] = 'Real' if analysis['confidence_score'] > 0.7 else 'Deepfake' if analysis['confidence_score'] < 0.3 else 'Suspicious'

            return analysis

        except Exception as e:
            logger.error(f"Frame analysis error: {e}")
            return {
                'frame_number': frame_number,
                'error': str(e),
                'confidence_score': 0.5,
                'classification': 'Error'
            }

    def _detect_faces_basic(self, frame: np.ndarray) -> Dict:
        """Basic face detection"""
        try:
            face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            faces = face_cascade.detectMultiScale(gray, 1.1, 4)

            return {
                'detected': len(faces) > 0,
                'count': len(faces),
                'locations': faces.tolist() if len(faces) > 0 else []
            }
        except:
            return {'detected': False, 'count': 0, 'locations': []}

    def _detect_motion_artifacts(self, frame: np.ndarray) -> Dict:
        """Detect motion-related artifacts"""
        try:
            # Analyze frame differences and motion blur
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            laplacian_var = cv2.Laplacian(gray, cv2.CV_64F).var()

            return {
                'blur_detected': laplacian_var < 100,
                'sharpness_score': min(laplacian_var / 500, 1.0),
                'motion_artifacts': laplacian_var < 50
            }
        except:
            return {'blur_detected': False, 'sharpness_score': 0.5, 'motion_artifacts': False}

    def _check_color_consistency(self, frame: np.ndarray) -> Dict:
        """Check color consistency and anomalies"""
        try:
            # Analyze color distribution
            hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
            hist = cv2.calcHist([hsv], [0, 1, 2], None, [8, 8, 8], [0, 180, 0, 256, 0, 256])

            # Check for unnatural color distributions
            uniformity = np.std(hist) / np.mean(hist) if np.mean(hist) > 0 else 1.0

            return {
                'color_uniformity': uniformity,
                'unnatural_colors': uniformity > 2.0,
                'color_balance': self._check_color_balance(frame)
            }
        except:
            return {'color_uniformity': 1.0, 'unnatural_colors': False, 'color_balance': True}

    def _detect_edge_artifacts(self, frame: np.ndarray) -> Dict:
        """Detect edge artifacts common in deepfakes"""
        try:
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            edges = cv2.Canny(gray, 100, 200)

            # Analyze edge consistency
            edge_density = np.sum(edges > 0) / edges.size
            edge_uniformity = np.std(edges) / np.mean(edges) if np.mean(edges) > 0 else 1.0

            return {
                'edge_density': edge_density,
                'edge_uniformity': edge_uniformity,
                'artifact_detected': edge_uniformity > 1.5 or edge_density < 0.01
            }
        except:
            return {'edge_density': 0.0, 'edge_uniformity': 1.0, 'artifact_detected': False}

    def _check_temporal_consistency(self, frame: np.ndarray) -> Dict:
        """Check temporal consistency with previous frames"""
        if len(self.frame_buffer) < 2:
            return {'consistent': True, 'difference_score': 0.0}

        try:
            prev_frame = self.frame_buffer[-1]
            diff = cv2.absdiff(frame, prev_frame)
            mean_diff = np.mean(diff)

            return {
                'consistent': mean_diff < 50,
                'difference_score': mean_diff / 255.0,
                'temporal_artifacts': mean_diff > 100
            }
        except:
            return {'consistent': True, 'difference_score': 0.0, 'temporal_artifacts': False}

    def _detect_compression_artifacts(self, frame: np.ndarray) -> Dict:
        """Detect compression artifacts"""
        try:
            # Analyze for JPEG-like compression artifacts
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

            # Check for blocking artifacts (8x8 blocks)
            h, w = gray.shape
            block_artifacts = 0

            for i in range(0, h-8, 8):
                for j in range(0, w-8, 8):
                    block = gray[i:i+8, j:j+8]
                    if np.std(block) < 5:  # Very uniform blocks indicate compression
                        block_artifacts += 1

            compression_ratio = block_artifacts / ((h//8) * (w//8))

            return {
                'compression_artifacts': compression_ratio > 0.3,
                'compression_score': compression_ratio,
                'block_uniformity': compression_ratio
            }
        except:
            return {'compression_artifacts': False, 'compression_score': 0.0, 'block_uniformity': 0.0}

    def _check_lighting_consistency(self, frame: np.ndarray) -> Dict:
        """Check lighting consistency"""
        try:
            # Analyze lighting patterns
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

            # Divide frame into regions and check lighting consistency
            h, w = gray.shape
            regions = [
                gray[:h//2, :w//2], gray[:h//2, w//2:],  # Top halves
                gray[h//2:, :w//2], gray[h//2:, w//2:]   # Bottom halves
            ]

            means = [np.mean(region) for region in regions]
            lighting_variance = np.std(means)

            return {
                'lighting_consistent': lighting_variance < 30,
                'lighting_variance': lighting_variance,
                'unnatural_lighting': lighting_variance > 50
            }
        except:
            return {'lighting_consistent': True, 'lighting_variance': 0.0, 'unnatural_lighting': False}

    def _analyze_texture_patterns(self, frame: np.ndarray) -> Dict:
        """Analyze texture patterns for manipulation"""
        try:
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

            # Use Gabor filters to detect texture inconsistencies
            from skimage.filters import gabor
            from skimage import img_as_float

            float_img = img_as_float(gray)
            gabor_result = gabor(float_img, frequency=0.6)

            # Analyze texture uniformity
            texture_energy = np.mean(np.abs(gabor_result[0]))
            texture_uniformity = np.std(gabor_result[0])

            return {
                'texture_energy': texture_energy,
                'texture_uniformity': texture_uniformity,
                'suspicious_texture': texture_uniformity > 0.8
            }
        except:
            return {'texture_energy': 0.5, 'texture_uniformity': 0.5, 'suspicious_texture': False}

    def _analyze_frequency_domain(self, frame: np.ndarray) -> Dict:
        """Analyze frequency domain for manipulation traces"""
        try:
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

            # FFT analysis
            f = np.fft.fft2(gray)
            fshift = np.fft.fftshift(f)
            magnitude_spectrum = 20 * np.log(np.abs(fshift) + 1)

            # Analyze frequency distribution
            center_region = magnitude_spectrum[magnitude_spectrum.shape[0]//2-50:magnitude_spectrum.shape[0]//2+50,
                                             magnitude_spectrum.shape[1]//2-50:magnitude_spectrum.shape[1]//2+50]

            low_freq_energy = np.mean(center_region)
            high_freq_energy = np.mean(magnitude_spectrum) - low_freq_energy

            return {
                'low_freq_energy': low_freq_energy,
                'high_freq_energy': high_freq_energy,
                'frequency_ratio': high_freq_energy / (low_freq_energy + 1e-10),
                'suspicious_frequency': abs(high_freq_energy - low_freq_energy) > 1000
            }
        except:
            return {'low_freq_energy': 0.0, 'high_freq_energy': 0.0, 'frequency_ratio': 1.0, 'suspicious_frequency': False}

    def _analyze_frame_metadata(self, frame: np.ndarray) -> Dict:
        """Analyze frame metadata and properties"""
        try:
            h, w = frame.shape[:2]

            # Analyze color channels
            b, g, r = cv2.split(frame)
            channel_stats = {
                'r_mean': np.mean(r), 'g_mean': np.mean(g), 'b_mean': np.mean(b),
                'r_std': np.std(r), 'g_std': np.std(g), 'b_std': np.std(b)
            }

            # Check for channel inconsistencies
            channel_variance = np.std([channel_stats['r_mean'], channel_stats['g_mean'], channel_stats['b_mean']])

            return {
                'dimensions': (w, h),
                'aspect_ratio': w / h if h > 0 else 0,
                'channel_stats': channel_stats,
                'channel_consistency': channel_variance < 20,
                'color_depth': frame.dtype,
                'suspicious_metadata': channel_variance > 50
            }
        except:
            return {'dimensions': (0, 0), 'aspect_ratio': 0, 'channel_stats': {}, 'channel_consistency': True, 'color_depth': 'unknown', 'suspicious_metadata': False}

    def _check_color_balance(self, frame: np.ndarray) -> bool:
        """Check if colors are properly balanced"""
        try:
            b, g, r = cv2.split(frame)
            means = [np.mean(b), np.mean(g), np.mean(r)]
            std_dev = np.std(means)
            return std_dev < 30  # Reasonable color balance
        except:
            return True

    def _calculate_overall_confidence(self, analysis_results: Dict) -> float:
        """Calculate overall confidence score from all analyses"""
        try:
            scores = []

            # Face detection (higher weight)
            if analysis_results.get('face_detected', {}).get('detected', False):
                scores.append(0.8)  # Faces detected, likely real
            else:
                scores.append(0.3)  # No faces, could be suspicious

            # Motion artifacts
            if analysis_results.get('motion_artifacts', {}).get('motion_artifacts', False):
                scores.append(0.2)
            else:
                scores.append(0.7)

            # Color consistency
            if analysis_results.get('color_consistency', {}).get('unnatural_colors', False):
                scores.append(0.3)
            else:
                scores.append(0.8)

            # Edge artifacts
            if analysis_results.get('edge_artifacts', {}).get('artifact_detected', False):
                scores.append(0.2)
            else:
                scores.append(0.8)

            # Temporal consistency
            if analysis_results.get('temporal_consistency', {}).get('temporal_artifacts', False):
                scores.append(0.3)
            else:
                scores.append(0.8)

            # Compression artifacts
            if analysis_results.get('compression_artifacts', {}).get('compression_artifacts', False):
                scores.append(0.4)
            else:
                scores.append(0.7)

            # Lighting consistency
            if analysis_results.get('lighting_consistency', {}).get('unnatural_lighting', False):
                scores.append(0.3)
            else:
                scores.append(0.8)

            # Texture analysis
            if analysis_results.get('texture_analysis', {}).get('suspicious_texture', False):
                scores.append(0.3)
            else:
                scores.append(0.8)

            # Frequency domain
            if analysis_results.get('frequency_domain', {}).get('suspicious_frequency', False):
                scores.append(0.3)
            else:
                scores.append(0.8)

            # Metadata analysis
            if analysis_results.get('metadata_analysis', {}).get('suspicious_metadata', False):
                scores.append(0.3)
            else:
                scores.append(0.8)

            # Calculate weighted average
            if scores:
                return np.mean(scores)
            else:
                return 0.5

        except Exception as e:
            logger.error(f"Confidence calculation error: {e}")
            return 0.5

    def stop_streaming(self):
        """Stop streaming analysis"""
        self.is_streaming = False
        if self.stream_thread and self.stream_thread.is_alive():
            self.stream_thread.join(timeout=5)


class BatchVideoProcessor:
    """Batch processing for multiple videos"""

    def __init__(self, max_workers: int = 4):
        self.max_workers = max_workers
        self.results = {}
        self.progress_callbacks = []

    def add_progress_callback(self, callback: Callable):
        """Add callback for progress updates"""
        self.progress_callbacks.append(callback)

    def process_batch(self, video_paths: List[str], config: Dict = None) -> Dict[str, Dict]:
        """Process multiple videos in batch"""
        if config is None:
            config = {
                'sampling_rate': 5,
                'max_frames': 100,
                'enable_streaming': False
            }

        results = {}

        def process_single_video(video_path: str) -> Tuple[str, Dict]:
            """Process a single video"""
            try:
                analyzer = StreamingVideoAnalyzer()

                # For batch processing, we'll analyze key frames
                cap = cv2.VideoCapture(video_path)
                if not cap.isOpened():
                    return video_path, {'error': 'Cannot open video'}

                total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
                fps = cap.get(cv2.CAP_PROP_FPS)

                # Sample frames throughout the video
                frame_indices = np.linspace(0, total_frames-1,
                                          min(config['max_frames'], total_frames),
                                          dtype=int)

                frame_results = []
                for idx in frame_indices:
                    cap.set(cv2.CAP_PROP_POS_FRAMES, idx)
                    ret, frame = cap.read()
                    if ret:
                        result = analyzer._analyze_frame(frame, idx)
                        frame_results.append(result)

                cap.release()

                # Aggregate results
                if frame_results:
                    avg_confidence = np.mean([r['confidence_score'] for r in frame_results])
                    classifications = [r['classification'] for r in frame_results]

                    # Determine overall classification
                    real_count = classifications.count('Real')
                    deepfake_count = classifications.count('Deepfake')
                    suspicious_count = classifications.count('Suspicious')

                    if real_count > deepfake_count and real_count > suspicious_count:
                        overall_classification = 'Real'
                    elif deepfake_count > real_count and deepfake_count > suspicious_count:
                        overall_classification = 'Deepfake'
                    else:
                        overall_classification = 'Suspicious'

                    result = {
                        'video_path': video_path,
                        'total_frames_analyzed': len(frame_results),
                        'avg_confidence': avg_confidence,
                        'classification': overall_classification,
                        'frame_breakdown': {
                            'real': real_count,
                            'deepfake': deepfake_count,
                            'suspicious': suspicious_count
                        },
                        'video_info': {
                            'total_frames': total_frames,
                            'fps': fps,
                            'duration': total_frames / fps if fps > 0 else 0
                        },
                        'detailed_results': frame_results[:10]  # First 10 frames details
                    }
                else:
                    result = {'error': 'No frames could be analyzed'}

                return video_path, result

            except Exception as e:
                logger.error(f"Batch processing error for {video_path}: {e}")
                return video_path, {'error': str(e)}

        # Process videos in parallel
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            futures = [executor.submit(process_single_video, path) for path in video_paths]

            for i, future in enumerate(as_completed(futures)):
                video_path, result = future.result()
                results[video_path] = result

                # Update progress
                progress = (i + 1) / len(video_paths)
                for callback in self.progress_callbacks:
                    try:
                        callback(progress, video_path, result)
                    except Exception as e:
                        logger.error(f"Progress callback error: {e}")

        return results


class EnhancedVideoAnalysisEngine:
    """Enhanced video analysis engine with streaming and batch capabilities"""

    def __init__(self):
        self.streaming_analyzer = StreamingVideoAnalyzer()
        self.batch_processor = BatchVideoProcessor()

    def analyze_video_streaming(self, video_source: str, callbacks: List[Callable] = None) -> Generator[Dict, None, None]:
        """Analyze video in streaming mode"""
        if callbacks:
            for callback in callbacks:
                self.streaming_analyzer.add_callback(callback)

        return self.streaming_analyzer.start_stream_analysis(video_source)

    def analyze_video_batch(self, video_paths: List[str], config: Dict = None, progress_callbacks: List[Callable] = None) -> Dict[str, Dict]:
        """Analyze multiple videos in batch"""
        if progress_callbacks:
            for callback in progress_callbacks:
                self.batch_processor.add_progress_callback(callback)

        return self.batch_processor.process_batch(video_paths, config)

    def stop_streaming(self):
        """Stop any ongoing streaming analysis"""
        self.streaming_analyzer.stop_streaming()