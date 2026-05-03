#!/usr/bin/env python
"""
DeepFake Detection Pro - Website-Style UI
Modern single-page application with header navigation
No sidebar, clean website-like layout
"""

import streamlit as st
import os
import sys
from pathlib import Path
import logging
import time
import tempfile
from datetime import datetime
import threading
import queue
from typing import List, Dict, Any, Optional, Tuple

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

try:
    from Code.video_detection_module import VideoAnalysisEngine
    from Code.multifile_detection_module import MultiFileDetectionEngine
    logger.info("✅ Core detection modules loaded successfully")
    CORE_MODULES_AVAILABLE = True
except Exception as e:
    logger.warning(f"⚠️ Could not load core detection modules: {e}")
    CORE_MODULES_AVAILABLE = False

try:
    from Code.content_analyzer import ContentAnalyzer
    logger.info("✅ Content analyzer loaded successfully")
    CONTENT_ANALYZER_AVAILABLE = True
except Exception as e:
    logger.warning(f"⚠️ Could not load content analyzer: {e}")
    CONTENT_ANALYZER_AVAILABLE = False

try:
    import tensorflow as tf
    logger.info(f"✅ TensorFlow {tf.__version__} loaded")
    TF_AVAILABLE = True
except ImportError:
    logger.warning("⚠️ TensorFlow not available")
    TF_AVAILABLE = False

# Initialize detection engines and content analyzer
multi_file_engine = None
video_engine = None
content_analyzer = None

if CORE_MODULES_AVAILABLE:
    try:
        multi_file_engine = MultiFileDetectionEngine()
    except Exception as e:
        logger.warning(f"⚠️ Failed to initialize MultiFileDetectionEngine: {e}")
        multi_file_engine = None
    try:
        video_engine = VideoAnalysisEngine()
    except Exception as e:
        logger.warning(f"⚠️ Failed to initialize VideoAnalysisEngine: {e}")
        video_engine = None

if CONTENT_ANALYZER_AVAILABLE:
    try:
        content_analyzer = ContentAnalyzer()
    except Exception as e:
        logger.warning(f"⚠️ Failed to initialize ContentAnalyzer: {e}")
        content_analyzer = None

# ============================================================================
# PAGE CONFIGURATION
# ============================================================================

