"""
Enhanced UI Components Library
Premium UI components for the deepfake detection application
"""

import streamlit as st
import streamlit.components.v1 as components
from typing import Dict, List, Optional, Any, Callable, Tuple
import json
from datetime import datetime, timedelta
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import base64
from pathlib import Path
import time


class PremiumUIComponents:
    """Premium UI components for enhanced user experience"""

    @staticmethod
    def inject_custom_css():
        """Inject custom CSS for premium styling"""
        custom_css = """
        <style>
        /* Premium color scheme */
        :root {
            --primary-color: #6366f1;
            --secondary-color: #8b5cf6;
            --accent-color: #06b6d4;
            --success-color: #10b981;
            --warning-color: #f59e0b;
            --error-color: #ef4444;
            --background-primary: #ffffff;
            --background-secondary: #f8fafc;
            --background-tertiary: #f1f5f9;
            --text-primary: #1e293b;
            --text-secondary: #64748b;
            --text-muted: #94a3b8;
            --border-color: #e2e8f0;
            --shadow-sm: 0 1px 2px 0 rgb(0 0 0 / 0.05);
            --shadow-md: 0 4px 6px -1px rgb(0 0 0 / 0.1);
            --shadow-lg: 0 10px 15px -3px rgb(0 0 0 / 0.1);
            --shadow-xl: 0 20px 25px -5px rgb(0 0 0 / 0.1);
            --border-radius-sm: 0.375rem;
            --border-radius-md: 0.5rem;
            --border-radius-lg: 0.75rem;
            --border-radius-xl: 1rem;
        }

        /* Global styles */
        .main {
            background: linear-gradient(135deg, var(--background-secondary) 0%, var(--background-primary) 100%);
        }

        /* Header styles */
        .premium-header {
            background: linear-gradient(135deg, var(--primary-color) 0%, var(--secondary-color) 100%);
            color: white;
            padding: 2rem;
            border-radius: var(--border-radius-xl);
            box-shadow: var(--shadow-xl);
            margin-bottom: 2rem;
            text-align: center;
        }

        .premium-header h1 {
            font-size: 2.5rem;
            font-weight: 700;
            margin-bottom: 0.5rem;
            text-shadow: 0 2px 4px rgba(0,0,0,0.3);
        }

        .premium-header p {
            font-size: 1.1rem;
            opacity: 0.9;
            margin: 0;
        }

        /* Footer styles */
        .premium-footer {
            background: var(--background-tertiary);
            padding: 2rem;
            border-radius: var(--border-radius-lg);
            margin-top: 3rem;
            border-top: 2px solid var(--primary-color);
            text-align: center;
        }

        .footer-content {
            display: flex;
            justify-content: space-between;
            align-items: center;
            flex-wrap: wrap;
            gap: 1rem;
        }

        .footer-info h4 {
            color: var(--primary-color);
            margin-bottom: 0.5rem;
        }

        .footer-links {
            display: flex;
            gap: 1rem;
            flex-wrap: wrap;
        }

        .footer-link {
            color: var(--text-secondary);
            text-decoration: none;
            padding: 0.5rem 1rem;
            border-radius: var(--border-radius-md);
            transition: all 0.3s ease;
        }

        .footer-link:hover {
            background: var(--primary-color);
            color: white;
            text-decoration: none;
        }

        /* Card styles */
        .premium-card {
            background: var(--background-primary);
            border-radius: var(--border-radius-lg);
            box-shadow: var(--shadow-md);
            padding: 1.5rem;
            margin-bottom: 1.5rem;
            border: 1px solid var(--border-color);
            transition: all 0.3s ease;
        }

        .premium-card:hover {
            box-shadow: var(--shadow-lg);
            transform: translateY(-2px);
        }

        .card-header {
            display: flex;
            align-items: center;
            margin-bottom: 1rem;
        }

        .card-icon {
            font-size: 1.5rem;
            margin-right: 0.75rem;
            color: var(--primary-color);
        }

        .card-title {
            font-size: 1.25rem;
            font-weight: 600;
            color: var(--text-primary);
            margin: 0;
        }

        /* Button styles */
        .premium-button {
            background: linear-gradient(135deg, var(--primary-color) 0%, var(--secondary-color) 100%);
            color: white;
            border: none;
            padding: 0.75rem 1.5rem;
            border-radius: var(--border-radius-md);
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s ease;
            box-shadow: var(--shadow-md);
        }

        .premium-button:hover {
            transform: translateY(-2px);
            box-shadow: var(--shadow-lg);
        }

        .premium-button.secondary {
            background: linear-gradient(135deg, var(--accent-color) 0%, var(--primary-color) 100%);
        }

        .premium-button.success {
            background: linear-gradient(135deg, var(--success-color) 0%, var(--primary-color) 100%);
        }

        /* Status badges */
        .status-badge {
            display: inline-block;
            padding: 0.25rem 0.75rem;
            border-radius: var(--border-radius-xl);
            font-size: 0.875rem;
            font-weight: 500;
            text-transform: uppercase;
        }

        .status-badge.real {
            background: var(--success-color);
            color: white;
        }

        .status-badge.fake {
            background: var(--error-color);
            color: white;
        }

        .status-badge.suspicious {
            background: var(--warning-color);
            color: white;
        }

        .status-badge.processing {
            background: var(--accent-color);
            color: white;
        }

        /* Progress bar */
        .premium-progress {
            width: 100%;
            height: 8px;
            background: var(--background-tertiary);
            border-radius: var(--border-radius-xl);
            overflow: hidden;
            margin: 1rem 0;
        }

        .progress-fill {
            height: 100%;
            background: linear-gradient(90deg, var(--primary-color) 0%, var(--accent-color) 100%);
            border-radius: var(--border-radius-xl);
            transition: width 0.3s ease;
        }

        /* Metric cards */
        .metric-card {
            background: var(--background-primary);
            border-radius: var(--border-radius-lg);
            padding: 1.5rem;
            text-align: center;
            box-shadow: var(--shadow-sm);
            border: 1px solid var(--border-color);
        }

        .metric-value {
            font-size: 2rem;
            font-weight: 700;
            color: var(--primary-color);
            margin-bottom: 0.5rem;
        }

        .metric-label {
            font-size: 0.875rem;
            color: var(--text-secondary);
            text-transform: uppercase;
            letter-spacing: 0.05em;
        }

        /* Navigation tabs */
        .nav-tabs {
            display: flex;
            background: var(--background-primary);
            border-radius: var(--border-radius-lg);
            padding: 0.5rem;
            margin-bottom: 2rem;
            box-shadow: var(--shadow-sm);
        }

        .nav-tab {
            flex: 1;
            text-align: center;
            padding: 0.75rem 1rem;
            border-radius: var(--border-radius-md);
            cursor: pointer;
            transition: all 0.3s ease;
            font-weight: 500;
            color: var(--text-secondary);
        }

        .nav-tab.active {
            background: linear-gradient(135deg, var(--primary-color) 0%, var(--secondary-color) 100%);
            color: white;
            box-shadow: var(--shadow-md);
        }

        .nav-tab:hover:not(.active) {
            background: var(--background-tertiary);
            color: var(--text-primary);
        }

        /* File upload area */
        .upload-area {
            border: 2px dashed var(--border-color);
            border-radius: var(--border-radius-lg);
            padding: 2rem;
            text-align: center;
            background: var(--background-secondary);
            transition: all 0.3s ease;
            cursor: pointer;
        }

        .upload-area:hover {
            border-color: var(--primary-color);
            background: var(--background-primary);
        }

        .upload-icon {
            font-size: 3rem;
            color: var(--text-muted);
            margin-bottom: 1rem;
        }

        .upload-text {
            color: var(--text-secondary);
            margin: 0;
        }

        /* Results display */
        .result-item {
            display: flex;
            align-items: center;
            padding: 1rem;
            border-radius: var(--border-radius-md);
            background: var(--background-primary);
            margin-bottom: 0.75rem;
            box-shadow: var(--shadow-sm);
            border: 1px solid var(--border-color);
        }

        .result-icon {
            font-size: 1.5rem;
            margin-right: 1rem;
        }

        .result-content {
            flex: 1;
        }

        .result-title {
            font-weight: 600;
            color: var(--text-primary);
            margin-bottom: 0.25rem;
        }

        .result-details {
            color: var(--text-secondary);
            font-size: 0.875rem;
        }

        /* Dashboard grid */
        .dashboard-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 1.5rem;
            margin-bottom: 2rem;
        }

        /* Animation classes */
        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(20px); }
            to { opacity: 1; transform: translateY(0); }
        }

        @keyframes pulse {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.7; }
        }

        .fade-in {
            animation: fadeIn 0.5s ease-out;
        }

        .pulse {
            animation: pulse 2s infinite;
        }

        /* Responsive design */
        @media (max-width: 768px) {
            .premium-header h1 {
                font-size: 2rem;
            }

            .footer-content {
                flex-direction: column;
                text-align: center;
            }

            .nav-tabs {
                flex-direction: column;
            }

            .dashboard-grid {
                grid-template-columns: 1fr;
            }
        }

        /* Dark theme support */
        @media (prefers-color-scheme: dark) {
            :root {
                --background-primary: #1e293b;
                --background-secondary: #0f172a;
                --background-tertiary: #334155;
                --text-primary: #f1f5f9;
                --text-secondary: #cbd5e1;
                --text-muted: #94a3b8;
                --border-color: #475569;
            }
        }
        </style>
        """
        st.markdown(custom_css, unsafe_allow_html=True)

    @staticmethod
    def create_premium_header(title: str, subtitle: str = "", icon: str = "🔍"):
        """Create premium header component"""
        header_html = f"""
        <div class="premium-header fade-in">
            <h1>{icon} {title}</h1>
            {f'<p>{subtitle}</p>' if subtitle else ''}
        </div>
        """
        st.markdown(header_html, unsafe_allow_html=True)

    @staticmethod
    def create_premium_footer(developer_info: Dict = None):
        """Create premium footer component"""
        if developer_info is None:
            developer_info = {
                'name': 'DeepFake Detection Team',
                'email': 'contact@deepfakedetection.com',
                'version': '2.0.0',
                'year': datetime.now().year
            }

        footer_html = f"""
        <div class="premium-footer">
            <div class="footer-content">
                <div class="footer-info">
                    <h4>🚀 DeepFake Detection & Prevention</h4>
                    <p>Advanced AI-powered content analysis system</p>
                    <p><strong>Version:</strong> {developer_info['version']} | <strong>© {developer_info['year']}</strong></p>
                </div>
                <div class="footer-links">
                    <a href="#" class="footer-link">📧 Contact</a>
                    <a href="#" class="footer-link">📚 Documentation</a>
                    <a href="#" class="footer-link">🔒 Privacy Policy</a>
                    <a href="#" class="footer-link">📋 Terms of Service</a>
                    <a href="#" class="footer-link">⭐ GitHub</a>
                </div>
            </div>
        </div>
        """
        st.markdown(footer_html, unsafe_allow_html=True)

    @staticmethod
    def create_metric_card(title: str, value: Any, subtitle: str = "", icon: str = "", color: str = "primary"):
        """Create metric card component"""
        card_html = f"""
        <div class="metric-card fade-in">
            {f'<div class="card-icon">{icon}</div>' if icon else ''}
            <div class="metric-value">{value}</div>
            <div class="metric-label">{title}</div>
            {f'<div style="font-size: 0.75rem; color: var(--text-muted); margin-top: 0.25rem;">{subtitle}</div>' if subtitle else ''}
        </div>
        """
        st.markdown(card_html, unsafe_allow_html=True)

    @staticmethod
    def create_status_badge(status: str, text: str = None) -> str:
        """Create status badge"""
        if text is None:
            text = status.title()

        status_class = status.lower()
        if status_class not in ['real', 'fake', 'suspicious', 'processing']:
            status_class = 'processing'

        badge_html = f'<span class="status-badge {status_class}">{text}</span>'
        return badge_html

    @staticmethod
    def create_progress_bar(progress: float, label: str = "", show_percentage: bool = True):
        """Create premium progress bar"""
        percentage = int(progress * 100)
        progress_html = f"""
        <div class="premium-progress">
            <div class="progress-fill" style="width: {percentage}%"></div>
        </div>
        {f'<div style="text-align: center; color: var(--text-secondary); font-size: 0.875rem;">{label} {percentage}%</div>' if show_percentage else ''}
        """
        st.markdown(progress_html, unsafe_allow_html=True)

    @staticmethod
    def create_navigation_tabs(tabs: List[str], active_tab: str = None) -> str:
        """Create navigation tabs"""
        if active_tab is None:
            active_tab = tabs[0] if tabs else ""

        tab_html = '<div class="nav-tabs">'
        for tab in tabs:
            active_class = 'active' if tab == active_tab else ''
            tab_html += f'<div class="nav-tab {active_class}" onclick="selectTab(\'{tab}\')">{tab}</div>'
        tab_html += '</div>'

        # Add JavaScript for tab selection (simplified)
        tab_html += '''
        <script>
        function selectTab(tabName) {
            // This would be handled by Streamlit session state in practice
            console.log('Selected tab:', tabName);
        }
        </script>
        '''

        return tab_html

    @staticmethod
    def create_file_upload_area(accept_types: List[str] = None, multiple: bool = True):
        """Create premium file upload area"""
        if accept_types is None:
            accept_types = ['image/*', 'video/*', 'audio/*', '.pdf', '.docx', '.txt']

        accept_string = ', '.join(accept_types)

        upload_html = f"""
        <div class="upload-area" onclick="document.getElementById('file-upload').click()">
            <div class="upload-icon">📁</div>
            <h3>Drop files here or click to browse</h3>
            <p class="upload-text">Supports: {accept_string}</p>
            <p class="upload-text">Maximum file size: 100MB per file</p>
        </div>
        <input type="file" id="file-upload" multiple={"multiple" if multiple else ""} accept="{accept_string}" style="display: none;">
        """

        st.markdown(upload_html, unsafe_allow_html=True)
        return st.file_uploader("", accept_multiple_files=multiple, type=None, key="premium_upload")

    @staticmethod
    def create_result_item(title: str, details: str, status: str, confidence: float = None, icon: str = ""):
        """Create result item component"""
        status_badge = PremiumUIComponents.create_status_badge(status)

        confidence_html = ""
        if confidence is not None:
            confidence_pct = int(confidence * 100)
            confidence_html = f'<div style="font-size: 0.75rem; color: var(--text-muted);">Confidence: {confidence_pct}%</div>'

        result_html = f"""
        <div class="result-item fade-in">
            {f'<div class="result-icon">{icon}</div>' if icon else ''}
            <div class="result-content">
                <div class="result-title">{title}</div>
                <div class="result-details">{details}</div>
                {confidence_html}
            </div>
            <div>{status_badge}</div>
        </div>
        """
        st.markdown(result_html, unsafe_allow_html=True)

    @staticmethod
    def create_dashboard_grid(metrics: List[Dict]):
        """Create dashboard grid with metrics"""
        grid_html = '<div class="dashboard-grid">'

        for metric in metrics:
            icon = metric.get('icon', '📊')
            value = metric.get('value', '0')
            title = metric.get('title', 'Metric')
            subtitle = metric.get('subtitle', '')
            color = metric.get('color', 'primary')

            grid_html += f"""
            <div class="metric-card fade-in">
                <div class="card-icon">{icon}</div>
                <div class="metric-value" style="color: var(--{color}-color);">{value}</div>
                <div class="metric-label">{title}</div>
                {f'<div style="font-size: 0.75rem; color: var(--text-muted); margin-top: 0.25rem;">{subtitle}</div>' if subtitle else ''}
            </div>
            """

        grid_html += '</div>'
        st.markdown(grid_html, unsafe_allow_html=True)

    @staticmethod
    def create_premium_card(title: str, content: str = "", icon: str = "", actions: List[Dict] = None):
        """Create premium card component"""
        card_html = f"""
        <div class="premium-card fade-in">
            <div class="card-header">
                {f'<div class="card-icon">{icon}</div>' if icon else ''}
                <h3 class="card-title">{title}</h3>
            </div>
            {f'<div>{content}</div>' if content else ''}
        """

        if actions:
            card_html += '<div style="margin-top: 1rem; display: flex; gap: 0.5rem; flex-wrap: wrap;">'
            for action in actions:
                btn_class = action.get('class', 'premium-button')
                btn_text = action.get('text', 'Action')
                btn_icon = action.get('icon', '')
                card_html += f'<button class="{btn_class}">{btn_icon} {btn_text}</button>'
            card_html += '</div>'

        card_html += '</div>'
        st.markdown(card_html, unsafe_allow_html=True)

    @staticmethod
    def create_loading_animation(message: str = "Processing..."):
        """Create loading animation"""
        loading_html = f"""
        <div style="text-align: center; padding: 2rem;">
            <div class="pulse" style="font-size: 2rem; margin-bottom: 1rem;">⏳</div>
            <div style="color: var(--text-secondary); font-size: 1.1rem;">{message}</div>
        </div>
        """
        st.markdown(loading_html, unsafe_allow_html=True)

    @staticmethod
    def create_success_message(message: str, icon: str = "✅"):
        """Create success message"""
        success_html = f"""
        <div style="background: var(--success-color); color: white; padding: 1rem; border-radius: var(--border-radius-md); margin: 1rem 0; display: flex; align-items: center;">
            <div style="font-size: 1.5rem; margin-right: 0.75rem;">{icon}</div>
            <div>{message}</div>
        </div>
        """
        st.markdown(success_html, unsafe_allow_html=True)

    @staticmethod
    def create_error_message(message: str, icon: str = "❌"):
        """Create error message"""
        error_html = f"""
        <div style="background: var(--error-color); color: white; padding: 1rem; border-radius: var(--border-radius-md); margin: 1rem 0; display: flex; align-items: center;">
            <div style="font-size: 1.5rem; margin-right: 0.75rem;">{icon}</div>
            <div>{message}</div>
        </div>
        """
        st.markdown(error_html, unsafe_allow_html=True)

    @staticmethod
    def create_warning_message(message: str, icon: str = "⚠️"):
        """Create warning message"""
        warning_html = f"""
        <div style="background: var(--warning-color); color: black; padding: 1rem; border-radius: var(--border-radius-md); margin: 1rem 0; display: flex; align-items: center;">
            <div style="font-size: 1.5rem; margin-right: 0.75rem;">{icon}</div>
            <div>{message}</div>
        </div>
        """
        st.markdown(warning_html, unsafe_allow_html=True)


