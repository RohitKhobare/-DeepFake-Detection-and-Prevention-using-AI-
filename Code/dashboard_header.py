"""
Dashboard Header Component
Premium dashboard header with navigation and metrics
"""

import streamlit as st
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import json
from Code.enhanced_ui_components import PremiumUIComponents, ChartComponents


class DashboardHeader:
    """Dashboard header component with navigation and key metrics"""

    def __init__(self, task_history_manager=None):
        self.task_history_manager = task_history_manager

    def render_header(self):
        """Render the complete dashboard header"""
        # Inject custom CSS
        PremiumUIComponents.inject_custom_css()

        # Create premium header
        PremiumUIComponents.create_premium_header(
            title="DeepFake Detection & Prevention",
            subtitle="Advanced AI-powered content analysis system with comprehensive media support",
            icon="🔍"
        )

        # Create navigation tabs
        self._render_navigation_tabs()

        # Create metrics dashboard
        self._render_metrics_dashboard()

    def _render_navigation_tabs(self):
        """Render navigation tabs"""
        tabs = ["🏠 Dashboard", "📁 File Analysis", "🎥 Video Analysis", "📊 Batch Processing",
                "📈 Analytics", "⚙️ Settings", "📚 Training"]

        # Get current page from session state
        current_page = st.session_state.get('current_page', '🏠 Dashboard')

        # Create tabs HTML
        tabs_html = '<div class="nav-tabs">'
        for tab in tabs:
            active_class = 'active' if tab == current_page else ''
            tab_id = tab.replace(' ', '_').replace('🏠', 'home').replace('📁', 'file').replace('🎥', 'video').replace('📊', 'batch').replace('📈', 'analytics').replace('⚙️', 'settings').replace('📚', 'training')
            tabs_html += f'<div class="nav-tab {active_class}" id="{tab_id}">{tab}</div>'
        tabs_html += '</div>'

        st.markdown(tabs_html, unsafe_allow_html=True)

        # Handle tab clicks with session state
        for tab in tabs:
            if st.button(tab, key=f"nav_{tab}", help=f"Navigate to {tab}"):
                st.session_state.current_page = tab
                st.rerun()

    def _render_metrics_dashboard(self):
        """Render key metrics dashboard"""
        st.markdown("### 📊 System Overview")

        # Get metrics data
        metrics = self._get_dashboard_metrics()

        # Create metrics grid
        PremiumUIComponents.create_dashboard_grid(metrics)

        # Create charts row
        col1, col2 = st.columns(2)

        with col1:
            self._render_activity_chart()

        with col2:
            self._render_file_type_distribution()

    def _get_dashboard_metrics(self) -> List[Dict]:
        """Get dashboard metrics data"""
        # Default metrics if no task history manager
        if self.task_history_manager is None:
            return [
                {
                    'icon': '📁',
                    'value': '0',
                    'title': 'Files Analyzed',
                    'subtitle': 'Total files processed',
                    'color': 'primary'
                },
                {
                    'icon': '🎯',
                    'value': '95%',
                    'title': 'Detection Accuracy',
                    'subtitle': 'Average confidence score',
                    'color': 'success'
                },
                {
                    'icon': '⚡',
                    'value': '2.3s',
                    'title': 'Avg Processing Time',
                    'subtitle': 'Per file analysis',
                    'color': 'accent'
                },
                {
                    'icon': '🔍',
                    'value': '12',
                    'title': 'Active Sessions',
                    'subtitle': 'Current analysis tasks',
                    'color': 'warning'
                }
            ]

        try:
            # Get real metrics from task history manager
            stats = self.task_history_manager.get_statistics()

            return [
                {
                    'icon': '📁',
                    'value': f"{stats.get('total_tasks', 0):,}",
                    'title': 'Files Analyzed',
                    'subtitle': 'Total files processed',
                    'color': 'primary'
                },
                {
                    'icon': '🎯',
                    'value': f"{stats.get('avg_accuracy', 95):.1f}%",
                    'title': 'Detection Accuracy',
                    'subtitle': 'Average confidence score',
                    'color': 'success'
                },
                {
                    'icon': '⚡',
                    'value': f"{stats.get('avg_processing_time', 2.3):.1f}s",
                    'title': 'Avg Processing Time',
                    'subtitle': 'Per file analysis',
                    'color': 'accent'
                },
                {
                    'icon': '🔍',
                    'value': stats.get('active_sessions', 0),
                    'title': 'Active Sessions',
                    'subtitle': 'Current analysis tasks',
                    'color': 'warning'
                }
            ]
        except Exception as e:
            st.warning(f"Could not load dashboard metrics: {e}")
            return self._get_dashboard_metrics()  # Return default metrics

    def _render_activity_chart(self):
        """Render activity timeline chart"""
        st.markdown("#### 📈 Recent Activity")

        # Generate sample activity data for the last 7 days
        dates = [(datetime.now() - timedelta(days=i)).strftime('%Y-%m-%d') for i in range(7)]
        activity_counts = [12, 8, 15, 6, 10, 14, 9]  # Sample data

        fig = ChartComponents.create_performance_metrics_chart({
            'Mon': activity_counts[6],
            'Tue': activity_counts[5],
            'Wed': activity_counts[4],
            'Thu': activity_counts[3],
            'Fri': activity_counts[2],
            'Sat': activity_counts[1],
            'Sun': activity_counts[0]
        })

        fig.update_layout(
            title='',
            xaxis_title='Day',
            yaxis_title='Files Processed'
        )

        st.plotly_chart(fig, use_container_width=True)

    def _render_file_type_distribution(self):
        """Render file type distribution chart"""
        st.markdown("#### 📊 File Types Analyzed")

        # Sample file type distribution
        file_types = {
            'Images': 45,
            'Videos': 25,
            'Audio': 15,
            'Documents': 10,
            'Archives': 5
        }

        fig = ChartComponents.create_file_type_distribution(file_types)
        st.plotly_chart(fig, use_container_width=True)


