"""
Video Deepfake Detection Module
Handles video processing, frame extraction, and deepfake detection
"""

import cv2
import numpy as np
from pathlib import Path
from typing import List, Dict, Tuple, Optional
import tempfile
from concurrent.futures import ThreadPoolExecutor
import logging

logger = logging.getLogger(__name__)


class VideoProcessor:
    """Process and extract frames from video files"""
    
    SUPPORTED_FORMATS = ['.mp4', '.avi', '.mov', '.mkv', '.webm', '.flv', '.wmv', '.m4v']
    
    def __init__(self, max_workers: int = 4):
        self.max_workers = max_workers
        self.temp_dir = Path(tempfile.gettempdir()) / "deepfake_video_processing"
        self.temp_dir.mkdir(exist_ok=True, parents=True)
    
    @staticmethod
    def is_supported_format(file_path: str) -> bool:
        """Check if file format is supported"""
        return Path(file_path).suffix.lower() in VideoProcessor.SUPPORTED_FORMATS
    
    def extract_frames(
        self, 
        video_path: str, 
        sampling_rate: int = 1,
        max_frames: Optional[int] = None
    ) -> List[np.ndarray]:
        """
        Extract frames from video
        
        Args:
            video_path: Path to video file
            sampling_rate: Extract every nth frame
            max_frames: Maximum number of frames to extract
            
        Returns:
            List of frame arrays
        """
        frames = []
        frame_count = 0
        
        try:
            video = cv2.VideoCapture(video_path)
            
            if not video.isOpened():
                logger.error(f"Failed to open video: {video_path}")
                return frames
            
            total_frames = int(video.get(cv2.CAP_PROP_FRAME_COUNT))
            fps = video.get(cv2.CAP_PROP_FPS)
            
            logger.info(f"Video Info - Total frames: {total_frames}, FPS: {fps}")
            
            frame_idx = 0
            while True:
                ret, frame = video.read()
                
                if not ret:
                    break
                
                if frame_idx % sampling_rate == 0:
                    frames.append(frame)
                    frame_count += 1
                    
                    if max_frames and frame_count >= max_frames:
                        break
                
                frame_idx += 1
            
            video.release()
            logger.info(f"Extracted {len(frames)} frames from video")
            
        except Exception as e:
            logger.error(f"Error extracting frames: {str(e)}")
        
        return frames
    
    def get_video_info(self, video_path: str) -> Dict:
        """Get video metadata"""
        info = {
            'duration': 0,
            'fps': 0,
            'total_frames': 0,
            'width': 0,
            'height': 0,
            'codec': 'Unknown',
            'file_size': 0
        }
        
        try:
            video = cv2.VideoCapture(video_path)
            
            if video.isOpened():
                info['fps'] = video.get(cv2.CAP_PROP_FPS)
                info['total_frames'] = int(video.get(cv2.CAP_PROP_FRAME_COUNT))
                info['width'] = int(video.get(cv2.CAP_PROP_FRAME_WIDTH))
                info['height'] = int(video.get(cv2.CAP_PROP_FRAME_HEIGHT))
                info['duration'] = info['total_frames'] / max(info['fps'], 1)
                
                video.release()
            
            info['file_size'] = Path(video_path).stat().st_size / (1024 * 1024)  # MB
            
        except Exception as e:
            logger.error(f"Error getting video info: {str(e)}")
        
        return info
    
    def save_frames(self, frames: List[np.ndarray], output_dir: str) -> List[str]:
        """Save extracted frames to disk"""
        output_paths = []
        output_path = Path(output_dir)
        output_path.mkdir(exist_ok=True, parents=True)
        
        for idx, frame in enumerate(frames):
            frame_path = output_path / f"frame_{idx:06d}.png"
            try:
                cv2.imwrite(str(frame_path), frame)
                output_paths.append(str(frame_path))
            except Exception as e:
                logger.error(f"Error saving frame {idx}: {str(e)}")
        
        return output_paths


class FaceDetectionModule:
    """Detect and extract faces from video frames"""
    
    def __init__(self):
        # Load cascade classifier for face detection
        cascade_path = cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
        self.face_cascade = cv2.CascadeClassifier(cascade_path)
    
    def detect_faces(self, frame: np.ndarray) -> List[Tuple[int, int, int, int]]:
        """
        Detect faces in frame
        
        Returns:
            List of (x, y, w, h) tuples
        """
        try:
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            faces = self.face_cascade.detectMultiScale(
                gray, 
                scaleFactor=1.1, 
                minNeighbors=5, 
                minSize=(30, 30)
            )
            return list(faces)
        except Exception as e:
            logger.error(f"Error detecting faces: {str(e)}")
            return []
    
    def extract_faces(self, frame: np.ndarray) -> List[np.ndarray]:
        """Extract face ROIs from frame"""
        faces = self.detect_faces(frame)
        face_images = []
        
        for (x, y, w, h) in faces:
            face_roi = frame[y:y+h, x:x+w]
            face_images.append(face_roi)
        
        return face_images


