"""
Batch Processor for Multiple File Analysis
Handles batch processing of multiple files with progress tracking and parallel execution
"""

import os
import json
import time
from pathlib import Path
from typing import List, Dict, Callable, Optional, Any, Tuple
from concurrent.futures import ThreadPoolExecutor, as_completed
import logging
from queue import Queue
import threading
from datetime import datetime
import pandas as pd

logger = logging.getLogger(__name__)


class BatchProcessor:
    """Handles batch processing of multiple files for deepfake analysis"""

    def __init__(self, max_workers: int = 4, progress_callback: Optional[Callable] = None):
        self.max_workers = max_workers
        self.progress_callback = progress_callback
        self.is_processing = False
        self.cancel_requested = False
        self.results = {}
        self.errors = []
        self.processing_stats = {
            'total_files': 0,
            'processed_files': 0,
            'successful_analyses': 0,
            'failed_analyses': 0,
            'start_time': None,
            'end_time': None,
            'total_processing_time': 0
        }

    def process_batch(self, file_paths: List[str], analysis_function: Callable,
                     config: Optional[Dict] = None, batch_name: str = "batch_analysis") -> Dict[str, Any]:
        """Process a batch of files using the provided analysis function"""
        if not file_paths:
            return {'error': 'No files provided for batch processing'}

        self.is_processing = True
        self.cancel_requested = False
        self.results = {}
        self.errors = []
        self.processing_stats = {
            'total_files': len(file_paths),
            'processed_files': 0,
            'successful_analyses': 0,
            'failed_analyses': 0,
            'start_time': datetime.now(),
            'end_time': None,
            'total_processing_time': 0,
            'batch_name': batch_name
        }

        logger.info(f"Starting batch processing of {len(file_paths)} files")

        try:
            # Validate file paths
            valid_paths = self._validate_file_paths(file_paths)

            if not valid_paths:
                return {'error': 'No valid files found for processing'}

            # Process files in parallel
            with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
                # Submit all tasks
                future_to_path = {
                    executor.submit(self._process_single_file, path, analysis_function, config): path
                    for path in valid_paths
                }

                # Process completed tasks
                for future in as_completed(future_to_path):
                    if self.cancel_requested:
                        break

                    file_path = future_to_path[future]
                    try:
                        result = future.result()
                        self.results[file_path] = result
                        self.processing_stats['processed_files'] += 1

                        if result.get('success', False):
                            self.processing_stats['successful_analyses'] += 1
                        else:
                            self.processing_stats['failed_analyses'] += 1
                            self.errors.append({
                                'file_path': file_path,
                                'error': result.get('error', 'Unknown error')
                            })

                        # Update progress
                        self._update_progress(file_path, result)

                    except Exception as e:
                        logger.error(f"Error processing {file_path}: {e}")
                        self.results[file_path] = {'success': False, 'error': str(e)}
                        self.processing_stats['failed_analyses'] += 1
                        self.errors.append({'file_path': file_path, 'error': str(e)})
                        self._update_progress(file_path, {'success': False, 'error': str(e)})

            # Calculate final statistics
            self.processing_stats['end_time'] = datetime.now()
            self.processing_stats['total_processing_time'] = (
                self.processing_stats['end_time'] - self.processing_stats['start_time']
            ).total_seconds()

            # Generate summary
            summary = self._generate_batch_summary()

            logger.info(f"Batch processing completed. Processed {self.processing_stats['processed_files']} files")

            return {
                'success': True,
                'batch_name': batch_name,
                'statistics': self.processing_stats,
                'results': self.results,
                'errors': self.errors,
                'summary': summary
            }

        except Exception as e:
            logger.error(f"Batch processing failed: {e}")
            return {
                'success': False,
                'error': str(e),
                'statistics': self.processing_stats,
                'results': self.results,
                'errors': self.errors
            }
        finally:
            self.is_processing = False

    def _process_single_file(self, file_path: str, analysis_function: Callable,
                           config: Optional[Dict] = None) -> Dict[str, Any]:
        """Process a single file"""
        try:
            start_time = time.time()

            # Call the analysis function
            if config:
                result = analysis_function(file_path, **config)
            else:
                result = analysis_function(file_path)

            processing_time = time.time() - start_time

            # Ensure result has success flag
            if not isinstance(result, dict):
                result = {'success': True, 'result': result}

            if 'success' not in result:
                result['success'] = 'error' not in result

            # Add processing metadata
            result['processing_time'] = processing_time
            result['processed_at'] = datetime.now().isoformat()

            return result

        except Exception as e:
            logger.error(f"Error in single file processing for {file_path}: {e}")
            return {
                'success': False,
                'error': str(e),
                'processing_time': time.time() - start_time if 'start_time' in locals() else 0,
                'processed_at': datetime.now().isoformat()
            }

    def _validate_file_paths(self, file_paths: List[str]) -> List[str]:
        """Validate and filter file paths"""
        valid_paths = []

        for path in file_paths:
            path_obj = Path(path)

            if not path_obj.exists():
                self.errors.append({'file_path': path, 'error': 'File does not exist'})
                continue

            if not path_obj.is_file():
                self.errors.append({'file_path': path, 'error': 'Path is not a file'})
                continue

            # Check file size (skip files larger than 2GB for safety)
            file_size = path_obj.stat().st_size
            if file_size > 2 * 1024 * 1024 * 1024:  # 2GB
                self.errors.append({'file_path': path, 'error': 'File too large (>2GB)'})
                continue

            if file_size == 0:
                self.errors.append({'file_path': path, 'error': 'File is empty'})
                continue

            valid_paths.append(path)

        return valid_paths

    def _update_progress(self, file_path: str, result: Dict):
        """Update progress callback"""
        if self.progress_callback:
            try:
                progress_info = {
                    'file_path': file_path,
                    'result': result,
                    'current': self.processing_stats['processed_files'],
                    'total': self.processing_stats['total_files'],
                    'percentage': (self.processing_stats['processed_files'] / self.processing_stats['total_files']) * 100,
                    'successful': self.processing_stats['successful_analyses'],
                    'failed': self.processing_stats['failed_analyses'],
                    'elapsed_time': (datetime.now() - self.processing_stats['start_time']).total_seconds()
                }
                self.progress_callback(progress_info)
            except Exception as e:
                logger.error(f"Progress callback error: {e}")

    def _generate_batch_summary(self) -> Dict[str, Any]:
        """Generate comprehensive batch processing summary"""
        try:
            # Calculate success rate
            success_rate = (
                self.processing_stats['successful_analyses'] / self.processing_stats['processed_files'] * 100
                if self.processing_stats['processed_files'] > 0 else 0
            )

            # Calculate average processing time
            total_time = self.processing_stats['total_processing_time']
            avg_time_per_file = total_time / self.processing_stats['processed_files'] if self.processing_stats['processed_files'] > 0 else 0

            # Analyze results by file type
            file_type_stats = self._analyze_results_by_file_type()

            # Analyze results by classification
            classification_stats = self._analyze_results_by_classification()

            # Performance analysis
            performance_stats = self._analyze_performance()

            summary = {
                'batch_overview': {
                    'total_files': self.processing_stats['total_files'],
                    'processed_files': self.processing_stats['processed_files'],
                    'successful_analyses': self.processing_stats['successful_analyses'],
                    'failed_analyses': self.processing_stats['failed_analyses'],
                    'success_rate': round(success_rate, 2),
                    'total_processing_time': round(total_time, 2),
                    'average_time_per_file': round(avg_time_per_file, 2),
                    'processing_speed': round(self.processing_stats['processed_files'] / total_time, 2) if total_time > 0 else 0
                },
                'file_type_breakdown': file_type_stats,
                'classification_breakdown': classification_stats,
                'performance_analysis': performance_stats,
                'error_summary': self._summarize_errors(),
                'recommendations': self._generate_recommendations(success_rate, performance_stats)
            }

            return summary

        except Exception as e:
            logger.error(f"Error generating batch summary: {e}")
            return {'error': f'Summary generation failed: {e}'}

    def _analyze_results_by_file_type(self) -> Dict[str, Any]:
        """Analyze results grouped by file type"""
        file_types = {}

        for file_path, result in self.results.items():
            file_ext = Path(file_path).suffix.lower()

            if file_ext not in file_types:
                file_types[file_ext] = {
                    'count': 0,
                    'successful': 0,
                    'failed': 0,
                    'avg_processing_time': 0,
                    'total_processing_time': 0
                }

            file_types[file_ext]['count'] += 1

            if result.get('success', False):
                file_types[file_ext]['successful'] += 1
            else:
                file_types[file_ext]['failed'] += 1

            processing_time = result.get('processing_time', 0)
            file_types[file_ext]['total_processing_time'] += processing_time

        # Calculate averages
        for ext, stats in file_types.items():
            if stats['count'] > 0:
                stats['avg_processing_time'] = round(stats['total_processing_time'] / stats['count'], 2)
                stats['success_rate'] = round((stats['successful'] / stats['count']) * 100, 2)

        return file_types

    def _analyze_results_by_classification(self) -> Dict[str, Any]:
        """Analyze results by deepfake classification"""
        classifications = {}

        for file_path, result in self.results.items():
            if not result.get('success', False):
                continue

            # Extract classification from result
            classification = 'Unknown'
            if 'result' in result and isinstance(result['result'], dict):
                classification = result['result'].get('classification', result['result'].get('assessment', 'Unknown'))
            elif 'classification' in result:
                classification = result['classification']

            if classification not in classifications:
                classifications[classification] = {
                    'count': 0,
                    'files': []
                }

            classifications[classification]['count'] += 1
            classifications[classification]['files'].append({
                'path': file_path,
                'name': Path(file_path).name,
                'processing_time': result.get('processing_time', 0)
            })

        return classifications

    def _analyze_performance(self) -> Dict[str, Any]:
        """Analyze processing performance"""
        if not self.results:
            return {'error': 'No results to analyze'}

        processing_times = [r.get('processing_time', 0) for r in self.results.values() if r.get('success', False)]

        if not processing_times:
            return {'error': 'No successful processing times to analyze'}

        return {
            'min_processing_time': round(min(processing_times), 2),
            'max_processing_time': round(max(processing_times), 2),
            'avg_processing_time': round(sum(processing_times) / len(processing_times), 2),
            'median_processing_time': round(sorted(processing_times)[len(processing_times) // 2], 2),
            'processing_time_std': round(pd.Series(processing_times).std(), 2) if len(processing_times) > 1 else 0,
            'fastest_file': self._find_extreme_file('min'),
            'slowest_file': self._find_extreme_file('max')
        }

    def _find_extreme_file(self, mode: str) -> Dict[str, Any]:
        """Find file with extreme processing time"""
        if not self.results:
            return {}

        if mode == 'min':
            extreme_result = min(
                [(r.get('processing_time', float('inf')), path, r)
                 for path, r in self.results.items() if r.get('success', False)],
                key=lambda x: x[0]
            )
        else:  # max
            extreme_result = max(
                [(r.get('processing_time', 0), path, r)
                 for path, r in self.results.items() if r.get('success', False)],
                key=lambda x: x[0]
            )

        time_val, path, result = extreme_result
        return {
            'file_path': path,
            'file_name': Path(path).name,
            'processing_time': round(time_val, 2)
        }

    def _summarize_errors(self) -> Dict[str, Any]:
        """Summarize errors that occurred during processing"""
        if not self.errors:
            return {'total_errors': 0, 'error_types': {}}

        error_types = {}
        for error in self.errors:
            error_type = error.get('error', 'Unknown error')
            # Group similar errors
            if 'does not exist' in error_type.lower():
                error_type = 'File not found'
            elif 'too large' in error_type.lower():
                error_type = 'File too large'
            elif 'empty' in error_type.lower():
                error_type = 'Empty file'
            elif 'not a file' in error_type.lower():
                error_type = 'Invalid file path'

            if error_type not in error_types:
                error_types[error_type] = 0
            error_types[error_type] += 1

        return {
            'total_errors': len(self.errors),
            'error_types': error_types,
            'error_rate': round((len(self.errors) / self.processing_stats['total_files']) * 100, 2)
        }

    def _generate_recommendations(self, success_rate: float, performance_stats: Dict) -> List[str]:
        """Generate recommendations based on batch processing results"""
        recommendations = []

        if success_rate < 80:
            recommendations.append("Consider reviewing failed files for common issues (file format, corruption, size)")
            if self.errors:
                error_summary = self._summarize_errors()
                top_error = max(error_summary['error_types'].items(), key=lambda x: x[1])
                recommendations.append(f"Address most common error: {top_error[0]} ({top_error[1]} occurrences)")

        if performance_stats.get('avg_processing_time', 0) > 30:
            recommendations.append("Consider increasing max_workers for faster processing of large batches")
            recommendations.append("Large files detected - consider preprocessing or splitting large files")

        if performance_stats.get('processing_time_std', 0) > 10:
            recommendations.append("High variance in processing times - consider load balancing or resource optimization")

        if not recommendations:
            recommendations.append("Batch processing completed successfully with good performance")

        return recommendations

    def cancel_processing(self):
        """Cancel ongoing batch processing"""
        self.cancel_requested = True
        logger.info("Batch processing cancellation requested")

    def is_processing_active(self) -> bool:
        """Check if batch processing is currently active"""
        return self.is_processing

    def get_processing_status(self) -> Dict[str, Any]:
        """Get current processing status"""
        return {
            'is_processing': self.is_processing,
            'cancel_requested': self.cancel_requested,
            'statistics': self.processing_stats,
            'errors_count': len(self.errors),
            'results_count': len(self.results)
        }

    def export_results_to_csv(self, output_path: str) -> bool:
        """Export batch results to CSV"""
        try:
            if not self.results:
                return False

            # Prepare data for CSV
            csv_data = []
            for file_path, result in self.results.items():
                row = {
                    'file_path': file_path,
                    'file_name': Path(file_path).name,
                    'file_extension': Path(file_path).suffix,
                    'success': result.get('success', False),
                    'processing_time': result.get('processing_time', 0),
                    'processed_at': result.get('processed_at', ''),
                    'error': result.get('error', ''),
                }

                # Add result details if available
                if 'result' in result and isinstance(result['result'], dict):
                    for key, value in result['result'].items():
                        if isinstance(value, (str, int, float, bool)):
                            row[f'result_{key}'] = value
                        else:
                            row[f'result_{key}'] = json.dumps(value)

                csv_data.append(row)

            # Create DataFrame and export
            df = pd.DataFrame(csv_data)
            df.to_csv(output_path, index=False)

            return True

        except Exception as e:
            logger.error(f"CSV export failed: {e}")
            return False

    def export_results_to_json(self, output_path: str) -> bool:
        """Export batch results to JSON"""
        try:
            export_data = {
                'batch_info': {
                    'name': self.processing_stats.get('batch_name', 'batch_analysis'),
                    'exported_at': datetime.now().isoformat(),
                    'statistics': self.processing_stats
                },
                'results': self.results,
                'errors': self.errors,
                'summary': self._generate_batch_summary() if hasattr(self, '_generate_batch_summary') else {}
            }

            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, indent=2, ensure_ascii=False)

            return True

        except Exception as e:
            logger.error(f"JSON export failed: {e}")
            return False


class BatchProcessorManager:
    """Manager for multiple batch processing operations"""

    def __init__(self):
        self.active_processors = {}
        self.completed_batches = {}
        self.processor_lock = threading.Lock()

    def create_batch_processor(self, batch_id: str, max_workers: int = 4,
                             progress_callback: Optional[Callable] = None) -> BatchProcessor:
        """Create a new batch processor"""
        with self.processor_lock:
            processor = BatchProcessor(max_workers=max_workers, progress_callback=progress_callback)
            self.active_processors[batch_id] = processor
            return processor

    def get_processor(self, batch_id: str) -> Optional[BatchProcessor]:
        """Get a batch processor by ID"""
        with self.processor_lock:
            return self.active_processors.get(batch_id)

    def remove_processor(self, batch_id: str):
        """Remove a completed batch processor"""
        with self.processor_lock:
            if batch_id in self.active_processors:
                processor = self.active_processors[batch_id]
                if not processor.is_processing_active():
                    self.completed_batches[batch_id] = {
                        'processor': processor,
                        'completed_at': datetime.now(),
                        'statistics': processor.processing_stats
                    }
                    del self.active_processors[batch_id]

    def cancel_batch(self, batch_id: str) -> bool:
        """Cancel a batch processing operation"""
        processor = self.get_processor(batch_id)
        if processor and processor.is_processing_active():
            processor.cancel_processing()
            return True
        return False

    def get_active_batches(self) -> Dict[str, Dict]:
        """Get information about active batches"""
        with self.processor_lock:
            return {
                batch_id: {
                    'is_processing': processor.is_processing_active(),
                    'statistics': processor.processing_stats,
                    'status': processor.get_processing_status()
                }
                for batch_id, processor in self.active_processors.items()
            }

    def get_completed_batches(self) -> Dict[str, Dict]:
        """Get information about completed batches"""
        with self.processor_lock:
            return {
                batch_id: {
                    'completed_at': info['completed_at'],
                    'statistics': info['statistics']
                }
                for batch_id, info in self.completed_batches.items()
            }