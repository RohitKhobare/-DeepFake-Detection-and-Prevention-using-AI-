"""
Enhanced Model Trainer
Advanced training system for deepfake detection models with comprehensive evaluation
"""

import os
import json
import numpy as np
import pandas as pd
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Callable, Any
import logging
from datetime import datetime
import tensorflow as tf
from tensorflow import keras
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, confusion_matrix, roc_auc_score
import matplotlib.pyplot as plt
import seaborn as sns
from concurrent.futures import ThreadPoolExecutor
import cv2
from tqdm import tqdm
import shutil

logger = logging.getLogger(__name__)


class EnhancedModelTrainer:
    """Enhanced model training system for deepfake detection"""

    def __init__(self, model_save_path: str = "models", log_path: str = "training_logs"):
        self.model_save_path = Path(model_save_path)
        self.log_path = Path(log_path)
        self.model_save_path.mkdir(exist_ok=True)
        self.log_path.mkdir(exist_ok=True)

        # Training configuration
        self.config = {
            'batch_size': 32,
            'epochs': 50,
            'learning_rate': 0.001,
            'validation_split': 0.2,
            'early_stopping_patience': 10,
            'reduce_lr_patience': 5,
            'model_architecture': 'efficientnet_b0',
            'input_shape': (224, 224, 3),
            'num_classes': 2
        }

        # Training history
        self.training_history = {}
        self.current_training_id = None

    def prepare_dataset(self, real_images_path: str, fake_images_path: str,
                       validation_split: float = 0.2, test_split: float = 0.1) -> Dict[str, Any]:
        """Prepare dataset for training"""
        logger.info("Preparing dataset for training...")

        # Load and preprocess images
        real_images = self._load_images_from_directory(real_images_path, label=0)
        fake_images = self._load_images_from_directory(fake_images_path, label=1)

        # Combine datasets
        all_images = real_images + fake_images
        X = np.array([item['image'] for item in all_images])
        y = np.array([item['label'] for item in all_images])

        # Split dataset
        X_train, X_temp, y_train, y_temp = train_test_split(
            X, y, test_size=(validation_split + test_split), random_state=42, stratify=y
        )

        X_val, X_test, y_val, y_test = train_test_split(
            X_temp, y_temp, test_size=(test_split / (validation_split + test_split)),
            random_state=42, stratify=y_temp
        )

        # Data augmentation
        train_datagen = keras.preprocessing.image.ImageDataGenerator(
            rotation_range=20,
            width_shift_range=0.2,
            height_shift_range=0.2,
            horizontal_flip=True,
            zoom_range=0.2,
            fill_mode='nearest'
        )

        val_datagen = keras.preprocessing.image.ImageDataGenerator()

        # Create data generators
        train_generator = train_datagen.flow(X_train, y_train, batch_size=self.config['batch_size'])
        val_generator = val_datagen.flow(X_val, y_val, batch_size=self.config['batch_size'])

        dataset_info = {
            'train_samples': len(X_train),
            'val_samples': len(X_val),
            'test_samples': len(X_test),
            'total_samples': len(X),
            'class_distribution': {
                'real': np.sum(y == 0),
                'fake': np.sum(y == 1)
            },
            'generators': {
                'train': train_generator,
                'validation': val_generator
            },
            'test_data': (X_test, y_test)
        }

        logger.info(f"Dataset prepared: {dataset_info['total_samples']} samples")
        return dataset_info

    def _load_images_from_directory(self, directory_path: str, label: int) -> List[Dict]:
        """Load images from directory with preprocessing"""
        images = []
        directory = Path(directory_path)

        if not directory.exists():
            logger.warning(f"Directory {directory_path} does not exist")
            return images

        image_extensions = {'.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.webp'}

        for image_file in directory.rglob('*'):
            if image_file.suffix.lower() in image_extensions:
                try:
                    # Load and preprocess image
                    image = cv2.imread(str(image_file))
                    if image is None:
                        continue

                    # Resize and normalize
                    image = cv2.resize(image, self.config['input_shape'][:2])
                    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
                    image = image.astype(np.float32) / 255.0

                    images.append({
                        'image': image,
                        'label': label,
                        'file_path': str(image_file),
                        'file_name': image_file.name
                    })

                except Exception as e:
                    logger.warning(f"Error loading image {image_file}: {e}")
                    continue

        logger.info(f"Loaded {len(images)} images from {directory_path}")
        return images

    def build_model(self, architecture: str = None, num_classes: int = None) -> keras.Model:
        """Build deepfake detection model"""
        if architecture:
            self.config['model_architecture'] = architecture
        if num_classes:
            self.config['num_classes'] = num_classes

        arch = self.config['model_architecture']
        input_shape = self.config['input_shape']

        logger.info(f"Building model with architecture: {arch}")

        if arch == 'efficientnet_b0':
            base_model = tf.keras.applications.EfficientNetB0(
                include_top=False,
                weights='imagenet',
                input_shape=input_shape
            )
        elif arch == 'resnet50':
            base_model = tf.keras.applications.ResNet50(
                include_top=False,
                weights='imagenet',
                input_shape=input_shape
            )
        elif arch == 'vgg16':
            base_model = tf.keras.applications.VGG16(
                include_top=False,
                weights='imagenet',
                input_shape=input_shape
            )
        else:
            # Custom CNN architecture
            return self._build_custom_cnn()

        # Freeze base model layers
        base_model.trainable = False

        # Add custom head
        inputs = keras.Input(shape=input_shape)
        x = base_model(inputs, training=False)
        x = keras.layers.GlobalAveragePooling2D()(x)
        x = keras.layers.Dropout(0.3)(x)
        x = keras.layers.Dense(256, activation='relu')(x)
        x = keras.layers.Dropout(0.3)(x)

        if self.config['num_classes'] == 2:
            outputs = keras.layers.Dense(1, activation='sigmoid')(x)
            loss = 'binary_crossentropy'
            metrics = ['accuracy', tf.keras.metrics.AUC()]
        else:
            outputs = keras.layers.Dense(self.config['num_classes'], activation='softmax')(x)
            loss = 'categorical_crossentropy'
            metrics = ['accuracy']

        model = keras.Model(inputs, outputs)

        # Compile model
        optimizer = keras.optimizers.Adam(learning_rate=self.config['learning_rate'])
        model.compile(optimizer=optimizer, loss=loss, metrics=metrics)

        logger.info(f"Model built with {model.count_params()} parameters")
        return model

    def _build_custom_cnn(self) -> keras.Model:
        """Build custom CNN architecture"""
        model = keras.Sequential([
            keras.layers.Conv2D(32, (3, 3), activation='relu', input_shape=self.config['input_shape']),
            keras.layers.MaxPooling2D((2, 2)),
            keras.layers.Conv2D(64, (3, 3), activation='relu'),
            keras.layers.MaxPooling2D((2, 2)),
            keras.layers.Conv2D(128, (3, 3), activation='relu'),
            keras.layers.MaxPooling2D((2, 2)),
            keras.layers.Flatten(),
            keras.layers.Dense(512, activation='relu'),
            keras.layers.Dropout(0.5),
            keras.layers.Dense(256, activation='relu'),
            keras.layers.Dropout(0.3),
            keras.layers.Dense(1 if self.config['num_classes'] == 2 else self.config['num_classes'],
                             activation='sigmoid' if self.config['num_classes'] == 2 else 'softmax')
        ])

        optimizer = keras.optimizers.Adam(learning_rate=self.config['learning_rate'])
        loss = 'binary_crossentropy' if self.config['num_classes'] == 2 else 'categorical_crossentropy'
        metrics = ['accuracy']

        model.compile(optimizer=optimizer, loss=loss, metrics=metrics)
        return model

    def train_model(self, model: keras.Model, dataset_info: Dict,
                   training_id: str = None, callbacks: List = None) -> Dict[str, Any]:
        """Train the model with comprehensive monitoring"""
        if training_id is None:
            training_id = f"training_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        self.current_training_id = training_id
        logger.info(f"Starting training session: {training_id}")

        # Setup callbacks
        if callbacks is None:
            callbacks = self._get_default_callbacks(training_id)

        # Get data generators
        train_generator = dataset_info['generators']['train']
        val_generator = dataset_info['generators']['validation']

        # Calculate steps
        steps_per_epoch = len(train_generator)
        validation_steps = len(val_generator)

        # Train model
        start_time = datetime.now()

        try:
            history = model.fit(
                train_generator,
                epochs=self.config['epochs'],
                validation_data=val_generator,
                steps_per_epoch=steps_per_epoch,
                validation_steps=validation_steps,
                callbacks=callbacks,
                verbose=1
            )

            training_time = (datetime.now() - start_time).total_seconds()

            # Evaluate on test set
            test_results = self._evaluate_on_test_set(model, dataset_info['test_data'])

            # Save training results
            training_results = {
                'training_id': training_id,
                'config': self.config.copy(),
                'history': history.history,
                'training_time': training_time,
                'final_metrics': {
                    'train_accuracy': history.history['accuracy'][-1],
                    'val_accuracy': history.history['val_accuracy'][-1],
                    'train_loss': history.history['loss'][-1],
                    'val_loss': history.history['val_loss'][-1]
                },
                'test_results': test_results,
                'completed_epochs': len(history.history['loss']),
                'early_stopped': len(history.history['loss']) < self.config['epochs']
            }

            # Save model
            model_path = self.model_save_path / f"{training_id}.h5"
            model.save(model_path)
            training_results['model_path'] = str(model_path)

            # Generate training report
            self._generate_training_report(training_results)

            # Store in history
            self.training_history[training_id] = training_results

            logger.info(f"Training completed: {training_id}")
            return training_results

        except Exception as e:
            logger.error(f"Training failed: {e}")
            return {'error': str(e), 'training_id': training_id}

    def _get_default_callbacks(self, training_id: str) -> List:
        """Get default training callbacks"""
        callbacks = []

        # Early stopping
        early_stopping = keras.callbacks.EarlyStopping(
            monitor='val_loss',
            patience=self.config['early_stopping_patience'],
            restore_best_weights=True,
            verbose=1
        )
        callbacks.append(early_stopping)

        # Reduce learning rate on plateau
        reduce_lr = keras.callbacks.ReduceLROnPlateau(
            monitor='val_loss',
            factor=0.5,
            patience=self.config['reduce_lr_patience'],
            min_lr=1e-7,
            verbose=1
        )
        callbacks.append(reduce_lr)

        # Model checkpoint
        checkpoint_path = self.model_save_path / f"{training_id}_checkpoint.h5"
        model_checkpoint = keras.callbacks.ModelCheckpoint(
            filepath=str(checkpoint_path),
            monitor='val_accuracy',
            save_best_only=True,
            verbose=1
        )
        callbacks.append(model_checkpoint)

        # TensorBoard logging
        log_dir = self.log_path / training_id
        tensorboard = keras.callbacks.TensorBoard(
            log_dir=str(log_dir),
            histogram_freq=1,
            write_graph=True,
            write_images=True
        )
        callbacks.append(tensorboard)

        # Custom progress callback
        progress_callback = TrainingProgressCallback()
        callbacks.append(progress_callback)

        return callbacks

    def _evaluate_on_test_set(self, model: keras.Model, test_data: Tuple) -> Dict:
        """Evaluate model on test set"""
        X_test, y_test = test_data

        # Get predictions
        y_pred_prob = model.predict(X_test, batch_size=self.config['batch_size'])
        y_pred = (y_pred_prob > 0.5).astype(int).flatten()

        # Calculate metrics
        if self.config['num_classes'] == 2:
            # Binary classification
            test_loss, test_accuracy = model.evaluate(X_test, y_test, verbose=0)

            # Additional metrics
            try:
                auc_score = roc_auc_score(y_test, y_pred_prob.flatten())
            except:
                auc_score = 0.0

            # Classification report
            class_report = classification_report(y_test, y_pred,
                                               target_names=['Real', 'Fake'],
                                               output_dict=True)

            # Confusion matrix
            cm = confusion_matrix(y_test, y_pred)

            return {
                'test_loss': test_loss,
                'test_accuracy': test_accuracy,
                'auc_score': auc_score,
                'classification_report': class_report,
                'confusion_matrix': cm.tolist(),
                'precision': class_report['weighted avg']['precision'],
                'recall': class_report['weighted avg']['recall'],
                'f1_score': class_report['weighted avg']['f1-score']
            }
        else:
            # Multi-class classification
            test_loss, test_accuracy = model.evaluate(X_test, y_test, verbose=0)
            return {
                'test_loss': test_loss,
                'test_accuracy': test_accuracy
            }

    def _generate_training_report(self, training_results: Dict):
        """Generate comprehensive training report"""
        training_id = training_results['training_id']
        report_path = self.log_path / f"{training_id}_report.json"

        # Create visualizations
        self._create_training_plots(training_results)

        # Save detailed report
        report = {
            'training_session': training_id,
            'timestamp': datetime.now().isoformat(),
            'configuration': training_results['config'],
            'performance_metrics': {
                'final_train_accuracy': training_results['final_metrics']['train_accuracy'],
                'final_val_accuracy': training_results['final_metrics']['val_accuracy'],
                'best_val_accuracy': max(training_results['history']['val_accuracy']),
                'final_train_loss': training_results['final_metrics']['train_loss'],
                'final_val_loss': training_results['final_metrics']['val_loss'],
                'best_val_loss': min(training_results['history']['val_loss']),
                'test_accuracy': training_results['test_results'].get('test_accuracy', 0),
                'test_loss': training_results['test_results'].get('test_loss', 0),
                'auc_score': training_results['test_results'].get('auc_score', 0)
            },
            'training_details': {
                'total_epochs': training_results['completed_epochs'],
                'training_time_seconds': training_results['training_time'],
                'early_stopped': training_results['early_stopped'],
                'batch_size': training_results['config']['batch_size']
            },
            'model_info': {
                'architecture': training_results['config']['model_architecture'],
                'input_shape': training_results['config']['input_shape'],
                'num_classes': training_results['config']['num_classes'],
                'model_path': training_results['model_path']
            },
            'recommendations': self._generate_training_recommendations(training_results)
        }

        with open(report_path, 'w') as f:
            json.dump(report, f, indent=2, default=str)

        logger.info(f"Training report saved: {report_path}")

    def _create_training_plots(self, training_results: Dict):
        """Create training visualization plots"""
        training_id = training_results['training_id']
        plot_dir = self.log_path / training_id
        plot_dir.mkdir(exist_ok=True)

        history = training_results['history']

        # Accuracy plot
        plt.figure(figsize=(12, 4))

        plt.subplot(1, 3, 1)
        plt.plot(history['accuracy'], label='Train Accuracy')
        plt.plot(history['val_accuracy'], label='Validation Accuracy')
        plt.title('Model Accuracy')
        plt.xlabel('Epoch')
        plt.ylabel('Accuracy')
        plt.legend()

        # Loss plot
        plt.subplot(1, 3, 2)
        plt.plot(history['loss'], label='Train Loss')
        plt.plot(history['val_loss'], label='Validation Loss')
        plt.title('Model Loss')
        plt.xlabel('Epoch')
        plt.ylabel('Loss')
        plt.legend()

        # Confusion matrix
        if 'confusion_matrix' in training_results['test_results']:
            plt.subplot(1, 3, 3)
            cm = np.array(training_results['test_results']['confusion_matrix'])
            sns.heatmap(cm, annot=True, fmt='d', cmap='Blues',
                       xticklabels=['Real', 'Fake'], yticklabels=['Real', 'Fake'])
            plt.title('Confusion Matrix')
            plt.xlabel('Predicted')
            plt.ylabel('True')

        plt.tight_layout()
        plt.savefig(plot_dir / 'training_plots.png', dpi=300, bbox_inches='tight')
        plt.close()

        # ROC curve if binary classification
        if 'auc_score' in training_results['test_results'] and training_results['test_results']['auc_score'] > 0:
            self._create_roc_curve(training_results, plot_dir)

    def _create_roc_curve(self, training_results: Dict, plot_dir: Path):
        """Create ROC curve plot"""
        # This would require storing prediction probabilities during evaluation
        # For now, just create a placeholder
        plt.figure(figsize=(8, 6))
        plt.plot([0, 1], [0, 1], 'k--', label='Random')
        plt.title('ROC Curve (Placeholder)')
        plt.xlabel('False Positive Rate')
        plt.ylabel('True Positive Rate')
        plt.legend()
        plt.savefig(plot_dir / 'roc_curve.png', dpi=300, bbox_inches='tight')
        plt.close()

    def _generate_training_recommendations(self, training_results: Dict) -> List[str]:
        """Generate training recommendations based on results"""
        recommendations = []

        metrics = training_results['final_metrics']
        test_results = training_results['test_results']

        # Overfitting check
        if metrics['train_accuracy'] > metrics['val_accuracy'] + 0.1:
            recommendations.append("Model shows signs of overfitting. Consider adding more regularization or data augmentation.")

        # Underfitting check
        if metrics['val_accuracy'] < 0.7:
            recommendations.append("Model performance is low. Consider increasing model complexity or training longer.")

        # Early stopping
        if training_results['early_stopped']:
            recommendations.append("Training stopped early. The model may benefit from more training or different architecture.")

        # Test performance
        if test_results.get('test_accuracy', 0) < 0.8:
            recommendations.append("Test accuracy is below threshold. Consider collecting more diverse training data.")

        if not recommendations:
            recommendations.append("Training completed successfully. Model performance looks good.")

        return recommendations

    def load_model(self, model_path: str) -> Optional[keras.Model]:
        """Load a trained model"""
        try:
            model = keras.models.load_model(model_path)
            logger.info(f"Model loaded from {model_path}")
            return model
        except Exception as e:
            logger.error(f"Failed to load model: {e}")
            return None

    def evaluate_model(self, model: keras.Model, test_data_path: str) -> Dict:
        """Evaluate model on new test data"""
        logger.info(f"Evaluating model on test data: {test_data_path}")

        # Load test data
        test_images = self._load_images_from_directory(test_data_path, label=-1)  # Label doesn't matter for evaluation

        if not test_images:
            return {'error': 'No test images found'}

        X_test = np.array([item['image'] for item in test_images])
        y_test = np.array([item['label'] for item in test_images])

        # Evaluate
        results = self._evaluate_on_test_set(model, (X_test, y_test))

        # Add file-level results
        file_results = []
        predictions = model.predict(X_test, batch_size=self.config['batch_size'])

        for i, pred in enumerate(predictions):
            file_results.append({
                'file_path': test_images[i]['file_path'],
                'file_name': test_images[i]['file_name'],
                'true_label': 'Real' if y_test[i] == 0 else 'Fake',
                'predicted_label': 'Real' if pred[0] < 0.5 else 'Fake',
                'confidence': float(pred[0]) if pred[0] < 0.5 else float(1 - pred[0])
            })

        results['file_results'] = file_results
        results['evaluation_timestamp'] = datetime.now().isoformat()

        return results

    def compare_models(self, model_paths: List[str], test_data_path: str) -> Dict:
        """Compare multiple models on the same test data"""
        logger.info(f"Comparing {len(model_paths)} models")

        results = {}
        test_images = self._load_images_from_directory(test_data_path, label=-1)

        if not test_images:
            return {'error': 'No test images found'}

        X_test = np.array([item['image'] for item in test_images])
        y_test = np.array([item['label'] for item in test_images])

        for model_path in model_paths:
            model_name = Path(model_path).stem
            model = self.load_model(model_path)

            if model:
                evaluation = self._evaluate_on_test_set(model, (X_test, y_test))
                results[model_name] = evaluation
                logger.info(f"Evaluated {model_name}: Test accuracy = {evaluation.get('test_accuracy', 0):.4f}")
            else:
                results[model_name] = {'error': 'Failed to load model'}

        # Create comparison summary
        comparison = self._create_model_comparison(results)
        results['comparison'] = comparison

        return results

    def _create_model_comparison(self, results: Dict) -> Dict:
        """Create model comparison summary"""
        valid_results = {k: v for k, v in results.items() if 'error' not in v}

        if not valid_results:
            return {'error': 'No valid model results for comparison'}

        # Find best models
        best_accuracy = max((v.get('test_accuracy', 0) for v in valid_results.values()))
        best_model = [k for k, v in valid_results.items() if v.get('test_accuracy', 0) == best_accuracy][0]

        best_auc = max((v.get('auc_score', 0) for v in valid_results.values()))
        best_auc_model = [k for k, v in valid_results.items() if v.get('auc_score', 0) == best_auc][0]

        return {
            'best_accuracy_model': best_model,
            'best_accuracy_score': best_accuracy,
            'best_auc_model': best_auc_model,
            'best_auc_score': best_auc,
            'model_rankings': sorted(
                [(k, v.get('test_accuracy', 0)) for k, v in valid_results.items()],
                key=lambda x: x[1],
                reverse=True
            )
        }

    def get_training_history(self, training_id: str = None) -> Dict:
        """Get training history"""
        if training_id:
            return self.training_history.get(training_id, {'error': 'Training session not found'})
        else:
            return {
                'total_sessions': len(self.training_history),
                'sessions': list(self.training_history.keys()),
                'summary': {
                    session_id: {
                        'final_accuracy': results['final_metrics']['val_accuracy'],
                        'training_time': results['training_time'],
                        'test_accuracy': results['test_results'].get('test_accuracy', 0)
                    }
                    for session_id, results in self.training_history.items()
                }
            }

    def cleanup_old_models(self, keep_recent: int = 5):
        """Clean up old model files, keeping only the most recent ones"""
        model_files = list(self.model_save_path.glob('*.h5'))
        model_files.sort(key=lambda x: x.stat().st_mtime, reverse=True)

        if len(model_files) > keep_recent:
            files_to_delete = model_files[keep_recent:]
            for file_path in files_to_delete:
                try:
                    file_path.unlink()
                    logger.info(f"Deleted old model: {file_path}")
                except Exception as e:
                    logger.error(f"Failed to delete {file_path}: {e}")

        return len(model_files) - keep_recent


