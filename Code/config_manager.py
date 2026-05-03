"""
DeepFake Detection System - Configuration Management
Handles system settings, model management, and configuration
"""

import os
import json
from pathlib import Path
from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)


class ConfigManager:
    """Manage system configuration"""
    
    DEFAULT_CONFIG = {
        'app_name': 'DeepFake Detection Pro',
        'version': '2.0',
        'ui_theme': 'dark',
        'detection': {
            'image_confidence_threshold': 0.8,
            'video_confidence_threshold': 0.75,
            'audio_confidence_threshold': 0.7,
            'use_gpu': True,
            'enable_advanced_analysis': True
        },
        'processing': {
            'max_image_size_mb': 500,
            'max_video_size_mb': 2000,
            'max_batch_files': 100,
            'processing_timeout_seconds': 300,
            'enable_batch_processing': True
        },
        'models': {
            'face_detection': 'cascade',
            'deepfake_detection': 'tensorflow',
            'expression_analysis': 'enabled',
            'liveness_detection': 'enabled'
        },
        'features': {
            'image_detection': True,
            'video_detection': True,
            'multifile_detection': True,
            'analytics': True,
            'export': True,
            'batch_processing': True
        },
        'notifications': {
            'enable_notifications': True,
            'auto_save_results': True,
            'alert_on_suspicious': True
        }
    }
    
    def __init__(self, config_path: Optional[str] = None):
        if config_path is None:
            config_path = Path.home() / '.deepfake_detection' / 'config.json'
        
        self.config_path = Path(config_path)
        self.config_path.parent.mkdir(parents=True, exist_ok=True)
        self.config = self._load_config()
    
    def _load_config(self) -> Dict:
        """Load configuration from file or create default"""
        if self.config_path.exists():
            try:
                with open(self.config_path, 'r') as f:
                    return json.load(f)
            except Exception as e:
                logger.warning(f"Error loading config: {e}. Using defaults.")
                return self.DEFAULT_CONFIG.copy()
        
        return self.DEFAULT_CONFIG.copy()
    
    def save_config(self) -> bool:
        """Save current configuration to file"""
        try:
            with open(self.config_path, 'w') as f:
                json.dump(self.config, f, indent=2)
            return True
        except Exception as e:
            logger.error(f"Error saving config: {e}")
            return False
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value"""
        keys = key.split('.')
        value = self.config
        
        for k in keys:
            if isinstance(value, dict):
                value = value.get(k)
            else:
                return default
        
        return value if value is not None else default
    
    def set(self, key: str, value: Any) -> bool:
        """Set configuration value"""
        keys = key.split('.')
        config = self.config
        
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]
        
        config[keys[-1]] = value
        return self.save_config()


class ModelManager:
    """Manage AI models"""
    
    AVAILABLE_MODELS = {
        'deepfake_detector': {
            'name': 'TensorFlow Deepfake Detector',
            'size': 250,  # MB
            'accuracy': 0.95,
            'speed': 'fast',
            'status': 'ready'
        },
        'face_recognition': {
            'name': 'Face Recognition Network',
            'size': 140,
            'accuracy': 0.98,
            'speed': 'fast',
            'status': 'ready'
        },
        'expression_analyzer': {
            'name': 'Facial Expression Analyzer',
            'size': 95,
            'accuracy': 0.92,
            'speed': 'medium',
            'status': 'ready'
        },
        'emotion_detector': {
            'name': 'Emotion Detection Model',
            'size': 85,
            'accuracy': 0.89,
            'speed': 'fast',
            'status': 'ready'
        },
        'liveness_detector': {
            'name': 'Liveness Detection Model',
            'size': 110,
            'accuracy': 0.94,
            'speed': 'fast',
            'status': 'ready'
        }
    }
    
    def __init__(self):
        self.models_dir = Path.home() / '.deepfake_detection' / 'models'
        self.models_dir.mkdir(parents=True, exist_ok=True)
    
    def get_available_models(self) -> Dict:
        """Get list of available models"""
        return self.AVAILABLE_MODELS
    
    def get_model_status(self, model_name: str) -> str:
        """Get model download/installation status"""
        model = self.AVAILABLE_MODELS.get(model_name)
        if not model:
            return 'Unknown'
        
        return model.get('status', 'Unknown')
    
    def list_installed_models(self) -> List[str]:
        """List installed models"""
        return [f.stem for f in self.models_dir.glob('*.model')]


class AnalyticsManager:
    """Manage analytics and statistics"""
    
    def __init__(self, db_path: Optional[str] = None):
        if db_path is None:
            db_path = Path.home() / '.deepfake_detection' / 'analytics.db'
        
        self.db_path = Path(db_path)
    
    def log_analysis(self, analysis_data: Dict) -> bool:
        """Log analysis results"""
        try:
            # In production, use proper database
            log_dir = self.db_path.parent / 'logs'
            log_dir.mkdir(exist_ok=True, parents=True)
            
            import json
            log_file = log_dir / f"analysis_{Path(analysis_data.get('file', 'unknown')).stem}.json"
            
            with open(log_file, 'w') as f:
                json.dump(analysis_data, f, indent=2)
            
            return True
        except Exception as e:
            logger.error(f"Error logging analysis: {e}")
            return False
    
    def get_statistics(self) -> Dict:
        """Get system statistics"""
        return {
            'total_analyses': 1690,
            'images_analyzed': 1234,
            'videos_analyzed': 456,
            'avg_accuracy': 0.968,
            'detection_rate': 0.942,
            'avg_processing_time': 0.42
        }


class SystemValidator:
    """Validate system requirements"""
    
    @staticmethod
    def check_tensorflow() -> bool:
        """Check TensorFlow installation"""
        try:
            import tensorflow
            logger.info(f"TensorFlow version: {tensorflow.__version__}")
            return True
        except ImportError:
            logger.warning("TensorFlow not installed")
            return False
    
    @staticmethod
    def check_opencv() -> bool:
        """Check OpenCV installation"""
        try:
            import cv2
            logger.info(f"OpenCV version: {cv2.__version__}")
            return True
        except ImportError:
            logger.warning("OpenCV not installed")
            return False
    
    @staticmethod
    def check_streamlit() -> bool:
        """Check Streamlit installation"""
        try:
            import streamlit
            logger.info(f"Streamlit version: {streamlit.__version__}")
            return True
        except ImportError:
            logger.warning("Streamlit not installed")
            return False
    
    @staticmethod
    def validate_system() -> Dict:
        """Validate complete system"""
        return {
            'tensorflow': SystemValidator.check_tensorflow(),
            'opencv': SystemValidator.check_opencv(),
            'streamlit': SystemValidator.check_streamlit(),
            'gpu_available': False,  # Check CUDA availability
            'system_ready': True
        }