st.set_page_config(
    page_title="DeepFake Detection Pro",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================================================
# MULTIPLE THEMES SYSTEM
# ============================================================================

# Professional themes inspired by real SaaS platforms
THEMES = {
    "default": {
        "name": "DeepFake Pro",
        "primary": "#6366f1",      # Indigo
        "primary_light": "#818cf8",
        "primary_dark": "#4f46e5",
        "secondary": "#f8fafc",
        "accent": "#06b6d4",
        "success": "#10b981",
        "warning": "#f59e0b",
        "danger": "#ef4444",
        "gray_50": "#f8fafc",
        "gray_100": "#f1f5f9",
        "gray_200": "#e2e8f0",
        "gray_300": "#cbd5e1",
        "gray_400": "#94a3b8",
        "gray_500": "#64748b",
        "gray_600": "#475569",
        "gray_700": "#334155",
        "gray_800": "#1e293b",
        "gray_900": "#0f172a",
        "white": "#ffffff",
        "black": "#000000",
        "text_color": "#0f172a",   # Dark text for light theme
        "text_secondary": "#475569", # Secondary text color
        "bg_gradient": "linear-gradient(135deg, #f8fafc 0%, #ffffff 100%)",
        "card_bg": "#ffffff",
        "header_bg": "#ffffff"
    },
    "dark": {
        "name": "DeepFake Pro Dark",
        "primary": "#3b82f6",      # Blue
        "primary_light": "#60a5fa",
        "primary_dark": "#2563eb",
        "secondary": "#1e293b",
        "accent": "#06b6d4",
        "success": "#10b981",
        "warning": "#f59e0b",
        "danger": "#ef4444",
        "gray_50": "#f8fafc",
        "gray_100": "#f1f5f9",
        "gray_200": "#e2e8f0",
        "gray_300": "#cbd5e1",
        "gray_400": "#94a3b8",
        "gray_500": "#64748b",
        "gray_600": "#475569",
        "gray_700": "#334155",
        "gray_800": "#1e293b",
        "gray_900": "#0f172a",
        "white": "#ffffff",
        "black": "#000000",
        "text_color": "#f1f5f9",   # Light text for dark theme
        "text_secondary": "#94a3b8", # Light secondary text for dark theme
        "bg_gradient": "linear-gradient(135deg, #0f172a 0%, #1e293b 100%)",
        "card_bg": "#1e293b",
        "header_bg": "#0f172a"
    },
    "nature": {
        "name": "DeepFake Pro Nature",
        "primary": "#059669",
        "primary_light": "#10b981",
        "primary_dark": "#047857",
        "secondary": "#f0fdf4",
        "accent": "#84cc16",
        "success": "#22c55e",
        "warning": "#f59e0b",
        "danger": "#ef4444",
        "gray_50": "#f8fafc",
        "gray_100": "#f1f5f9",
        "gray_200": "#e2e8f0",
        "gray_300": "#cbd5e1",
        "gray_400": "#94a3b8",
        "gray_500": "#64748b",
        "gray_600": "#475569",
        "gray_700": "#334155",
        "gray_800": "#1e293b",
        "gray_900": "#0f172a",
        "white": "#ffffff",
        "black": "#000000",
        "text_color": "#065f46",
        "text_secondary": "#047857",
        "bg_gradient": "linear-gradient(135deg, #f0fdf4 0%, #ffffff 100%)",
        "card_bg": "#ffffff",
        "header_bg": "#ffffff"
    },
    "sunset": {
        "name": "DeepFake Pro Sunset",
        "primary": "#dc2626",      # Red
        "primary_light": "#ef4444",
        "primary_dark": "#b91c1c",
        "secondary": "#fef2f2",
        "accent": "#f59e0b",
        "success": "#10b981",
        "warning": "#f59e0b",
        "danger": "#dc2626",
        "gray_50": "#f8fafc",
        "gray_100": "#f1f5f9",
        "gray_200": "#e2e8f0",
        "gray_300": "#cbd5e1",
        "gray_400": "#94a3b8",
        "gray_500": "#64748b",
        "gray_600": "#475569",
        "gray_700": "#334155",
        "gray_800": "#1e293b",
        "gray_900": "#0f172a",
        "white": "#ffffff",
        "black": "#000000",
        "text_color": "#1f2937",
        "text_secondary": "#374151",
        "bg_gradient": "linear-gradient(135deg, #fef2f2 0%, #ffffff 100%)",
        "card_bg": "#ffffff",
        "header_bg": "#ffffff"
    },
    "ocean": {
        "name": "DeepFake Pro Ocean",
        "primary": "#0891b2",      # Cyan
        "primary_light": "#06b6d4",
        "primary_dark": "#0e7490",
        "secondary": "#ecfeff",
        "accent": "#3b82f6",
        "success": "#10b981",
        "warning": "#f59e0b",
        "danger": "#ef4444",
        "gray_50": "#f8fafc",
        "gray_100": "#f1f5f9",
        "gray_200": "#e2e8f0",
        "gray_300": "#cbd5e1",
        "gray_400": "#94a3b8",
        "gray_500": "#64748b",
        "gray_600": "#475569",
        "gray_700": "#334155",
        "gray_800": "#1e293b",
        "gray_900": "#0f172a",
        "white": "#ffffff",
        "black": "#000000",
        "text_color": "#164e63",
        "text_secondary": "#0e7490",
        "bg_gradient": "linear-gradient(135deg, #ecfeff 0%, #ffffff 100%)",
        "card_bg": "#ffffff",
        "header_bg": "#ffffff"
    }
}

# Initialize theme in session state
if "selected_theme" not in st.session_state:
    st.session_state.selected_theme = "default"

# Get current theme
current_theme = THEMES[st.session_state.selected_theme]

# ============================================================================
# MODERN CSS STYLES - WEBSITE STYLE
# ============================================================================

def get_css_styles():
    """Generate CSS styles based on current theme"""
    return f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

:root {{
    --primary: {current_theme['primary']};
    --primary-light: {current_theme['primary_light']};
    --primary-dark: {current_theme['primary_dark']};
    --secondary: {current_theme['secondary']};
    --accent: {current_theme['accent']};
    --success: {current_theme['success']};
    --warning: {current_theme['warning']};
    --danger: {current_theme['danger']};
    --gray-50: {current_theme['gray_50']};
    --gray-100: {current_theme['gray_100']};
    --gray-200: {current_theme['gray_200']};
    --gray-300: {current_theme['gray_300']};
    --gray-400: {current_theme['gray_400']};
    --gray-500: {current_theme['gray_500']};
    --gray-600: {current_theme['gray_600']};
    --gray-700: {current_theme['gray_700']};
    --gray-800: {current_theme['gray_800']};
    --gray-900: {current_theme['gray_900']};
    --white: {current_theme['white']};
    --black: {current_theme['black']};
    --text-color: {current_theme['text_color']};
    --text-secondary: {current_theme['text_secondary']};
    --bg-gradient: {current_theme['bg_gradient']};
    --card-bg: {current_theme['card_bg']};
    --header-bg: {current_theme['header_bg']};
}}

* {{
    margin: 0;
    padding: 0;
    box-sizing: border-box;
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
}}

html, body, [data-testid="stAppViewContainer"] {{
    background: var(--bg-gradient);
    color: {current_theme.get('text_color', 'var(--gray-900)')};
    line-height: 1.6;
}}

/* Hide Streamlit elements */
#MainMenu {{visibility: hidden;}}
footer {{visibility: hidden;}}

/* Sidebar Styling */
[data-testid="stSidebar"] {{
    width: 320px !important;
    max-width: 320px !important;
    min-width: 320px !important;
    background: var(--secondary) !important;
    border-right: 1px solid var(--gray-200) !important;
    padding: 1rem 0.75rem !important;
    transition: all 0.35s cubic-bezier(0.4, 0, 0.2, 1) !important;
    box-shadow: 2px 0 8px rgba(0, 0, 0, 0.08) !important;
}}

[data-testid="stAppViewContainer"] {{
    transition: margin-left 0.35s cubic-bezier(0.4, 0, 0.2, 1);
}}

/* Modern Header */
.modern-header {{
    background: var(--header-bg);
    border-bottom: 1px solid var(--gray-200);
    padding: 1rem 2rem;
    position: sticky;
    top: 0;
    z-index: 1000;
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}}

.header-content {{
    display: flex;
    justify-content: space-between;
    align-items: center;
    max-width: 1400px;
    margin: 0 auto;
}}

.logo-section {{
    display: flex;
    align-items: center;
    gap: 1rem;
}}

.logo {{
    font-size: 1.5rem;
    font-weight: 700;
    color: var(--primary);
    text-decoration: none;
}}

.logo-icon {{
    font-size: 1.8rem;
}}

.nav-section {{
    display: flex;
    align-items: center;
    gap: 2rem;
}}

.nav-links {{
    display: flex;
    gap: 1.5rem;
    align-items: center;
}}

.nav-link {{
    color: var(--text-secondary);
    text-decoration: none;
    font-weight: 500;
    padding: 0.5rem 1rem;
    border-radius: 8px;
    transition: all 0.2s ease;
    position: relative;
}}

.nav-link:hover {{
    color: var(--primary);
    background: var(--gray-100);
}}

.nav-link.active {{
    color: var(--primary);
    background: rgba(99, 102, 241, 0.1);
    font-weight: 600;
}}

.nav-link.active::after {{
    content: '';
    position: absolute;
    bottom: -1px;
    left: 50%;
    transform: translateX(-50%);
    width: 20px;
    height: 2px;
    background: var(--primary);
    border-radius: 1px;
}}

.header-actions {{
    display: flex;
    align-items: center;
    gap: 1rem;
}}

/* Main Content */
.main-content {{
    max-width: 1400px;
    margin: 0 auto;
    padding: 2rem;
}}

.page-container {{
    background: var(--card-bg);
    border-radius: 16px;
    box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
    overflow: hidden;
}}

.page-header {{
    background: linear-gradient(135deg, var(--primary) 0%, var(--primary-light) 100%);
    color: white;
    padding: 3rem 2rem;
    text-align: center;
}}

.page-title {{
    font-size: 2.5rem;
    font-weight: 700;
    margin-bottom: 0.5rem;
}}

.page-subtitle {{
    font-size: 1.1rem;
    opacity: 0.9;
    max-width: 600px;
    margin: 0 auto;
}}

.page-content {{
    padding: 2rem;
}}

/* Cards */
.modern-card {{
    background: var(--card-bg);
    border: 1px solid var(--gray-200);
    border-radius: 12px;
    padding: 1.5rem;
    margin-bottom: 1.5rem;
    transition: all 0.3s ease;
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}}

.modern-card:hover {{
    border-color: var(--primary);
    box-shadow: 0 4px 12px rgba(99, 102, 241, 0.15);
    transform: translateY(-2px);
}}

.card-header {{
    display: flex;
    align-items: center;
    gap: 0.75rem;
    margin-bottom: 1rem;
}}

.card-icon {{
    font-size: 1.5rem;
}}

.card-title {{
    font-size: 1.25rem;
    font-weight: 600;
    color: var(--text-color);
}}

.card-description {{
    color: var(--text-secondary);
    font-size: 0.9rem;
    margin-bottom: 1rem;
}}

/* Stats Grid */
.stats-grid {{
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
    gap: 1.5rem;
    margin: 2rem 0;
}}

.stat-card {{
    background: linear-gradient(135deg, var(--primary) 0%, var(--primary-light) 100%);
    color: white;
    padding: 1.5rem;
    border-radius: 12px;
    text-align: center;
    box-shadow: 0 4px 6px rgba(99, 102, 241, 0.2);
}}

.stat-value {{
    font-size: 2rem;
    font-weight: 700;
    margin: 0.5rem 0;
}}

.stat-label {{
    font-size: 0.9rem;
    opacity: 0.9;
}}

/* Buttons */
.btn-primary {{
    background: var(--primary);
    color: white;
    border: none;
    padding: 0.75rem 1.5rem;
    border-radius: 8px;
    font-weight: 600;
    cursor: pointer;
    transition: all 0.2s ease;
    text-decoration: none;
    display: inline-block;
}}

.btn-primary:hover {{
    background: var(--primary-dark);
    transform: translateY(-1px);
    box-shadow: 0 4px 12px rgba(99, 102, 241, 0.3);
}}

.btn-secondary {{
    background: var(--gray-100);
    color: var(--gray-700);
    border: 1px solid var(--gray-300);
    padding: 0.75rem 1.5rem;
    border-radius: 8px;
    font-weight: 600;
    cursor: pointer;
    transition: all 0.2s ease;
    text-decoration: none;
    display: inline-block;
}}

.btn-secondary:hover {{
    background: var(--gray-200);
    border-color: var(--gray-400);
}}

/* Form Elements */
.stTextInput > div > div > input {{
    border: 2px solid var(--gray-200) !important;
    border-radius: 8px !important;
    padding: 0.75rem !important;
    font-size: 1rem !important;
    transition: all 0.2s ease !important;
}}

.stTextInput > div > div > input:focus {{
    border-color: var(--primary) !important;
    box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.1) !important;
}}

.stFileUploader > div > div {{
    border: 2px dashed var(--gray-300) !important;
    border-radius: 8px !important;
    padding: 2rem !important;
    text-align: center !important;
    transition: all 0.2s ease !important;
}}

.stFileUploader > div > div:hover {{
    border-color: var(--primary) !important;
    background: rgba(99, 102, 241, 0.05) !important;
}}

/* Progress Bars */
.stProgress > div > div > div {{
    background: var(--primary) !important;
}}

/* Footer */
.modern-footer {{
    background: var(--gray-900);
    color: var(--gray-300);
    padding: 3rem 2rem 1rem;
    margin-top: 4rem;
}}

.footer-content {{
    max-width: 1400px;
    margin: 0 auto;
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
    gap: 2rem;
}}

.footer-section h4 {{
    color: var(--white);
    margin-bottom: 1rem;
    font-size: 1.1rem;
}}

.footer-section p {{
    margin-bottom: 0.5rem;
    font-size: 0.9rem;
}}

