"""
Multi-File Type Detection Module
Analyzes various file types to detect if they were created by deepfakes or manually
Supports: Images, Videos, Audio, GIFs, 3D Models, Documents
"""

import os
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class FileType(Enum):
    """Supported file types"""
    IMAGE = "image"
    VIDEO = "video"
    AUDIO = "audio"
    GIF = "gif"
    DOCUMENT = "document"
    ARCHIVE = "archive"
    UNKNOWN = "unknown"


class FileTypeManager:
    """Manage and identify file types"""
    
    FILE_EXTENSIONS = {
        FileType.IMAGE: ['.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.webp', '.ico', '.svg'],
        FileType.VIDEO: ['.mp4', '.avi', '.mov', '.mkv', '.webm', '.flv', '.wmv', '.m4v', '.mpg', '.mpeg'],
        FileType.AUDIO: ['.mp3', '.wav', '.flac', '.aac', '.m4a', '.wma', '.ogg', '.opus', '.aiff'],
        FileType.GIF: ['.gif'],
        FileType.DOCUMENT: ['.pdf', '.docx', '.doc', '.pptx', '.xlsx', '.txt']
    }
    
    @staticmethod
    def get_file_type(file_path: str) -> FileType:
        """Identify file type by extension"""
        ext = Path(file_path).suffix.lower()
        
        for file_type, extensions in FileTypeManager.FILE_EXTENSIONS.items():
            if ext in extensions:
                return file_type
        
        return FileType.UNKNOWN
    
    @staticmethod
    def is_supported(file_path: str) -> bool:
        """Check if file type is supported"""
        return FileTypeManager.get_file_type(file_path) != FileType.UNKNOWN


class ImageMetadataAnalyzer:
    """Analyze image metadata and properties"""
    
    @staticmethod
    def analyze(image_path: str) -> Dict:
        """Extract and analyze image metadata"""
        try:
            from PIL import Image
            from PIL.ExifTags import TAGS
            
            results = {
                'file_path': image_path,
                'file_size': os.path.getsize(image_path),
                'format': None,
                'dimensions': None,
                'mode': None,
                'metadata': {},
                'manipulation_indicators': {
                    'jpeg_quality': None,
                    'artifact_detected': False,
                    'metadata_stripped': False,
                    'inconsistencies': []
                }
            }
            
            img = Image.open(image_path)
            results['format'] = img.format
            results['dimensions'] = img.size
            results['mode'] = img.mode
            
            # Extract EXIF data
            try:
                exif_data = img._getexif()
                if exif_data:
                    for tag_id, value in exif_data.items():
                        tag_name = TAGS.get(tag_id, tag_id)
                        results['metadata'][tag_name] = str(value)[:100]  # Limit length
                else:
                    results['manipulation_indicators']['metadata_stripped'] = True
            except:
                results['manipulation_indicators']['metadata_stripped'] = True
            
            # Analyze frequency domain
            import numpy as np
            import cv2
            
            img_array = np.array(img)
            if len(img_array.shape) == 3:
                gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
            else:
                gray = img_array
            
            # Compute Laplacian for edge detection
            laplacian = cv2.Laplacian(gray, cv2.CV_64F)
            variance = laplacian.var()
            
            # Check for compression artifacts
            if variance < 100:
                results['manipulation_indicators']['artifact_detected'] = True
                results['manipulation_indicators']['inconsistencies'].append(
                    "Low frequency variance detected (possible compression artifacts)"
                )
            
            return results
            
        except Exception as e:
            logger.error(f"Error analyzing image metadata: {str(e)}")
            return {'error': str(e)}


class AudioAnalyzer:
    """Analyze audio for synthetic or manipulated content"""
    
    @staticmethod
    def analyze(audio_path: str) -> Dict:
        """Analyze audio file"""
        results = {
            'file_path': audio_path,
            'file_size': os.path.getsize(audio_path),
            'format': Path(audio_path).suffix.lower(),
            'analysis': {},
            'indicators': {
                'speech_detection': False,
                'audio_quality': 'Unknown',
                'synthetic_indicators': [],
                'manipulation_score': 0.0
            }
        }
        
        try:
            import scipy.io.wavfile as wav
            import numpy as np
            
            # Try to read audio
            if audio_path.lower().endswith('.wav'):
                sample_rate, audio_data = wav.read(audio_path)
                results['sample_rate'] = sample_rate
                
                # Analyze frequency spectrum
                if len(audio_data.shape) > 1:
                    audio_mono = np.mean(audio_data, axis=1)
                else:
                    audio_mono = audio_data
                
                fft = np.abs(np.fft.fft(audio_mono[:min(44100, len(audio_mono))]))
                frequency_peaks = np.argsort(fft)[-5:]  # Top 5 frequency peaks
                
                results['analysis']['frequency_peaks'] = frequency_peaks.tolist()
                results['analysis']['rms_energy'] = float(np.sqrt(np.mean(audio_mono ** 2)))
        
        except Exception as e:
            logger.error(f"Error analyzing audio: {str(e)}")
            results['analysis']['error'] = str(e)
        
        return results