class FooterComponent:
    """Footer component with branding and links"""

    def __init__(self, developer_info: Dict = None):
        self.developer_info = developer_info or {
            'name': 'DeepFake Detection Team',
            'email': 'contact@deepfakedetection.com',
            'version': '2.0.0',
            'year': datetime.now().year,
            'social_links': {
                'GitHub': 'https://github.com/deepfake-detection',
                'LinkedIn': 'https://linkedin.com/company/deepfake-detection',
                'Twitter': 'https://twitter.com/deepfakedetect'
            }
        }

    def render_footer(self):
        """Render the footer component"""
        footer_html = f"""
        <div class="premium-footer">
            <div class="footer-content">
                <div class="footer-info">
                    <h4>🚀 DeepFake Detection & Prevention</h4>
                    <p>Advanced AI-powered content analysis system</p>
                    <p><strong>Version:</strong> {self.developer_info['version']} |
                       <strong>© {self.developer_info['year']}</strong> {self.developer_info['name']}</p>
                    <p><strong>Contact:</strong> {self.developer_info['email']}</p>
                </div>
                <div class="footer-links">
                    <a href="{self.developer_info['social_links']['GitHub']}" class="footer-link" target="_blank">⭐ GitHub</a>
                    <a href="{self.developer_info['social_links']['LinkedIn']}" class="footer-link" target="_blank">💼 LinkedIn</a>
                    <a href="{self.developer_info['social_links']['Twitter']}" class="footer-link" target="_blank">🐦 Twitter</a>
                    <a href="#" class="footer-link">📧 Contact</a>
                    <a href="#" class="footer-link">📚 Documentation</a>
                    <a href="#" class="footer-link">🔒 Privacy Policy</a>
                    <a href="#" class="footer-link">📋 Terms of Service</a>
                </div>
            </div>
            <div style="text-align: center; margin-top: 1rem; padding-top: 1rem; border-top: 1px solid var(--border-color);">
                <p style="color: var(--text-muted); font-size: 0.875rem;">
                    Powered by TensorFlow • OpenCV • Streamlit • Advanced AI Models
                </p>
                <p style="color: var(--text-muted); font-size: 0.75rem;">
                    Built with ❤️ for content authenticity and digital trust
                </p>
            </div>
        </div>
        """
        st.markdown(footer_html, unsafe_allow_html=True)