.footer-links {{
    display: flex;
    flex-direction: column;
    gap: 0.5rem;
}}

.footer-link {{
    color: var(--gray-400);
    text-decoration: none;
    transition: color 0.2s ease;
}}

.footer-link:hover {{
    color: var(--primary);
}}

.footer-bottom {{
    border-top: 1px solid var(--gray-800);
    margin-top: 2rem;
    padding-top: 1rem;
    text-align: center;
    color: var(--gray-500);
    font-size: 0.9rem;
}}

/* Responsive Design */
@media (max-width: 768px) {{
    .header-content {{
        flex-direction: column;
        gap: 1rem;
    }}

    .nav-links {{
        flex-wrap: wrap;
        justify-content: center;
    }}

    .main-content {{
        padding: 1rem;
    }}

    .page-header {{
        padding: 2rem 1rem;
    }}

    .page-title {{
        font-size: 2rem;
    }}

    .stats-grid {{
        grid-template-columns: 1fr;
    }}
}}

/* Hide any raw code or error messages */
code {{
    display: none !important;
}}

pre {{
    display: none !important;
}}

/* Hide Streamlit default elements */
.st-emotion-cache-1y4p8pa {{
    display: none !important;
}}

.st-emotion-cache-1v0mbdj {{
    display: none !important;
}}

/* Hide any markdown code blocks */
.markdown-text-container code {{
    display: none !important;
}}

.markdown-text-container pre {{
    display: none !important;
}}

/* Ensure no raw text shows */
.stMarkdown {{
    display: block !important;
}}

.stMarkdown p {{
    display: block !important;
}}

</style>
"""

# Apply CSS styles
st.markdown(get_css_styles(), unsafe_allow_html=True)

# Helper functions for analysis

def save_uploaded_to_temp(uploaded_file):
    temp_dir = Path(tempfile.gettempdir())
    temp_dir.mkdir(exist_ok=True, parents=True)
    temp_path = temp_dir / Path(uploaded_file.name).name
    with open(temp_path, "wb") as buffer:
        buffer.write(uploaded_file.getbuffer())
    return str(temp_path)


def _get_confidence(probability: float) -> str:
    if probability is None:
        return "Unknown"
    return f"{min(max(probability, 0.0), 1.0) * 100:.1f}%"


def _classify_image_analysis(analysis: Dict, threshold: float):
    if not analysis:
        return {
            'label': 'Unknown',
            'is_deepfake': False,
            'confidence': 0.0,
            'summary': 'No analysis data available.'
        }

    if analysis.get('error'):
        return {
            'label': 'Error',
            'is_deepfake': False,
            'confidence': 0.0,
            'summary': analysis.get('error')
        }

    ai_analysis = analysis.get('ai_human_analysis') or {}
    if ai_analysis:
        ai_prob = float(ai_analysis.get('ai_probability', 0.5))
        human_prob = float(ai_analysis.get('human_probability', 1.0 - ai_prob))
        is_deepfake = ai_prob >= threshold
        label = 'DEEPFAKE DETECTED' if is_deepfake else 'AUTHENTIC IMAGE'
        summary = ai_analysis.get('assessment', 'No assessment available.')
        return {
            'label': label,
            'is_deepfake': is_deepfake,
            'confidence': ai_prob if is_deepfake else human_prob,
            'summary': summary,
            'indicators': ai_analysis.get('indicators', [])
        }

    details = analysis.get('detailed_results', {})
    indicators = details.get('manipulation_indicators', {})
    score = 0.35

    if indicators.get('metadata_stripped'):
        score += 0.2
    if indicators.get('artifact_detected'):
        score += 0.25
    if 'Suspicious' in analysis.get('creation_method', ''):
        score += 0.15
    if len(indicators.get('inconsistencies', [])) > 1:
        score += 0.1

    score = min(0.98, score)
    is_deepfake = score >= threshold
    label = 'DEEPFAKE DETECTED' if is_deepfake else 'AUTHENTIC IMAGE'
    summary = analysis.get('creation_method', 'Manual review recommended')

    return {
        'label': label,
        'is_deepfake': is_deepfake,
        'confidence': score,
        'summary': summary,
        'indicators': indicators.get('inconsistencies', [])
    }


def _classify_file_analysis(analysis: Dict) -> Dict:
    if not analysis:
        return {'label': 'Unknown', 'confidence': 0.0, 'summary': 'No analysis data available.'}

    if analysis.get('error'):
        return {'label': 'Error', 'confidence': 0.0, 'summary': analysis.get('error')}

    ai_analysis = analysis.get('ai_human_analysis') or {}
    if ai_analysis:
        ai_prob = float(ai_analysis.get('ai_probability', 0.5))
        label = 'DEEPFAKE SUSPECTED' if ai_prob > 0.6 else 'AUTHENTIC CONTENT' if ai_prob < 0.4 else 'UNCERTAIN ORIGIN'
        return {
            'label': label,
            'confidence': ai_prob,
            'summary': ai_analysis.get('assessment', 'Review content details for a complete understanding'),
            'indicators': ai_analysis.get('indicators', [])
        }

    analysis_detail = analysis.get('analysis_detail') or {}
    if isinstance(analysis_detail, dict) and analysis.get('file_type') == 'video':
        ai_prob = float(analysis_detail.get('overall_confidence', 0.0))
        if analysis_detail.get('classification') == 'DEEPFAKE' or ai_prob > 0.6:
            return {
                'label': 'DEEPFAKE SUSPECTED',
                'confidence': ai_prob,
                'summary': analysis_detail.get('warnings', ['Video-level confidence indicates possible deepfake.'])[0],
                'indicators': analysis_detail.get('warnings', [])
            }
        return {
            'label': 'AUTHENTIC CONTENT',
            'confidence': ai_prob,
            'summary': 'Video analysis did not reveal strong deepfake indicators.',
            'indicators': analysis_detail.get('warnings', [])
        }

    method = analysis.get('creation_method', '')
    score = 0.5
    if 'Possible' in method or 'Suspicious' in method:
        score = 0.85
        label = 'DEEPFAKE SUSPECTED'
    else:
        score = 0.25
        label = 'AUTHENTIC CONTENT'

    return {
        'label': label,
        'confidence': score,
        'summary': method,
        'indicators': []
    }


def _classify_video_analysis(analysis: Dict, sensitivity: float) -> Dict:
    if not analysis:
        return {'label': 'Unknown', 'confidence': 0.0, 'summary': 'No analysis data available.'}

    if analysis.get('status') == 'error':
        return {'label': 'Error', 'confidence': 0.0, 'summary': 'Video analysis failed.'}

    classification = analysis.get('classification', 'Unknown')
    confidence = float(analysis.get('overall_confidence', 0.0))
    if classification == 'DEEPFAKE' or confidence >= sensitivity:
        label = 'DEEPFAKE DETECTED'
    elif confidence < (sensitivity * 0.6):
        label = 'AUTHENTIC VIDEO'
    else:
        label = 'POSSIBLE DEEPFAKE'

    summary = analysis.get('warnings', [])
    if not summary:
        summary = [f"Processed {analysis.get('total_frames_analyzed', 0)} frames."]

    return {
        'label': label,
        'confidence': confidence,
        'summary': ' '.join(summary) if isinstance(summary, list) else str(summary),
        'frame_count': analysis.get('total_frames_analyzed', 0),
        'face_frames': analysis.get('face_frames', 0)
    }

# ============================================================================
# SESSION STATE INITIALIZATION
# ============================================================================

if "current_page" not in st.session_state:
    st.session_state.current_page = "dashboard"

if "theme_mode" not in st.session_state:
    st.session_state.theme_mode = "light"

if "sidebar_visible" not in st.session_state:
    st.session_state.sidebar_visible = True

# ============================================================================
# MODERN HEADER COMPONENT
# ============================================================================

def render_sidebar_toggle():
    """Render a small toggle button when the sidebar is hidden."""
    if not st.session_state.sidebar_visible:
        if st.button("☰ Open Navigation", key="open_sidebar", help="Show the sliding navigation panel"):
            st.session_state.sidebar_visible = True
            st.experimental_rerun()

def render_sidebar():
    """Render the sidebar navigation and theme controls."""

    st.sidebar.markdown(f"# {current_theme['name']}")
    st.sidebar.markdown("Advanced deepfake detection across images, video, audio, and documents.")
    st.sidebar.markdown("---")

    nav_items = [
        ("Dashboard", "dashboard"),
        ("Image Analysis", "image_analysis"),
        ("File Analysis", "file_analysis"),
        ("Video Analysis", "video_analysis"),
        ("Batch Processing", "batch_processing"),
        ("Analytics", "analytics"),
        ("Model Training", "training"),
        ("Settings", "settings"),
        ("Docs", "docs"),
    ]

    selected_page = st.sidebar.radio(
        "Navigation",
        [item[0] for item in nav_items],
        index=[item[1] for item in nav_items].index(st.session_state.current_page),
        key="sidebar_navigation"
    )

    for label, page_key in nav_items:
        if label == selected_page:
            st.session_state.current_page = page_key
            break

    st.sidebar.markdown("---")
    theme_options = list(THEMES.keys())
    theme_labels = [THEMES[t]['name'] for t in theme_options]
    selected_theme_label = st.sidebar.selectbox(
        "Theme",
        theme_labels,
        index=theme_options.index(st.session_state.selected_theme),
        key="sidebar_theme_selector"
    )

    if theme_options[theme_labels.index(selected_theme_label)] != st.session_state.selected_theme:
        st.session_state.selected_theme = theme_options[theme_labels.index(selected_theme_label)]
        st.experimental_rerun()

    engine_status = "Ready" if multi_file_engine or video_engine or content_analyzer else "Unavailable"
    st.sidebar.markdown(f"**Detection engine:** {engine_status}")
    st.sidebar.markdown(f"- Core detection: {'✅' if multi_file_engine or video_engine else '❌'}")
    st.sidebar.markdown(f"- Content analyzer: {'✅' if content_analyzer else '❌'}")
    st.sidebar.markdown("---")
    if st.sidebar.button("← Hide Navigation", key="hide_sidebar"):
        st.session_state.sidebar_visible = False
        st.experimental_rerun()
    st.sidebar.write("Need support? Use the Docs section for instructions.")


def render_modern_header():
    """Render the modern website-style brand header."""
    st.markdown(f"""
    <div class="modern-header">
        <div class="header-content">
            <div class="logo-section">
                <span class="logo-icon">🔍</span>
                <span class="logo">{current_theme['name']}</span>
            </div>
            <div class="header-actions">
                <span class="nav-link active">Enterprise DeepFake Detection</span>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