class ChartComponents:
    """Chart components for data visualization"""

    @staticmethod
    def create_accuracy_chart(accuracy_data: List[float], val_accuracy_data: List[float] = None):
        """Create accuracy training chart"""
        fig = go.Figure()

        epochs = list(range(1, len(accuracy_data) + 1))

        fig.add_trace(go.Scatter(
            x=epochs,
            y=accuracy_data,
            mode='lines+markers',
            name='Training Accuracy',
            line=dict(color='#6366f1', width=3),
            marker=dict(size=6)
        ))

        if val_accuracy_data:
            fig.add_trace(go.Scatter(
                x=epochs,
                y=val_accuracy_data,
                mode='lines+markers',
                name='Validation Accuracy',
                line=dict(color='#ef4444', width=3),
                marker=dict(size=6)
            ))

        fig.update_layout(
            title='Model Training Accuracy',
            xaxis_title='Epoch',
            yaxis_title='Accuracy',
            template='plotly_white',
            height=400
        )

        return fig

    @staticmethod
    def create_confusion_matrix(cm_data: List[List[int]], labels: List[str] = None):
        """Create confusion matrix heatmap"""
        if labels is None:
            labels = ['Real', 'Fake']

        fig = px.imshow(
            cm_data,
            text_auto=True,
            labels=dict(x="Predicted", y="True", color="Count"),
            x=labels,
            y=labels,
            color_continuous_scale='Blues'
        )

        fig.update_layout(
            title='Confusion Matrix',
            height=400
        )

        return fig

    @staticmethod
    def create_task_timeline(tasks_data: List[Dict]):
        """Create task timeline chart"""
        df = pd.DataFrame(tasks_data)

        if 'start_time' in df.columns:
            df['start_time'] = pd.to_datetime(df['start_time'])

        fig = px.timeline(
            df,
            x_start='start_time',
            x_end='end_time' if 'end_time' in df.columns else None,
            y='task_type',
            color='status',
            title='Task Execution Timeline'
        )

        fig.update_layout(
            height=400
        )

        return fig

    @staticmethod
    def create_file_type_distribution(file_types: Dict[str, int]):
        """Create file type distribution pie chart"""
        labels = list(file_types.keys())
        values = list(file_types.values())

        fig = go.Figure(data=[go.Pie(
            labels=labels,
            values=values,
            marker_colors=px.colors.qualitative.Set3
        )])

        fig.update_layout(
            title='File Type Distribution',
            height=400
        )

        return fig

    @staticmethod
    def create_performance_metrics_chart(metrics_data: Dict):
        """Create performance metrics bar chart"""
        metrics = list(metrics_data.keys())
        values = list(metrics_data.values())

        fig = go.Figure(data=[go.Bar(
            x=metrics,
            y=values,
            marker_color='#6366f1'
        )])

        fig.update_layout(
            title='Performance Metrics',
            xaxis_title='Metric',
            yaxis_title='Value',
            height=400
        )

        return fig