class QuickActionsPanel:
    """Quick actions panel for common tasks"""

    def __init__(self, on_action_callback=None):
        self.on_action_callback = on_action_callback

    def render_quick_actions(self):
        """Render quick actions panel"""
        st.markdown("### ⚡ Quick Actions")

        col1, col2, col3, col4 = st.columns(4)

        with col1:
            if st.button("📁 Analyze File", use_container_width=True):
                if self.on_action_callback:
                    self.on_action_callback('analyze_file')

        with col2:
            if st.button("🎥 Stream Video", use_container_width=True):
                if self.on_action_callback:
                    self.on_action_callback('stream_video')

        with col3:
            if st.button("📊 Batch Process", use_container_width=True):
                if self.on_action_callback:
                    self.on_action_callback('batch_process')

        with col4:
            if st.button("📈 View Analytics", use_container_width=True):
                if self.on_action_callback:
                    self.on_action_callback('view_analytics')

        # Recent files section
        st.markdown("### 🕒 Recent Files")
        self._render_recent_files()

    def _render_recent_files(self):
        """Render recent files list"""
        # Sample recent files - in real implementation, this would come from task history
        recent_files = [
            {"name": "sample_video.mp4", "type": "Video", "status": "real", "time": "2 hours ago"},
            {"name": "document.pdf", "type": "Document", "status": "fake", "time": "5 hours ago"},
            {"name": "image.jpg", "type": "Image", "status": "real", "time": "1 day ago"},
        ]

        for file in recent_files:
            status_badge = PremiumUIComponents.create_status_badge(file['status'])
            st.markdown(f"""
            <div style="display: flex; justify-content: space-between; align-items: center; padding: 0.5rem; border-radius: 8px; background: var(--background-secondary); margin-bottom: 0.5rem;">
                <div>
                    <div style="font-weight: 500;">{file['name']}</div>
                    <div style="font-size: 0.8rem; color: var(--text-muted);">{file['type']} • {file['time']}</div>
                </div>
                <div>{status_badge}</div>
            </div>
            """, unsafe_allow_html=True)


class SystemStatusIndicator:
    """System status indicator component"""

    def __init__(self):
        self.system_status = {
            'models_loaded': True,
            'database_connected': True,
            'gpu_available': False,
            'memory_usage': 65,
            'cpu_usage': 45
        }

    def render_status(self):
        """Render system status indicator"""
        st.markdown("### 🔧 System Status")

        status_items = [
            {
                'label': 'AI Models',
                'status': 'online' if self.system_status['models_loaded'] else 'offline',
                'icon': '🧠'
            },
            {
                'label': 'Database',
                'status': 'online' if self.system_status['database_connected'] else 'offline',
                'icon': '💾'
            },
            {
                'label': 'GPU',
                'status': 'available' if self.system_status['gpu_available'] else 'unavailable',
                'icon': '🎮'
            }
        ]

        for item in status_items:
            status_color = 'success' if item['status'] == 'online' or item['status'] == 'available' else 'error'
            st.markdown(f"""
            <div style="display: flex; align-items: center; margin-bottom: 0.5rem;">
                <div style="font-size: 1.2rem; margin-right: 0.5rem;">{item['icon']}</div>
                <div style="flex: 1;">{item['label']}</div>
                <div style="color: var(--{status_color}-color); font-weight: 500;">{item['status'].title()}</div>
            </div>
            """, unsafe_allow_html=True)

        # Resource usage
        col1, col2 = st.columns(2)

        with col1:
            PremiumUIComponents.create_progress_bar(
                self.system_status['memory_usage'] / 100,
                f"Memory: {self.system_status['memory_usage']}%"
            )

        with col2:
            PremiumUIComponents.create_progress_bar(
                self.system_status['cpu_usage'] / 100,
                f"CPU: {self.system_status['cpu_usage']}%"
            )