class TrainingProgressCallback(keras.callbacks.Callback):
    """Custom callback for training progress monitoring"""

    def __init__(self):
        self.epoch_progress = {}

    def on_epoch_end(self, epoch, logs=None):
        self.epoch_progress[epoch] = logs.copy() if logs else {}

        # Log progress
        logger.info(f"Epoch {epoch + 1}: "
                   f"loss={logs.get('loss', 0):.4f}, "
                   f"accuracy={logs.get('accuracy', 0):.4f}, "
                   f"val_loss={logs.get('val_loss', 0):.4f}, "
                   f"val_accuracy={logs.get('val_accuracy', 0):.4f}")

    def get_progress(self):
        return self.epoch_progress


class ModelEnsembleTrainer:
    """Train ensemble of models for improved performance"""

    def __init__(self, trainer: EnhancedModelTrainer):
        self.trainer = trainer
        self.ensemble_models = []

    def train_ensemble(self, architectures: List[str], dataset_info: Dict) -> Dict:
        """Train multiple models with different architectures"""
        logger.info(f"Training ensemble with {len(architectures)} architectures")

        ensemble_results = {}

        for arch in architectures:
            logger.info(f"Training {arch} model...")

            # Build and train model
            model = self.trainer.build_model(architecture=arch)
            training_result = self.trainer.train_model(
                model, dataset_info,
                training_id=f"ensemble_{arch}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            )

            ensemble_results[arch] = training_result
            self.ensemble_models.append({
                'architecture': arch,
                'model': model,
                'training_result': training_result
            })

        # Create ensemble evaluation
        ensemble_eval = self._evaluate_ensemble(dataset_info['test_data'])

        return {
            'individual_results': ensemble_results,
            'ensemble_evaluation': ensemble_eval,
            'best_performing_model': max(ensemble_results.items(),
                                       key=lambda x: x[1]['test_results'].get('test_accuracy', 0))
        }

    def _evaluate_ensemble(self, test_data: Tuple) -> Dict:
        """Evaluate ensemble performance"""
        X_test, y_test = test_data

        # Get predictions from all models
        all_predictions = []

        for model_info in self.ensemble_models:
            model = model_info['model']
            try:
                pred = model.predict(X_test, batch_size=32)
                all_predictions.append(pred.flatten())
            except Exception as e:
                logger.error(f"Failed to get predictions from {model_info['architecture']}: {e}")
                continue

        if not all_predictions:
            return {'error': 'No valid predictions from ensemble models'}

        # Ensemble prediction (majority vote for binary, average for probabilities)
        ensemble_pred = np.mean(all_predictions, axis=0)
        ensemble_class_pred = (ensemble_pred > 0.5).astype(int)

        # Calculate ensemble metrics
        ensemble_accuracy = np.mean(ensemble_class_pred == y_test)

        try:
            ensemble_auc = roc_auc_score(y_test, ensemble_pred)
        except:
            ensemble_auc = 0.0

        return {
            'ensemble_accuracy': ensemble_accuracy,
            'ensemble_auc': ensemble_auc,
            'individual_model_count': len(all_predictions),
            'ensemble_prediction_std': np.std(ensemble_pred)
        }