class VideoAnalysisEngine:
    """Main video analysis pipeline"""
    
    def __init__(self):
        self.video_processor = VideoProcessor()
        self.face_detector = FaceDetectionModule()

    def _score_frame(self, frame: np.ndarray, faces: List[Tuple[int, int, int, int]]) -> float:
        """Estimate frame-level deepfake confidence based on face detail and visual artifacts"""
        if not faces:
            return 0.05

        frame_scores = []
        for (x, y, w, h) in faces:
            face_roi = frame[y:y+h, x:x+w]
            if face_roi.size == 0:
                continue

            face_gray = cv2.cvtColor(face_roi, cv2.COLOR_BGR2GRAY)
            laplacian_var = float(cv2.Laplacian(face_gray, cv2.CV_64F).var())
            brightness = float(np.mean(face_gray)) / 255.0

            detail_score = min(1.0, max(0.0, laplacian_var / 300.0))
            artifact_score = 1.0 - detail_score
            brightness_penalty = 0.1 if brightness < 0.15 or brightness > 0.85 else 0.0

            score = 0.35 + artifact_score * 0.4 + brightness_penalty
            frame_scores.append(min(0.98, max(0.02, score)))

        return float(np.mean(frame_scores)) if frame_scores else 0.05

    def analyze_video(
        self, 
        video_path: str,
        sensitivity: float = 0.8,
        sampling_rate: int = 1,
        progress_callback: Optional[callable] = None
    ) -> Dict:
        """
        Comprehensive video analysis
        
        Args:
            video_path: Path to video file
            sensitivity: Detection sensitivity (0.0-1.0)
            sampling_rate: Frame sampling rate
            progress_callback: Callback function for progress updates
            
        Returns:
            Analysis results dictionary
        """
        results = {
            'video_file': video_path,
            'status': 'processing',
            'video_info': {},
            'total_frames_analyzed': 0,
            'face_frames': 0,
            'deepfake_confidence': [],
            'frame_results': [],
            'overall_confidence': 0.0,
            'classification': 'Unknown',
            'warnings': [],
            'processing_time': 0
        }
        
        try:
            # Get video info
            results['video_info'] = self.video_processor.get_video_info(video_path)
            
            # Extract frames
            if progress_callback:
                progress_callback(0.1, "Extracting frames...")
            
            frames = self.video_processor.extract_frames(
                video_path, 
                sampling_rate=sampling_rate,
                max_frames=500  # Max 500 frames for analysis
            )
            
            results['total_frames_analyzed'] = len(frames)
            
            # Analyze frames
            deepfake_scores = []
            
            for idx, frame in enumerate(frames):
                # Detect faces
                faces = self.face_detector.detect_faces(frame)
                
                if len(faces) > 0:
                    results['face_frames'] += 1
                    
                    frame_confidence = self._score_frame(frame, faces)
                    deepfake_scores.append(frame_confidence)
                    
                    results['frame_results'].append({
                        'frame_idx': idx,
                        'faces_detected': len(faces),
                        'confidence': frame_confidence,
                        'is_deepfake': frame_confidence > sensitivity
                    })
                
                if progress_callback and idx % 10 == 0:
                    progress = 0.1 + (0.8 * (idx / len(frames)))
                    progress_callback(progress, f"Analyzing frame {idx}/{len(frames)}")
            
            # Calculate overall statistics
            if deepfake_scores:
                results['deepfake_confidence'] = deepfake_scores
                results['overall_confidence'] = np.mean(deepfake_scores)
                
                deepfake_count = sum(1 for s in deepfake_scores if s > sensitivity)
                deepfake_percentage = (deepfake_count / len(deepfake_scores)) * 100
                
                if deepfake_percentage > 30:
                    results['classification'] = 'DEEPFAKE'
                    results['warnings'].append(f"High deepfake score detected in {deepfake_percentage:.1f}% of frames")
                else:
                    results['classification'] = 'REAL'
            
            results['status'] = 'completed'
            
            if progress_callback:
                progress_callback(1.0, "Analysis complete")
            
        except Exception as e:
            logger.error(f"Error analyzing video: {str(e)}")
            results['status'] = 'error'
            results['warnings'].append(f"Analysis error: {str(e)}")
        
        return results