class AnimationComponents:
    """Animation components for enhanced UX"""

    @staticmethod
    def create_typing_effect(text: str, speed: float = 0.05):
        """Create typing effect animation"""
        placeholder = st.empty()

        displayed_text = ""
        for char in text:
            displayed_text += char
            placeholder.markdown(f"```\n{displayed_text}▊\n```")
            time.sleep(speed)

        placeholder.markdown(f"```\n{text}\n```")

    @staticmethod
    def create_progressive_loading(items: List[str], delay: float = 0.5):
        """Create progressive loading animation"""
        placeholder = st.empty()

        for i, item in enumerate(items):
            progress = (i + 1) / len(items) * 100

            html = f"""
            <div style="margin: 1rem 0;">
                <div style="display: flex; align-items: center; margin-bottom: 0.5rem;">
                    <div style="flex: 1; background: #e2e8f0; height: 8px; border-radius: 4px; margin-right: 1rem;">
                        <div style="width: {progress}%; height: 100%; background: linear-gradient(90deg, #6366f1 0%, #8b5cf6 100%); border-radius: 4px; transition: width 0.3s ease;"></div>
                    </div>
                    <span style="font-size: 0.875rem; color: #64748b;">{int(progress)}%</span>
                </div>
                <div style="color: #1e293b; font-weight: 500;">{item}</div>
            </div>
            """

            placeholder.markdown(html, unsafe_allow_html=True)
            time.sleep(delay)

    @staticmethod
    def create_success_celebration(message: str = "Success!"):
        """Create success celebration animation"""
        celebration_html = f"""
        <div style="text-align: center; padding: 2rem;">
            <div style="font-size: 4rem; animation: bounce 1s infinite;">🎉</div>
            <h2 style="color: #10b981; margin: 1rem 0;">{message}</h2>
            <div style="font-size: 2rem;">✨ ✨ ✨</div>
        </div>
        <style>
        @keyframes bounce {{
            0%, 20%, 50%, 80%, 100% {{ transform: translateY(0); }}
            40% {{ transform: translateY(-10px); }}
            60% {{ transform: translateY(-5px); }}
        }}
        </style>
        """
        st.markdown(celebration_html, unsafe_allow_html=True)
        time.sleep(2)  # Show celebration for 2 seconds