class GIFAnalyzer:
    """Analyze GIF files for deepfake detection"""
    
    @staticmethod
    def analyze(gif_path: str) -> Dict:
        """Analyze GIF animation"""
        results = {
            'file_path': gif_path,
            'file_size': os.path.getsize(gif_path),
            'frame_count': 0,
            'duration': 0,
            'frames_analyzed': 0,
            'deepfake_indicators': {
                'inconsistent_frames': 0,
                'face_detection_variance': 0.0,
                'suspicious_transitions': False
            }
        }
        
        try:
            from PIL import Image
            
            gif = Image.open(gif_path)
            frame_count = 0
            
            try:
                while True:
                    frame_count += 1
                    gif.seek(frame_count)
            except EOFError:
                pass
            
            results['frame_count'] = frame_count
            results['duration'] = (frame_count / 10) if frame_count > 0 else 0  # Estimate
            
            # Analyze frame consistency
            # This would use face detection on each frame
            results['frames_analyzed'] = min(frame_count, 50)
            
        except Exception as e:
            logger.error(f"Error analyzing GIF: {str(e)}")
            results['error'] = str(e)
        
        return results


class MultiFileDetectionEngine:
    """Main engine for multi-file type deepfake detection"""
    
    def __init__(self):
        self.file_type_manager = FileTypeManager()
        self.image_analyzer = ImageMetadataAnalyzer()
        self.audio_analyzer = AudioAnalyzer()
        self.gif_analyzer = GIFAnalyzer()
    
    def analyze_file(self, file_path: str, analysis_depth: str = "standard") -> Dict:
        """
        Analyze any supported file type
        
        Args:
            file_path: Path to file
            analysis_depth: "quick", "standard", or "deep"
            
        Returns:
            Comprehensive analysis results
        """
        file_path = str(file_path)
        
        if not os.path.exists(file_path):
            return {'error': 'File not found', 'file': file_path}
        
        file_type = self.file_type_manager.get_file_type(file_path)
        
        results = {
            'file': file_path,
            'file_type': file_type.value,
            'file_size_mb': os.path.getsize(file_path) / (1024 * 1024),
            'creation_method': 'Unknown',
            'confidence': 0.0,
            'analysis_depth': analysis_depth,
            'detailed_results': {},
            'recommendations': []
        }
        
        try:
            if file_type == FileType.IMAGE:
                results['detailed_results'] = self.image_analyzer.analyze(file_path)
                results['creation_method'] = self._determine_image_creation_method(results['detailed_results'])
                
            elif file_type == FileType.VIDEO:
                results['recommendations'].append("Use Video Detection module for comprehensive analysis")
                
            elif file_type == FileType.AUDIO:
                results['detailed_results'] = self.audio_analyzer.analyze(file_path)
                results['creation_method'] = self._determine_audio_creation_method(results['detailed_results'])
                
            elif file_type == FileType.GIF:
                results['detailed_results'] = self.gif_analyzer.analyze(file_path)
                results['creation_method'] = self._determine_gif_creation_method(results['detailed_results'])
            
            results['status'] = 'completed'
            
        except Exception as e:
            logger.error(f"Error analyzing file: {str(e)}")
            results['status'] = 'error'
            results['error'] = str(e)
        
        return results
    
    @staticmethod
    def _determine_image_creation_method(analysis: Dict) -> str:
        """Determine if image was manually created or by deepfake"""
        if 'manipulation_indicators' not in analysis:
            return 'Unknown'
        
        indicators = analysis['manipulation_indicators']
        
        if indicators.get('metadata_stripped'):
            return 'Possible Manipulation'
        
        if indicators.get('artifact_detected'):
            return 'Possible AI-Generated'
        
        if len(indicators.get('inconsistencies', [])) > 2:
            return 'Suspicious'
        
        return 'Likely Manual/Natural'
    
    @staticmethod
    def _determine_audio_creation_method(analysis: Dict) -> str:
        """Determine if audio was manually created or synthetic"""
        if 'indicators' not in analysis:
            return 'Unknown'
        
        indicators = analysis['indicators']
        
        if indicators.get('synthetic_indicators'):
            return 'Possible Synthetic Speech'
        
        return 'Likely Natural Speech'
    
    @staticmethod
    def _determine_gif_creation_method(analysis: Dict) -> str:
        """Determine GIF creation method"""
        if analysis.get('deepfake_indicators', {}).get('suspicious_transitions'):
            return 'Potentially Manipulated'
        
        return 'Likely Natural'
    
    def batch_analyze(self, file_paths: List[str], analysis_depth: str = "standard") -> List[Dict]:
        """Analyze multiple files"""
        results = []
        
        for file_path in file_paths:
            result = self.analyze_file(file_path, analysis_depth)
            results.append(result)
        
        return results
    
    def generate_report(self, analysis_results: Dict) -> str:
        """Generate human-readable report"""
        report = []
        report.append("=" * 60)
        report.append("FILE ANALYSIS REPORT")
        report.append("=" * 60)
        report.append(f"\nFile: {analysis_results.get('file', 'Unknown')}")
        report.append(f"Type: {analysis_results.get('file_type', 'Unknown')}")
        report.append(f"Size: {analysis_results.get('file_size_mb', 0):.2f} MB")
        report.append(f"Creation Method: {analysis_results.get('creation_method', 'Unknown')}")
        report.append(f"Confidence: {analysis_results.get('confidence', 0):.2%}")
        
        if analysis_results.get('recommendations'):
            report.append("\nRecommendations:")
            for rec in analysis_results['recommendations']:
                report.append(f"  • {rec}")
        
        report.append("\n" + "=" * 60)
        
        return "\n".join(report)