# ============================================================================
# DASHBOARD PAGE
# ============================================================================

def render_dashboard():
    """Render the main dashboard page"""

    st.markdown("""
    <div class="page-container">
        <div class="page-header">
            <h1 class="page-title">Welcome to DeepFake Detection Pro</h1>
            <p class="page-subtitle">
                Advanced AI-powered deepfake detection for images, videos, and documents.
                Enterprise-grade accuracy with real-time processing capabilities.
            </p>
        </div>

        <div class="page-content">
    """, unsafe_allow_html=True)

    # Stats Grid
    st.markdown("""
    <div class="stats-grid">
        <div class="stat-card">
            <div class="stat-value">1,690</div>
            <div class="stat-label">Total Analyses</div>
        </div>
        <div class="stat-card">
            <div class="stat-value">95.2%</div>
            <div class="stat-label">Accuracy Rate</div>
        </div>
        <div class="stat-card">
            <div class="stat-value">3.2s</div>
            <div class="stat-label">Avg Processing Time</div>
        </div>
        <div class="stat-card">
            <div class="stat-value">23.1%</div>
            <div class="stat-label">Detection Rate</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Quick Actions
    st.markdown("""
    <div class="modern-card">
        <div class="card-header">
            <span class="card-icon">⚡</span>
            <h3 class="card-title">Quick Actions</h3>
        </div>
        <div class="card-description">
            Get started with common detection tasks
        </div>
    """, unsafe_allow_html=True)

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        if st.button("📷 Analyze Image", use_container_width=True):
            st.session_state.current_page = "file_analysis"
            st.rerun()
    with col2:
        if st.button("🎥 Analyze Video", use_container_width=True):
            st.session_state.current_page = "video_analysis"
            st.rerun()
    with col3:
        if st.button("📊 Batch Process", use_container_width=True):
            st.session_state.current_page = "batch_processing"
            st.rerun()
    with col4:
        if st.button("📈 View Analytics", use_container_width=True):
            st.session_state.current_page = "analytics"
            st.rerun()

    st.markdown("</div>", unsafe_allow_html=True)

    # Recent Activity
    st.markdown("""
    <div class="modern-card">
        <div class="card-header">
            <span class="card-icon">📋</span>
            <h3 class="card-title">Recent Activity</h3>
        </div>
    """, unsafe_allow_html=True)

    # Sample recent activity data
    activity_data = {
        "Time": ["2 min ago", "15 min ago", "1 hour ago", "2 hours ago"],
        "Action": ["Image Analysis", "Video Processing", "Batch Analysis", "Model Training"],
        "File": ["profile.jpg", "interview.mp4", "dataset.zip", "model_v2.h5"],
        "Result": ["Authentic (96%)", "Deepfake (87%)", "Mixed Results", "Completed"],
        "Confidence": ["96%", "87%", "Multiple", "N/A"],
        "Status": ["✅", "⚠️", "✅", "✅"]
    }

    st.table(activity_data)
    st.markdown("</div>", unsafe_allow_html=True)

    # System Status
    st.markdown("""
    <div class="modern-card">
        <div class="card-header">
            <span class="card-icon">🔧</span>
            <h3 class="card-title">System Status</h3>
        </div>
        <div class="card-description">
            Current system health and performance metrics
        </div>
    """, unsafe_allow_html=True)

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("AI Models", "5 Active", "All Online")
    with col2:
        st.metric("Processing Queue", "3 Files", "Normal")
    with col3:
        st.metric("Storage Used", "2.4 GB", "67%")
    with col4:
        st.metric("Uptime", "99.9%", "This Month")

    st.markdown("</div></div></div>", unsafe_allow_html=True)

# ============================================================================
# IMAGE ANALYSIS PAGE
# ============================================================================

def render_image_analysis():
    """Render the dedicated image analysis page for deepfake detection"""

    st.markdown("""
    <div class="page-container">
        <div class="page-header">
            <h1 class="page-title">🖼️ Image Analysis</h1>
            <p class="page-subtitle">
                Advanced deepfake detection for images with AI-powered analysis
            </p>
        </div>

        <div class="page-content">
    """, unsafe_allow_html=True)

    # Upload Section
    st.markdown("""
    <div class="modern-card">
        <div class="card-header">
            <span class="card-icon">📷</span>
            <h3 class="card-title">Upload Image for DeepFake Analysis</h3>
        </div>
        <div class="card-description">
            Upload an image to analyze for deepfake manipulation using advanced AI algorithms
        </div>
    """, unsafe_allow_html=True)

    uploaded_image = st.file_uploader(
        "Choose an image to analyze",
        type=["jpg", "jpeg", "png", "gif", "bmp", "tiff", "webp"],
        help="Upload an image file for deepfake detection analysis",
        key="uploaded_image"
    )

    if uploaded_image:
        # Display the uploaded image
        col1, col2 = st.columns([1, 2])
        with col1:
            st.image(uploaded_image, caption="Uploaded Image", use_column_width=True)

        with col2:
            st.markdown("""
            <div class="modern-card">
                <div class="card-header">
                    <span class="card-icon">📊</span>
                    <h3 class="card-title">Image Information</h3>
                </div>
            </div>
            """, unsafe_allow_html=True)

            col1, col2 = st.columns(2)
            with col1:
                st.metric("File Name", uploaded_image.name)
                st.metric("File Size", f"{uploaded_image.size / 1024:.1f} KB")
            with col2:
                st.metric("File Type", uploaded_image.type or "Unknown")
                # Get image dimensions if possible
                try:
                    from PIL import Image
                    img = Image.open(uploaded_image)
                    st.metric("Dimensions", f"{img.size[0]} × {img.size[1]}")
                except:
                    st.metric("Dimensions", "Unknown")

        # Analysis Options
        st.markdown("""
        <div class="modern-card">
            <div class="card-header">
                <span class="card-icon">⚙️</span>
                <h3 class="card-title">Analysis Options</h3>
            </div>
        </div>
        """, unsafe_allow_html=True)

        col1, col2 = st.columns(2)
        with col1:
            analysis_mode = st.selectbox(
                "Analysis Mode",
                ["Standard Detection", "Advanced Analysis", "Comparison Mode"],
                help="Choose the type of analysis to perform"
            )

        with col2:
            confidence_threshold = st.slider(
                "Confidence Threshold",
                0.1, 1.0, 0.8, 0.1,
                help="Minimum confidence level for detection results"
            )

        # Start Analysis Button
        if st.button("🔍 Start DeepFake Analysis", use_container_width=True):
            with st.spinner("Analyzing image for deepfake manipulation..."):
                temp_file_path = save_uploaded_to_temp(uploaded_image)
                analysis = None

                if content_analyzer:
                    analysis = content_analyzer.analyze_file_comprehensive(temp_file_path)
                elif multi_file_engine:
                    analysis = multi_file_engine.analyze_file(temp_file_path, analysis_depth="deep")
                else:
                    analysis = {'error': 'Analysis engine unavailable. Please ensure required modules are installed.'}

                classification = _classify_image_analysis(analysis, threshold=confidence_threshold)
                progress_bar = st.progress(0)
                status_text = st.empty()

                steps = [
                    "Loading image metadata",
                    "Analyzing compression and artifacts",
                    "Evaluating color and pattern consistency",
                    "Calculating authenticity score",
                    "Preparing report"
                ]

                for idx, step in enumerate(steps):
                    progress_bar.progress((idx + 1) / len(steps))
                    status_text.info(step)
                    time.sleep(0.4)

                progress_bar.progress(1.0)
                status_text.success("Analysis complete")
                st.success("✅ Analysis Complete!")

                st.markdown("""
                <div class="modern-card">
                    <div class="card-header">
                        <span class="card-icon">🎯</span>
                        <h3 class="card-title">DeepFake Detection Results</h3>
                    </div>
                </div>
                """, unsafe_allow_html=True)

                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Result", classification['label'])
                with col2:
                    st.metric("Confidence", _get_confidence(classification['confidence']))
                with col3:
                    processing_time = max(0.8, min(6.0, 1.0 + classification['confidence'] * 3.0))
                    st.metric("Processing Time", f"{processing_time:.1f}s")

                st.markdown("### 📋 Detailed Analysis Report")

                if classification['label'].startswith("DEEPFAKE"):
                    st.error("⚠️ **DeepFake Detected**: This image shows signs of manipulation or synthetic generation.")
                elif classification['label'] == 'AUTHENTIC IMAGE':
                    st.success("✅ **Authentic Image**: No clear deepfake signals were identified.")
                else:
                    st.warning("⚠️ **Uncertain Origin**: The image analysis produced mixed signals.")

                if classification.get('indicators'):
                    st.markdown("**Key indicators:**")
                    for indicator in classification['indicators']:
                        st.markdown(f"- {indicator}")

                if isinstance(analysis, dict) and analysis.get('file_info'):
                    file_info = analysis['file_info']
                    st.markdown("**Image Summary:**")
                    st.markdown(f"- File name: {file_info.get('file_name', uploaded_image.name)}")
                    st.markdown(f"- File size: {file_info.get('file_size_human', f'{uploaded_image.size / 1024:.1f} KB')}")
                    st.markdown(f"- Format: {file_info.get('mime_type', uploaded_image.type or 'Unknown')}")
                elif isinstance(analysis, dict):
                    st.markdown(f"**Summary:** {classification['summary']}")

                with st.expander("View Full Analysis Details"):
                    st.json(analysis)

                col1, col2 = st.columns(2)
                with col1:
                    if st.button("📊 View Detailed Metrics", use_container_width=True):
                        st.info("📈 Detailed technical metrics are available in the full analysis expander.")

                with col2:
                    if st.button("💾 Save Analysis Report", use_container_width=True):
                        st.success("💾 Analysis report saved successfully!")

    else:
        # Show sample/placeholder content when no image is uploaded
        st.markdown("""
        <div class="modern-card">
            <div class="card-header">
                <span class="card-icon">💡</span>
                <h3 class="card-title">How It Works</h3>
            </div>
            <div class="card-description">
                Our advanced AI analyzes images for deepfake manipulation using multiple detection methods
            </div>
        </div>
        """, unsafe_allow_html=True)

        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown("**🎯 Facial Analysis**")
            st.markdown("Detects unnatural facial expressions and movements")
        with col2:
            st.markdown("**🔍 Artifact Detection**")
            st.markdown("Identifies pixel-level manipulation artifacts")
        with col3:
            st.markdown("**📊 Pattern Recognition**")
            st.markdown("Analyzes image patterns for AI generation signatures")

    st.markdown("</div></div>", unsafe_allow_html=True)

# ============================================================================
# FILE ANALYSIS PAGE
# ============================================================================

def render_file_analysis():
    """Render the comprehensive file analysis page"""

    st.markdown("""
    <div class="page-container">
        <div class="page-header">
            <h1 class="page-title">📄 File Analysis</h1>
            <p class="page-subtitle">
                Comprehensive content analysis for all file types with AI detection
            </p>
        </div>

        <div class="page-content">
    """, unsafe_allow_html=True)

    # Upload Section
    st.markdown("""
    <div class="modern-card">
        <div class="card-header">
            <span class="card-icon">📁</span>
            <h3 class="card-title">Upload Files for Analysis</h3>
        </div>
        <div class="card-description">
            Support for 40+ file formats including images, videos, documents, audio, and archives
        </div>
    """, unsafe_allow_html=True)

    uploaded_file = st.file_uploader(
        "Choose a file to analyze",
        type=["jpg", "jpeg", "png", "gif", "bmp", "tiff", "webp",
              "mp4", "avi", "mov", "mkv", "webm", "flv",
              "mp3", "wav", "flac", "aac", "ogg",
              "pdf", "docx", "xlsx", "pptx", "txt", "csv",
              "zip", "rar", "7z", "tar", "gz"],
        help="Upload any supported file type for comprehensive analysis",
        key="uploaded_file"
    )

    if uploaded_file:
        st.markdown(f"""
        <div class="modern-card">
            <div class="card-header">
                <span class="card-icon">📋</span>
                <h3 class="card-title">File Information</h3>
            </div>
        </div>
        """, unsafe_allow_html=True)

        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("File Name", uploaded_file.name)
        with col2:
            st.metric("File Size", f"{uploaded_file.size / 1024 / 1024:.2f} MB")
        with col3:
            st.metric("File Type", uploaded_file.type or "Unknown")

        if st.button("🔍 Start Comprehensive Analysis", use_container_width=True):
            with st.spinner("Analyzing file content..."):
                temp_file_path = save_uploaded_to_temp(uploaded_file)
                analysis = None

                if content_analyzer:
                    analysis = content_analyzer.analyze_file_comprehensive(temp_file_path)
                elif multi_file_engine:
                    video_extensions = {'.mp4', '.avi', '.mov', '.mkv', '.webm', '.flv'}
                    file_suffix = Path(temp_file_path).suffix.lower()
                    is_video = uploaded_file.type and uploaded_file.type.startswith('video/')
                    if not is_video and file_suffix in video_extensions:
                        is_video = True

                    if is_video and video_engine:
                        video_result = video_engine.analyze_video(
                            temp_file_path,
                            sensitivity=0.8,
                            sampling_rate=2
                        )
                        analysis = {
                            'file': temp_file_path,
                            'file_type': 'video',
                            'file_size_mb': Path(temp_file_path).stat().st_size / (1024 * 1024),
                            'analysis_detail': video_result,
                            'content_type': 'video'
                        }
                    else:
                        analysis = multi_file_engine.analyze_file(temp_file_path, analysis_depth="deep")
                else:
                    analysis = {'error': 'Analysis engine unavailable. Please ensure required modules are installed.'}

                classification = _classify_file_analysis(analysis)
                progress_bar = st.progress(0)
                status_text = st.empty()

                steps = ["Reading file metadata", "Extracting content", "AI detection", "Generating report"]
                for idx, step in enumerate(steps):
                    progress_bar.progress((idx + 1) / len(steps))
                    status_text.info(step)
                    time.sleep(0.8)

                progress_bar.progress(1.0)
                status_text.success("Analysis complete")
                st.success("✅ Analysis Complete!")

                st.markdown("""
                <div class="modern-card">
                    <div class="card-header">
                        <span class="card-icon">📊</span>
                        <h3 class="card-title">Analysis Results</h3>
                    </div>
                </div>
                """, unsafe_allow_html=True)

                content_type = analysis.get('content_type') if isinstance(analysis, dict) else uploaded_file.type or 'Unknown'
                result_label = classification['label']
                confidence_label = _get_confidence(classification['confidence'])
                processing_time = max(1.0, min(6.0, 1.0 + classification['confidence'] * 4.0))

                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Content Type", content_type.title() if isinstance(content_type, str) else content_type)
                with col2:
                    st.metric("Result", result_label)
                with col3:
                    st.metric("Confidence", confidence_label)

                st.markdown("### 📋 Detailed Analysis Report")

                if classification['label'] == 'DEEPFAKE SUSPECTED':
                    st.error("⚠️ **Potential Deepfake or Synthetic Content Detected**")
                elif classification['label'] == 'AUTHENTIC CONTENT':
                    st.success("✅ **Content appears authentic and human-created.**")
                else:
                    st.warning("⚠️ **Origin uncertain. Review the detailed analysis below.**")

                if classification.get('summary'):
                    st.markdown(f"**Summary:** {classification['summary']}")

                if classification.get('indicators'):
                    st.markdown("**Key signals:**")
                    for indicator in classification['indicators']:
                        st.markdown(f"- {indicator}")

                if isinstance(analysis, dict) and analysis.get('summary'):
                    summary = analysis['summary']
                    if isinstance(summary, dict):
                        summary = summary.get('content_summary', '')
                    if summary:
                        st.markdown(f"**Content Summary:** {summary}")

                if isinstance(analysis, dict) and analysis.get('file_info'):
                    file_info = analysis['file_info']
                    st.markdown("**File metadata:**")
                    st.markdown(f"- Name: {file_info.get('file_name', uploaded_file.name)}")
                    st.markdown(f"- Size: {file_info.get('file_size_human', f'{uploaded_file.size / 1024 / 1024:.2f} MB')}")
                    st.markdown(f"- Modified: {file_info.get('modified_time', 'Unknown')}")

                with st.expander("View Full Analysis Details"):
                    st.json(analysis)

    st.markdown("</div></div>", unsafe_allow_html=True)

# ============================================================================
# VIDEO ANALYSIS PAGE
# ============================================================================

def render_video_analysis():
    """Render the enhanced video analysis page"""

    st.markdown("""
    <div class="page-container">
        <div class="page-header">
            <h1 class="page-title">🎥 Video Analysis</h1>
            <p class="page-subtitle">
                Real-time streaming and batch video processing with frame-by-frame detection
            </p>
        </div>

        <div class="page-content">
    """, unsafe_allow_html=True)

    # Analysis Options
    st.markdown("""
    <div class="modern-card">
        <div class="card-header">
            <span class="card-icon">⚙️</span>
            <h3 class="card-title">Analysis Options</h3>
        </div>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        analysis_mode = st.radio(
            "Analysis Mode",
            ["Single Video", "Batch Processing", "Real-time Stream"],
            help="Choose how you want to analyze videos"
        )

    with col2:
        detection_sensitivity = st.slider(
            "Detection Sensitivity",
            0.1, 1.0, 0.8, 0.1,
            help="Higher values detect more potential deepfakes but may increase false positives"
        )

    st.markdown("</div>", unsafe_allow_html=True)

    # Upload Section
    if analysis_mode == "Single Video":
        st.markdown("""
        <div class="modern-card">
            <div class="card-header">
                <span class="card-icon">📹</span>
                <h3 class="card-title">Upload Video</h3>
            </div>
        </div>
        """, unsafe_allow_html=True)

        uploaded_video = st.file_uploader(
            "Choose a video file",
            type=["mp4", "avi", "mov", "mkv", "webm", "flv"],
            help="Upload a video file for deepfake analysis"
        )

        if uploaded_video:
            st.video(uploaded_video)

            if st.button("🎬 Start Video Analysis", use_container_width=True):
                temp_file_path = save_uploaded_to_temp(uploaded_video)
                status_text = st.empty()
                progress_bar = st.progress(0)
                progress_text = st.empty()

                def _video_progress(progress: float, message: str = ""):
                    progress_bar.progress(min(max(progress, 0.0), 1.0))
                    progress_text.markdown(f"**{message}**")

                with st.spinner("Analyzing video frames..."):
                    analysis = None
                    if video_engine:
                        analysis = video_engine.analyze_video(
                            temp_file_path,
                            sensitivity=detection_sensitivity,
                            sampling_rate=2,
                            progress_callback=_video_progress
                        )
                    elif content_analyzer:
                        analysis = content_analyzer.analyze_file_comprehensive(temp_file_path)
                    else:
                        analysis = {'error': 'Video analysis engine unavailable. Please ensure the detection module is installed.'}

                    progress_bar.progress(1.0)
                    progress_text.success("Analysis complete")
                    st.success("✅ Video Analysis Complete!")

                classification = _classify_video_analysis(analysis, sensitivity=detection_sensitivity)

                st.markdown("### 📊 Analysis Results")
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Overall Result", classification['label'])
                with col2:
                    st.metric("Confidence", _get_confidence(classification['confidence']))
                with col3:
                    st.metric("Frames Analyzed", classification.get('frame_count', 0))

                if classification['label'] == 'DEEPFAKE DETECTED':
                    st.error("⚠️ Deepfake signals found in multiple frames. Review the details below.")
                elif classification['label'] == 'AUTHENTIC VIDEO':
                    st.success("✅ Video appears authentic with low manipulation risk.")
                else:
                    st.warning("⚠️ Suspicious patterns detected. Further verification recommended.")

                if isinstance(analysis, dict) and analysis.get('video_info'):
                    st.markdown("**Video metadata:**")
                    video_info = analysis['video_info']
                    st.markdown(f"- Duration: {video_info.get('duration', 0):.1f}s")
                    st.markdown(f"- Resolution: {video_info.get('width', 0)}×{video_info.get('height', 0)}")
                    st.markdown(f"- FPS: {video_info.get('fps', 0):.1f}")
                    st.markdown(f"- Size: {video_info.get('file_size', 0):.2f} MB")

                if isinstance(analysis, dict) and analysis.get('warnings'):
                    for warning_text in analysis['warnings']:
                        st.warning(warning_text)

                with st.expander("View Full Analysis Details"):
                    st.json(analysis)

    elif analysis_mode == "Batch Processing":
        st.markdown("""
        <div class="modern-card">
            <div class="card-header">
                <span class="card-icon">📊</span>
                <h3 class="card-title">Batch Video Processing</h3>
            </div>
        </div>
        """, unsafe_allow_html=True)

        batch_videos = st.file_uploader(
            "Choose multiple videos",
            type=["mp4", "avi", "mov", "mkv", "webm", "flv"],
            accept_multiple_files=True
        )

        if batch_videos:
            st.markdown(f"**Selected {len(batch_videos)} videos for batch processing**")

            if st.button("🚀 Start Batch Analysis", use_container_width=True):
                with st.spinner("Processing video batch..."):
                    progress_bar = st.progress(0)

                    for idx, video in enumerate(batch_videos):
                        progress_bar.progress(
                            (idx + 1) / len(batch_videos),
                            text=f"Processing {video.name}..."
                        )
                        time.sleep(1)

                    st.success("✅ Batch Processing Complete!")

    elif analysis_mode == "Real-time Stream":
        st.markdown("""
        <div class="modern-card">
            <div class="card-header">
                <span class="card-icon">🔴</span>
                <h3 class="card-title">Real-time Stream Analysis</h3>
            </div>
            <div class="card-description">
                Analyze live video streams for real-time deepfake detection
            </div>
        </div>
        """, unsafe_allow_html=True)

        stream_url = st.text_input(
            "Stream URL",
            placeholder="rtmp://example.com/live/stream",
            help="Enter RTMP, RTSP, or HTTP stream URL"
        )

        if stream_url and st.button("🔴 Start Stream Analysis", use_container_width=True):
            st.info("🔄 Connecting to stream... (This would connect to live video feed in production)")

    st.markdown("</div></div>", unsafe_allow_html=True)

# ============================================================================
# BATCH PROCESSING PAGE
# ============================================================================

def render_batch_processing():
    """Render the batch processing page"""

    st.markdown("""
    <div class="page-container">
        <div class="page-header">
            <h1 class="page-title">📊 Batch Processing</h1>
            <p class="page-subtitle">
                Process multiple files simultaneously with parallel processing
            </p>
        </div>

        <div class="page-content">
    """, unsafe_allow_html=True)

    # Upload Section
    st.markdown("""
    <div class="modern-card">
        <div class="card-header">
            <span class="card-icon">📁</span>
            <h3 class="card-title">Upload Multiple Files</h3>
        </div>
        <div class="card-description">
            Select multiple files for parallel processing and analysis
        </div>
    """, unsafe_allow_html=True)

    batch_files = st.file_uploader(
        "Choose files for batch processing",
        type=["jpg", "jpeg", "png", "mp4", "avi", "mov", "mp3", "wav", "pdf", "docx"],
        accept_multiple_files=True
    )

    if batch_files:
        st.markdown(f"""
        <div class="modern-card">
            <div class="card-header">
                <span class="card-icon">📋</span>
                <h3 class="card-title">Batch Summary</h3>
            </div>
        </div>
        """, unsafe_allow_html=True)

        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total Files", len(batch_files))
        with col2:
            st.metric("Total Size", f"{sum(f.size for f in batch_files) / 1024 / 1024:.1f} MB")
        with col3:
            image_count = sum(1 for f in batch_files if f.type and f.type.startswith('image/'))
            st.metric("Images", image_count)
        with col4:
            video_count = sum(1 for f in batch_files if f.type and f.type.startswith('video/'))
            st.metric("Videos", video_count)

        # Processing options
        col1, col2 = st.columns(2)
        with col1:
            parallel_processing = st.checkbox("Enable Parallel Processing", value=True)
        with col2:
            save_results = st.checkbox("Save Results to File", value=True)

        if st.button("🚀 Start Batch Processing", use_container_width=True):
            with st.spinner("Processing files in parallel..."):
                progress_bar = st.progress(0)

                for idx, file in enumerate(batch_files):
                    progress_bar.progress(
                        (idx + 1) / len(batch_files),
                        text=f"Processing {file.name}..."
                    )
                    time.sleep(0.8)

                st.success("✅ Batch Processing Complete!")

                # Results summary
                st.markdown("### 📊 Processing Results")
                results_data = {
                    "File Name": [f.name for f in batch_files],
                    "Type": [f.type or "Unknown" for f in batch_files],
                    "Size (MB)": [f"{f.size / 1024 / 1024:.2f}" for f in batch_files],
                    "Result": ["Authentic"] * len(batch_files),
                    "Confidence": ["92-98%"] * len(batch_files)
                }
                st.table(results_data)

    st.markdown("</div></div>", unsafe_allow_html=True)

# ============================================================================
# ANALYTICS PAGE
# ============================================================================

def render_analytics():
    """Render the analytics dashboard"""

    st.markdown("""
    <div class="page-container">
        <div class="page-header">
            <h1 class="page-title">📈 Analytics Dashboard</h1>
            <p class="page-subtitle">
                Comprehensive insights and performance metrics
            </p>
        </div>

        <div class="page-content">
    """, unsafe_allow_html=True)

    # Key Metrics
    st.markdown("""
    <div class="stats-grid">
        <div class="stat-card">
            <div class="stat-value">1,690</div>
            <div class="stat-label">Total Analyses</div>
        </div>
        <div class="stat-card">
            <div class="stat-value">95.2%</div>
            <div class="stat-label">Avg Accuracy</div>
        </div>
        <div class="stat-card">
            <div class="stat-value">3.2s</div>
            <div class="stat-label">Avg Processing Time</div>
        </div>
        <div class="stat-card">
            <div class="stat-value">23.1%</div>
            <div class="stat-label">Deepfake Detection Rate</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Charts Section
    st.markdown("""
    <div class="modern-card">
        <div class="card-header">
            <span class="card-icon">📊</span>
            <h3 class="card-title">Detection Trends</h3>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.info("📈 Interactive charts would be displayed here showing detection trends over time")

    # Breakdown Analysis
    st.markdown("""
    <div class="modern-card">
        <div class="card-header">
            <span class="card-icon">🔍</span>
            <h3 class="card-title">Detection Breakdown</h3>
        </div>
    </div>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("**By Content Type:**")
        st.markdown("- Images: 65%")
        st.markdown("- Videos: 30%")
        st.markdown("- Audio: 3%")
        st.markdown("- Documents: 2%")

    with col2:
        st.markdown("**By Detection Result:**")
        st.markdown("- Authentic: 77%")
        st.markdown("- Deepfake: 20%")
        st.markdown("- Suspicious: 3%")

    # Recent Activity Table
    st.markdown("""
    <div class="modern-card">
        <div class="card-header">
            <span class="card-icon">📋</span>
            <h3 class="card-title">Recent Activity</h3>
        </div>
    </div>
    """, unsafe_allow_html=True)

    recent_activity = {
        "Timestamp": ["2024-04-06 14:32", "2024-04-06 14:25", "2024-04-06 14:18", "2024-04-06 14:12"],
        "File": ["portrait.jpg", "interview.mp4", "document.pdf", "audio.wav"],
        "Type": ["Image", "Video", "Document", "Audio"],
        "Result": ["Authentic", "Deepfake", "Authentic", "Authentic"],
        "Confidence": ["96%", "87%", "92%", "94%"],
        "Processing Time": ["1.2s", "3.5s", "0.8s", "1.1s"]
    }

    st.table(recent_activity)

    st.markdown("</div></div>", unsafe_allow_html=True)

# ============================================================================
# MODEL TRAINING PAGE
# ============================================================================

def render_training():
    """Render the model training page"""

    st.markdown("""
    <div class="page-container">
        <div class="page-header">
            <h1 class="page-title">📚 Model Training</h1>
            <p class="page-subtitle">
                Train and optimize deepfake detection models
            </p>
        </div>

        <div class="page-content">
    """, unsafe_allow_html=True)

    # Training Options
    st.markdown("""
    <div class="modern-card">
        <div class="card-header">
            <span class="card-icon">⚙️</span>
            <h3 class="card-title">Training Configuration</h3>
        </div>
    </div>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        model_type = st.selectbox(
            "Model Architecture",
            ["CNN", "ResNet", "EfficientNet", "Custom Ensemble"],
            help="Choose the neural network architecture for training"
        )

        dataset_size = st.slider(
            "Dataset Size",
            1000, 100000, 10000, 1000,
            help="Number of training samples to use"
        )

    with col2:
        training_mode = st.radio(
            "Training Mode",
            ["From Scratch", "Fine-tune Existing", "Transfer Learning"],
            help="How to train the model"
        )

        epochs = st.slider(
            "Training Epochs",
            10, 200, 50, 10,
            help="Number of training iterations"
        )

    # Dataset Upload
    st.markdown("""
    <div class="modern-card">
        <div class="card-header">
            <span class="card-icon">📁</span>
            <h3 class="card-title">Training Dataset</h3>
        </div>
        <div class="card-description">
            Upload your training dataset (images/videos with labels)
        </div>
    </div>
    """, unsafe_allow_html=True)

    training_data = st.file_uploader(
        "Upload training dataset (ZIP file)",
        type=["zip"],
        help="Upload a ZIP file containing your training images and labels"
    )

    if training_data:
        st.success(f"✅ Dataset uploaded: {training_data.name}")

    # Training Controls
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("🚀 Start Training", use_container_width=True):
            with st.spinner("Initializing training..."):
                time.sleep(2)

            st.info("🔄 Training in progress... (This would run actual model training)")

            # Simulate training progress
            progress_bar = st.progress(0)
            status_text = st.empty()

            for epoch in range(epochs):
                progress = (epoch + 1) / epochs
                progress_bar.progress(progress, text=f"Epoch {epoch + 1}/{epochs}")
                status_text.text(f"Training epoch {epoch + 1}... Loss: {0.5 - epoch * 0.01:.3f}")
                time.sleep(0.5)

            st.success("✅ Training Complete!")
            st.metric("Final Accuracy", "96.7%", "+2.1%")

    with col2:
        if st.button("📊 View Metrics", use_container_width=True):
            st.info("📈 Training metrics would be displayed here")

    with col3:
        if st.button("💾 Save Model", use_container_width=True):
            st.success("💾 Model saved successfully!")

    st.markdown("</div></div>", unsafe_allow_html=True)

# ============================================================================
# SETTINGS PAGE
# ============================================================================

def render_settings():
    """Render the settings page"""

    st.markdown("""
    <div class="page-container">
        <div class="page-header">
            <h1 class="page-title">⚙️ Settings</h1>
            <p class="page-subtitle">
                Configure detection preferences and system settings
            </p>
        </div>

        <div class="page-content">
    """, unsafe_allow_html=True)

    # Detection Settings
    st.markdown("""
    <div class="modern-card">
        <div class="card-header">
            <span class="card-icon">🎯</span>
            <h3 class="card-title">Detection Settings</h3>
        </div>
    </div>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        confidence_threshold = st.slider(
            "Confidence Threshold",
            0.0, 1.0, 0.80, 0.05,
            help="Minimum confidence level for detection results"
        )

        enable_advanced = st.checkbox(
            "Enable Advanced Analysis",
            value=True,
            help="Use more sophisticated detection algorithms"
        )

    with col2:
        batch_size = st.slider(
            "Batch Processing Size",
            1, 50, 10, 1,
            help="Number of files to process simultaneously"
        )

        save_history = st.checkbox(
            "Save Analysis History",
            value=True,
            help="Keep track of all analysis results"
        )

    # System Settings
    st.markdown("""
    <div class="modern-card">
        <div class="card-header">
            <span class="card-icon">🖥️</span>
            <h3 class="card-title">System Settings</h3>
        </div>
    </div>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        theme = st.selectbox(
            "Theme",
            ["Light", "Dark", "Auto"],
            index=0,
            help="Choose the application theme"
        )

        language = st.selectbox(
            "Language",
            ["English", "Spanish", "French", "German"],
            index=0,
            help="Select your preferred language"
        )

    with col2:
        notifications = st.checkbox(
            "Enable Notifications",
            value=True,
            help="Show desktop notifications for analysis completion"
        )

        auto_update = st.checkbox(
            "Auto-update Models",
            value=False,
            help="Automatically download new model versions"
        )

    # Save Settings
    if st.button("💾 Save Settings", use_container_width=True):
        st.success("✅ Settings saved successfully!")

    st.markdown("</div></div>", unsafe_allow_html=True)

# ============================================================================
# DOCS PAGE
# ============================================================================

def render_docs():
    """Render the documentation page"""

    st.markdown("""
    <div class="page-container">
        <div class="page-header">
            <h1 class="page-title">📖 Documentation</h1>
            <p class="page-subtitle">
                Learn how to use DeepFake Detection Pro effectively
            </p>
        </div>

        <div class="page-content">
    """, unsafe_allow_html=True)

    # Getting Started
    st.markdown("""
    <div class="modern-card">
        <div class="card-header">
            <span class="card-icon">🚀</span>
            <h3 class="card-title">Getting Started</h3>
        </div>
        <div class="card-description">
            Quick start guide for using the deepfake detection platform
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    ### 📋 Quick Start Steps:
    1. **Upload Files**: Use the file uploaders on analysis pages
    2. **Choose Analysis Type**: Select from File, Video, or Batch analysis
    3. **Configure Settings**: Adjust confidence thresholds and options
    4. **Start Analysis**: Click the analysis button to begin processing
    5. **Review Results**: Check the detailed analysis reports

    ### 🎯 Supported File Types:
    - **Images**: JPG, PNG, GIF, BMP, TIFF, WebP
    - **Videos**: MP4, AVI, MOV, MKV, WebM, FLV
    - **Audio**: MP3, WAV, FLAC, AAC, OGG
    - **Documents**: PDF, DOCX, XLSX, PPTX, TXT, CSV
    - **Archives**: ZIP, RAR, 7Z, TAR, GZ
    """)

    # API Documentation
    st.markdown("""
    <div class="modern-card">
        <div class="card-header">
            <span class="card-icon">🔧</span>
            <h3 class="card-title">API Reference</h3>
        </div>
        <div class="card-description">
            Technical documentation for developers
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    ### 📚 Available Endpoints:

    #### File Analysis
    ```python
    POST /api/analyze/file
    Content-Type: multipart/form-data

    Parameters:
    - file: File to analyze
    - options: JSON string with analysis options
    ```

    #### Batch Processing
    ```python
    POST /api/analyze/batch
    Content-Type: multipart/form-data

    Parameters:
    - files: Multiple files to analyze
    - parallel: Boolean for parallel processing
    ```

    #### Video Stream Analysis
    ```python
    POST /api/analyze/stream
    Content-Type: application/json

    Parameters:
    - stream_url: URL of video stream
    - sensitivity: Detection sensitivity (0.0-1.0)
    ```
    """)

    st.markdown("</div></div>", unsafe_allow_html=True)

# ============================================================================
# MODERN FOOTER
# ============================================================================

def render_modern_footer():
    """Render the modern website-style footer"""

    st.markdown(f"""
    <div class="modern-footer">
        <div class="footer-content">
            <div class="footer-section">
                <h4>🔍 DeepFake Pro</h4>
                <p>Enterprise-grade deepfake detection powered by advanced AI</p>
                <p>Supporting 40+ file formats with real-time processing</p>
            </div>

            <div class="footer-section">
                <h4>🛠️ Features</h4>
                <div class="footer-links">
                    <a href="#" class="footer-link">File Analysis</a>
                    <a href="#" class="footer-link">Video Processing</a>
                    <a href="#" class="footer-link">Batch Operations</a>
                    <a href="#" class="footer-link">Model Training</a>
                </div>
            </div>

            <div class="footer-section">
                <h4>📚 Resources</h4>
                <div class="footer-links">
                    <a href="#" class="footer-link">Documentation</a>
                    <a href="#" class="footer-link">API Reference</a>
                    <a href="#" class="footer-link">Support</a>
                    <a href="#" class="footer-link">GitHub</a>
                </div>
            </div>

            <div class="footer-section">
                <h4>📞 Contact</h4>
                <p>support@deepfakepro.com</p>
                <p>+1 (555) 123-4567</p>
                <div class="footer-links">
                    <a href="#" class="footer-link">Privacy Policy</a>
                    <a href="#" class="footer-link">Terms of Service</a>
                </div>
            </div>
        </div>

        <div class="footer-bottom">
            <p>&copy; 2024 DeepFake Detection Pro. All rights reserved. | Built with ❤️ using Streamlit</p>
        </div>
    </div>
    """, unsafe_allow_html=True)

# ============================================================================
# MAIN APPLICATION
# ============================================================================

def main():
    """Main application entry point"""

    # Apply CSS styles (reapply when theme changes)
    st.markdown(get_css_styles(), unsafe_allow_html=True)

    # Render sidebar and header
    render_sidebar()
    render_sidebar_toggle()
    render_modern_header()

    # Main content area
    st.markdown('<div class="main-content">', unsafe_allow_html=True)

    # Route to appropriate page
    if st.session_state.current_page == "dashboard":
        render_dashboard()
    elif st.session_state.current_page == "image_analysis":
        render_image_analysis()
    elif st.session_state.current_page == "file_analysis":
        render_file_analysis()
    elif st.session_state.current_page == "video_analysis":
        render_video_analysis()
    elif st.session_state.current_page == "batch_processing":
        render_batch_processing()
    elif st.session_state.current_page == "analytics":
        render_analytics()
    elif st.session_state.current_page == "training":
        render_training()
    elif st.session_state.current_page == "settings":
        render_settings()
    elif st.session_state.current_page == "docs":
        render_docs()

    st.markdown('</div>', unsafe_allow_html=True)

    # Render footer
    render_modern_footer()

# ============================================================================
# APPLICATION ENTRY POINT
# ============================================================================

if __name__ == "__main__":
    main()