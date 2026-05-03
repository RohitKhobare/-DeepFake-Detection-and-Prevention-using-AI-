"""
Task History Manager
Tracks and manages all analysis tasks performed on the project
"""

import json
import sqlite3
from pathlib import Path
from typing import List, Dict, Optional, Any
from datetime import datetime, timedelta
import threading
import logging
from collections import defaultdict
import pandas as pd

logger = logging.getLogger(__name__)


class TaskHistoryManager:
    """Manages task history and analytics for the deepfake detection system"""

    def __init__(self, db_path: str = "task_history.db"):
        self.db_path = Path(db_path)
        self.db_lock = threading.Lock()
        self._init_database()

    def _init_database(self):
        """Initialize the SQLite database"""
        with self.db_lock:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            # Create tasks table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS tasks (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    task_id TEXT UNIQUE NOT NULL,
                    task_type TEXT NOT NULL,
                    file_path TEXT,
                    file_name TEXT,
                    file_size INTEGER,
                    content_type TEXT,
                    status TEXT DEFAULT 'running',
                    start_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    end_time TIMESTAMP,
                    duration REAL,
                    result TEXT,
                    confidence_score REAL,
                    classification TEXT,
                    error_message TEXT,
                    metadata TEXT,
                    created_by TEXT DEFAULT 'system'
                )
            ''')

            # Create task_details table for detailed analysis results
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS task_details (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    task_id TEXT NOT NULL,
                    detail_type TEXT NOT NULL,
                    detail_key TEXT NOT NULL,
                    detail_value TEXT,
                    FOREIGN KEY (task_id) REFERENCES tasks (task_id)
                )
            ''')

            # Create analytics table for aggregated statistics
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS analytics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    date DATE NOT NULL,
                    metric_type TEXT NOT NULL,
                    metric_name TEXT NOT NULL,
                    metric_value REAL,
                    UNIQUE(date, metric_type, metric_name)
                )
            ''')

            # Create indexes for better performance
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_tasks_type ON tasks(task_type)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_tasks_status ON tasks(status)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_tasks_start_time ON tasks(start_time)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_task_details_task_id ON task_details(task_id)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_analytics_date ON analytics(date)')

            conn.commit()
            conn.close()

    def create_task(self, task_type: str, file_path: Optional[str] = None,
                   metadata: Optional[Dict] = None) -> str:
        """Create a new task and return its ID"""
        task_id = f"{task_type}_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{hash(file_path or 'no_file') % 10000:04d}"

        with self.db_lock:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            file_name = Path(file_path).name if file_path else None
            file_size = Path(file_path).stat().st_size if file_path and Path(file_path).exists() else None

            cursor.execute('''
                INSERT INTO tasks (task_id, task_type, file_path, file_name, file_size, metadata)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (task_id, task_type, file_path, file_name, file_size, json.dumps(metadata or {})))

            conn.commit()
            conn.close()

        logger.info(f"Created task: {task_id}")
        return task_id

    def update_task_status(self, task_id: str, status: str,
                          result: Optional[Dict] = None,
                          error_message: Optional[str] = None):
        """Update task status and results"""
        with self.db_lock:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            update_data = {'status': status}

            if status in ['completed', 'failed']:
                update_data['end_time'] = datetime.now().isoformat()

                # Calculate duration
                cursor.execute('SELECT start_time FROM tasks WHERE task_id = ?', (task_id,))
                start_time_row = cursor.fetchone()
                if start_time_row:
                    start_time = datetime.fromisoformat(start_time_row[0])
                    duration = (datetime.now() - start_time).total_seconds()
                    update_data['duration'] = duration

            if result:
                update_data['result'] = json.dumps(result)
                if 'confidence_score' in result:
                    update_data['confidence_score'] = result['confidence_score']
                if 'classification' in result:
                    update_data['classification'] = result['classification']

            if error_message:
                update_data['error_message'] = error_message

            # Build dynamic update query
            set_clause = ', '.join([f"{k} = ?" for k in update_data.keys()])
            values = list(update_data.values()) + [task_id]

            cursor.execute(f'''
                UPDATE tasks SET {set_clause} WHERE task_id = ?
            ''', values)

            conn.commit()
            conn.close()

        logger.info(f"Updated task {task_id} status to {status}")

    def add_task_details(self, task_id: str, details: Dict[str, Any]):
        """Add detailed analysis results for a task"""
        with self.db_lock:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            for detail_type, detail_data in details.items():
                if isinstance(detail_data, dict):
                    for key, value in detail_data.items():
                        cursor.execute('''
                            INSERT INTO task_details (task_id, detail_type, detail_key, detail_value)
                            VALUES (?, ?, ?, ?)
                        ''', (task_id, detail_type, key, json.dumps(value) if not isinstance(value, (str, int, float, bool)) else str(value)))
                else:
                    cursor.execute('''
                        INSERT INTO task_details (task_id, detail_type, detail_key, detail_value)
                        VALUES (?, ?, ?, ?)
                    ''', (task_id, detail_type, 'value', json.dumps(detail_data) if not isinstance(detail_data, (str, int, float, bool)) else str(detail_data)))

            conn.commit()
            conn.close()

    def get_task(self, task_id: str) -> Optional[Dict]:
        """Get task information by ID"""
        with self.db_lock:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute('SELECT * FROM tasks WHERE task_id = ?', (task_id,))
            row = cursor.fetchone()

            if not row:
                conn.close()
                return None

            # Get column names
            columns = [desc[0] for desc in cursor.description]

            task = dict(zip(columns, row))

            # Parse JSON fields
            for field in ['result', 'metadata']:
                if task[field]:
                    try:
                        task[field] = json.loads(task[field])
                    except:
                        pass

            # Get task details
            cursor.execute('SELECT detail_type, detail_key, detail_value FROM task_details WHERE task_id = ?', (task_id,))
            details_rows = cursor.fetchall()

            task['details'] = {}
            for detail_type, detail_key, detail_value in details_rows:
                if detail_type not in task['details']:
                    task['details'][detail_type] = {}
                try:
                    task['details'][detail_type][detail_key] = json.loads(detail_value)
                except:
                    task['details'][detail_type][detail_key] = detail_value

            conn.close()
            return task

    def get_tasks(self, filters: Optional[Dict] = None, limit: int = 100, offset: int = 0) -> List[Dict]:
        """Get tasks with optional filtering"""
        with self.db_lock:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            query = "SELECT * FROM tasks WHERE 1=1"
            params = []

            if filters:
                if 'task_type' in filters:
                    query += " AND task_type = ?"
                    params.append(filters['task_type'])

                if 'status' in filters:
                    query += " AND status = ?"
                    params.append(filters['status'])

                if 'content_type' in filters:
                    query += " AND content_type = ?"
                    params.append(filters['content_type'])

                if 'date_from' in filters:
                    query += " AND start_time >= ?"
                    params.append(filters['date_from'])

                if 'date_to' in filters:
                    query += " AND start_time <= ?"
                    params.append(filters['date_to'])

                if 'classification' in filters:
                    query += " AND classification = ?"
                    params.append(filters['classification'])

            query += " ORDER BY start_time DESC LIMIT ? OFFSET ?"
            params.extend([limit, offset])

            cursor.execute(query, params)
            rows = cursor.fetchall()

            # Get column names
            columns = [desc[0] for desc in cursor.description]

            tasks = []
            for row in rows:
                task = dict(zip(columns, row))

                # Parse JSON fields
                for field in ['result', 'metadata']:
                    if task[field]:
                        try:
                            task[field] = json.loads(task[field])
                        except:
                            pass

                tasks.append(task)

            conn.close()
            return tasks

    def get_task_statistics(self, date_from: Optional[str] = None, date_to: Optional[str] = None) -> Dict:
        """Get comprehensive task statistics"""
        with self.db_lock:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            # Base query conditions
            conditions = []
            params = []

            if date_from:
                conditions.append("start_time >= ?")
                params.append(date_from)
            if date_to:
                conditions.append("start_time <= ?")
                params.append(date_to)

            where_clause = " AND ".join(conditions) if conditions else "1=1"

            # Overall statistics
            cursor.execute(f'''
                SELECT
                    COUNT(*) as total_tasks,
                    COUNT(CASE WHEN status = 'completed' THEN 1 END) as completed_tasks,
                    COUNT(CASE WHEN status = 'failed' THEN 1 END) as failed_tasks,
                    COUNT(CASE WHEN status = 'running' THEN 1 END) as running_tasks,
                    AVG(duration) as avg_duration,
                    SUM(duration) as total_duration,
                    AVG(confidence_score) as avg_confidence
                FROM tasks
                WHERE {where_clause}
            ''', params)

            overall_stats = dict(zip([desc[0] for desc in cursor.description], cursor.fetchone()))

            # Task type breakdown
            cursor.execute(f'''
                SELECT task_type, COUNT(*) as count,
                       AVG(duration) as avg_duration,
                       AVG(confidence_score) as avg_confidence
                FROM tasks
                WHERE {where_clause}
                GROUP BY task_type
                ORDER BY count DESC
            ''', params)

            task_types = [dict(zip([desc[0] for desc in cursor.description], row)) for row in cursor.fetchall()]

            # Content type breakdown
            cursor.execute(f'''
                SELECT content_type, COUNT(*) as count,
                       AVG(duration) as avg_duration,
                       AVG(confidence_score) as avg_confidence
                FROM tasks
                WHERE content_type IS NOT NULL AND {where_clause}
                GROUP BY content_type
                ORDER BY count DESC
            ''', params)

            content_types = [dict(zip([desc[0] for desc in cursor.description], row)) for row in cursor.fetchall()]

            # Classification breakdown
            cursor.execute(f'''
                SELECT classification, COUNT(*) as count
                FROM tasks
                WHERE classification IS NOT NULL AND {where_clause}
                GROUP BY classification
                ORDER BY count DESC
            ''', params)

            classifications = [dict(zip([desc[0] for desc in cursor.description], row)) for row in cursor.fetchall()]

            # Daily statistics (last 30 days)
            cursor.execute(f'''
                SELECT DATE(start_time) as date,
                       COUNT(*) as daily_count,
                       AVG(duration) as avg_duration,
                       COUNT(CASE WHEN status = 'completed' THEN 1 END) as completed_count
                FROM tasks
                WHERE start_time >= date('now', '-30 days') AND {where_clause}
                GROUP BY DATE(start_time)
                ORDER BY date DESC
            ''', params)

            daily_stats = [dict(zip([desc[0] for desc in cursor.description], row)) for row in cursor.fetchall()]

            # File size analysis
            cursor.execute(f'''
                SELECT
                    AVG(file_size) as avg_file_size,
                    MAX(file_size) as max_file_size,
                    MIN(file_size) as min_file_size,
                    SUM(file_size) as total_file_size
                FROM tasks
                WHERE file_size IS NOT NULL AND {where_clause}
            ''', params)

            file_stats = dict(zip([desc[0] for desc in cursor.description], cursor.fetchone()))

            conn.close()

            return {
                'overall': overall_stats,
                'by_task_type': task_types,
                'by_content_type': content_types,
                'by_classification': classifications,
                'daily_stats': daily_stats,
                'file_stats': file_stats,
                'date_range': {'from': date_from, 'to': date_to}
            }

    def get_recent_activity(self, limit: int = 10) -> List[Dict]:
        """Get recent task activity"""
        return self.get_tasks(limit=limit)

    def search_tasks(self, query: str, search_fields: List[str] = None) -> List[Dict]:
        """Search tasks by query"""
        if search_fields is None:
            search_fields = ['task_id', 'task_type', 'file_name', 'file_path', 'result', 'error_message']

        with self.db_lock:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            # Build search conditions
            conditions = []
            params = []

            for field in search_fields:
                if field in ['result', 'error_message']:
                    # JSON fields need special handling
                    conditions.append(f"{field} LIKE ?")
                    params.append(f'%{query}%')
                else:
                    conditions.append(f"{field} LIKE ?")
                    params.append(f'%{query}%')

            where_clause = " OR ".join(conditions)

            cursor.execute(f'''
                SELECT * FROM tasks
                WHERE {where_clause}
                ORDER BY start_time DESC
                LIMIT 100
            ''', params * len(search_fields))

            rows = cursor.fetchall()
            columns = [desc[0] for desc in cursor.description]

            tasks = []
            for row in rows:
                task = dict(zip(columns, row))

                # Parse JSON fields
                for field in ['result', 'metadata']:
                    if task[field]:
                        try:
                            task[field] = json.loads(task[field])
                        except:
                            pass

                tasks.append(task)

            conn.close()
            return tasks

    def export_tasks_to_csv(self, file_path: str, filters: Optional[Dict] = None) -> bool:
        """Export tasks to CSV file"""
        try:
            tasks = self.get_tasks(filters=filters, limit=10000)  # Export up to 10k tasks

            if not tasks:
                return False

            # Convert to DataFrame
            df = pd.DataFrame(tasks)

            # Flatten nested fields
            if 'result' in df.columns:
                df['result'] = df['result'].apply(lambda x: json.dumps(x) if isinstance(x, dict) else str(x))
            if 'metadata' in df.columns:
                df['metadata'] = df['metadata'].apply(lambda x: json.dumps(x) if isinstance(x, dict) else str(x))

            # Export to CSV
            df.to_csv(file_path, index=False)
            return True

        except Exception as e:
            logger.error(f"Export to CSV failed: {e}")
            return False

    def cleanup_old_tasks(self, days_to_keep: int = 90):
        """Clean up old completed tasks"""
        with self.db_lock:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cutoff_date = (datetime.now() - timedelta(days=days_to_keep)).isoformat()

            # Delete old completed tasks
            cursor.execute('''
                DELETE FROM task_details
                WHERE task_id IN (
                    SELECT task_id FROM tasks
                    WHERE status IN ('completed', 'failed')
                    AND start_time < ?
                )
            ''', (cutoff_date,))

            cursor.execute('''
                DELETE FROM tasks
                WHERE status IN ('completed', 'failed')
                AND start_time < ?
            ''', (cutoff_date,))

            deleted_count = cursor.rowcount
            conn.commit()
            conn.close()

            logger.info(f"Cleaned up {deleted_count} old tasks")
            return deleted_count

    def update_analytics(self):
        """Update analytics data"""
        today = datetime.now().date().isoformat()

        with self.db_lock:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            # Daily task counts
            cursor.execute('''
                SELECT COUNT(*) FROM tasks
                WHERE DATE(start_time) = ?
            ''', (today,))

            daily_count = cursor.fetchone()[0]

            # Update analytics
            cursor.execute('''
                INSERT OR REPLACE INTO analytics (date, metric_type, metric_name, metric_value)
                VALUES (?, 'tasks', 'daily_count', ?)
            ''', (today, daily_count))

            # Task type distribution
            cursor.execute('''
                SELECT task_type, COUNT(*) FROM tasks
                WHERE DATE(start_time) = ?
                GROUP BY task_type
            ''', (today,))

            for task_type, count in cursor.fetchall():
                cursor.execute('''
                    INSERT OR REPLACE INTO analytics (date, metric_type, metric_name, metric_value)
                    VALUES (?, 'task_types', ?, ?)
                ''', (today, task_type, count))

            conn.commit()
            conn.close()

    def get_analytics_summary(self, days: int = 30) -> Dict:
        """Get analytics summary for the specified number of days"""
        with self.db_lock:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            start_date = (datetime.now() - timedelta(days=days)).date().isoformat()

            # Get daily metrics
            cursor.execute('''
                SELECT date, metric_name, metric_value
                FROM analytics
                WHERE date >= ? AND metric_type = 'tasks'
                ORDER BY date
            ''', (start_date,))

            daily_metrics = {}
            for row in cursor.fetchall():
                date, metric_name, value = row
                if date not in daily_metrics:
                    daily_metrics[date] = {}
                daily_metrics[date][metric_name] = value

            # Get task type trends
            cursor.execute('''
                SELECT date, metric_name, SUM(metric_value) as total
                FROM analytics
                WHERE date >= ? AND metric_type = 'task_types'
                GROUP BY date, metric_name
                ORDER BY date
            ''', (start_date,))

            task_type_trends = defaultdict(dict)
            for row in cursor.fetchall():
                date, task_type, total = row
                task_type_trends[date][task_type] = total

            conn.close()

            return {
                'period_days': days,
                'daily_metrics': dict(daily_metrics),
                'task_type_trends': dict(task_type_trends),
                'total_tasks': sum([m.get('daily_count', 0) for m in daily_metrics.values()])
            }

    def get_performance_metrics(self) -> Dict:
        """Get system performance metrics"""
        with self.db_lock:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            # Average processing times by task type
            cursor.execute('''
                SELECT task_type,
                       AVG(duration) as avg_duration,
                       MIN(duration) as min_duration,
                       MAX(duration) as max_duration,
                       COUNT(*) as sample_size
                FROM tasks
                WHERE duration IS NOT NULL AND status = 'completed'
                GROUP BY task_type
                ORDER BY avg_duration DESC
            ''')

            performance_by_type = [dict(zip([desc[0] for desc in cursor.description], row)) for row in cursor.fetchall()]

            # Success rates
            cursor.execute('''
                SELECT task_type,
                       COUNT(CASE WHEN status = 'completed' THEN 1 END) * 100.0 / COUNT(*) as success_rate,
                       COUNT(*) as total_tasks
                FROM tasks
                GROUP BY task_type
                ORDER BY success_rate DESC
            ''')

            success_rates = [dict(zip([desc[0] for desc in cursor.description], row)) for row in cursor.fetchall()]

            # File size vs processing time correlation
            cursor.execute('''
                SELECT file_size, duration
                FROM tasks
                WHERE file_size IS NOT NULL AND duration IS NOT NULL AND status = 'completed'
                ORDER BY file_size
            ''')

            size_time_data = cursor.fetchall()

            conn.close()

            return {
                'performance_by_type': performance_by_type,
                'success_rates': success_rates,
                'size_time_correlation': size_time_data,
                'total_completed_tasks': sum([p['sample_size'] for p in performance_by_type])
            }