class NotificationComponents:
    """Notification components for user feedback"""

    @staticmethod
    def show_toast(message: str, type: str = "info", duration: int = 3000):
        """Show toast notification"""
        toast_types = {
            "success": {"icon": "✅", "color": "#10b981"},
            "error": {"icon": "❌", "color": "#ef4444"},
            "warning": {"icon": "⚠️", "color": "#f59e0b"},
            "info": {"icon": "ℹ️", "color": "#6366f1"}
        }

        toast_config = toast_types.get(type, toast_types["info"])

        toast_html = f"""
        <div id="toast" style="
            position: fixed;
            top: 20px;
            right: 20px;
            background: {toast_config['color']};
            color: white;
            padding: 1rem 1.5rem;
            border-radius: 8px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.3);
            z-index: 1000;
            display: flex;
            align-items: center;
            animation: slideIn 0.3s ease;
        ">
            <div style="font-size: 1.5rem; margin-right: 0.75rem;">{toast_config['icon']}</div>
            <div>{message}</div>
        </div>
        <style>
        @keyframes slideIn {{
            from {{ transform: translateX(100%); opacity: 0; }}
            to {{ transform: translateX(0); opacity: 1; }}
        }}
        @keyframes slideOut {{
            from {{ transform: translateX(0); opacity: 1; }}
            to {{ transform: translateX(100%); opacity: 0; }}
        }}
        </style>
        <script>
        setTimeout(function() {{
            var toast = document.getElementById('toast');
            if (toast) {{
                toast.style.animation = 'slideOut 0.3s ease';
                setTimeout(function() {{ toast.remove(); }}, 300);
            }}
        }}, {duration});
        </script>
        """

        st.markdown(toast_html, unsafe_allow_html=True)

    @staticmethod
    def show_progress_notification(current: int, total: int, message: str = "Processing..."):
        """Show progress notification"""
        progress = int((current / total) * 100) if total > 0 else 0

        progress_html = f"""
        <div style="
            position: fixed;
            bottom: 20px;
            right: 20px;
            background: #1e293b;
            color: white;
            padding: 1rem 1.5rem;
            border-radius: 8px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.3);
            z-index: 1000;
            min-width: 300px;
        ">
            <div style="display: flex; align-items: center; margin-bottom: 0.5rem;">
                <div style="font-size: 1.2rem; margin-right: 0.5rem;">⏳</div>
                <div style="font-weight: 500;">{message}</div>
            </div>
            <div style="background: #334155; height: 6px; border-radius: 3px; overflow: hidden;">
                <div style="width: {progress}%; height: 100%; background: linear-gradient(90deg, #6366f1 0%, #8b5cf6 100%); transition: width 0.3s ease;"></div>
            </div>
            <div style="text-align: right; font-size: 0.8rem; color: #94a3b8; margin-top: 0.25rem;">
                {current} / {total} ({progress}%)
            </div>
        </div>
        """

        # Use a placeholder to update the notification
        placeholder = st.empty()
        placeholder.markdown(progress_html, unsafe_allow_html=True)

        return placeholder