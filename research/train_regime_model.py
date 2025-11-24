"""
XGBoost Regime Classifier Training Script

Trains an XGBoost model to classify market regimes (Bull, Bear, Sideways).
Can use either live IBKR data or saved CSV files.

Usage:
    python train_regime_model.py --symbol SPY --start 2015-01-01 --end 2023-12-31
    python train_regime_model.py --csv data/SPY_daily.csv
"""

import argparse
import sys
import pandas as pd
import numpy as np
import xgboost as xgb
from sklearn.model_selection import TimeSeriesSplit
from sklearn.metrics import classification_report, confusion_matrix
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
from datetime import datetime

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent))

from src.feature_engineering import FeatureEngineer

class MarkdownReporter:
    """Generates markdown training reports similar to Jupyter notebook output."""
    
    def __init__(self, output_path):
        self.output_path = Path(output_path)
        self.sections = []
        self.start_time = datetime.now()
    
    def add_header(self, text, level=1):
        """Add markdown header."""
        self.sections.append(f"{'#' * level} {text}\n")
    
    def add_text(self, text):
        """Add plain text."""
        self.sections.append(f"{text}\n")
    
    def add_code(self, code, language='python'):
        """Add code block."""
        self.sections.append(f"```{language}\n{code}\n```\n")
    
    def add_dataframe(self, df, max_rows=10):
        """Add dataframe as markdown table."""
        self.sections.append(df.head(max_rows).to_markdown() + "\n")
    
    def add_metrics(self, metrics_dict):
        """Add metrics dictionary as formatted text."""
        self.sections.append("**Metrics:**\n")
        for key, value in metrics_dict.items():
            if isinstance(value, float):
                self.sections.append(f"- {key}: `{value:.4f}`\n")
            else:
                self.sections.append(f"- {key}: `{value}`\n")
        self.sections.append("\n")
    
    def add_image(self, image_path, caption=""):
        """
Add embedded image."""
        abs_path = Path(image_path).resolve()
        self.sections.append(f"![{caption}]({abs_path})\n\n")
    
    def save(self):
        """Save report to file."""
        content = "\n".join(self.sections)
        
        # Add footer
        duration = (datetime.now() - self.start_time).total_seconds()
        content += f"\n---\n\n*Report generated in {duration:.2f} seconds*\n"
        
        self.output_path.write_text(content, encoding='utf-8')
        print(f"\nMarkdown report saved to: {self.output_path}")


def load_data(csv_path=None, symbol=None, start_date=None, end_date=None):
    """Load data from CSV or fetch from IBKR."""
    if csv_path:
        print(f"Loading data from {csv_path}")
        df = pd.read_csv(csv_path, index_col=0, parse_dates=True)
    else:
        print(f"Fetching {symbol} data from IBKR...")
        from research.utils import SimpleDataFetcher
        fetcher = SimpleDataFetcher()
        df = fetcher.fetch_historical_data(
            symbol=symbol,
            start_date=start_date,
            end_date=end_date,
            bar_size='1 day'
        )
    
    print(f"Loaded {len(df)} rows")
    return df

def create_labels(df, lookback=20, bull_threshold=0.005, bear_threshold=-0.005):
    """Create regime labels from forward returns."""
    df['forward_return'] = df['close'].shift(-lookback) / df['close'] - 1
    
    def classify_regime(ret):
        if ret > bull_threshold:
            return 0  # Bull
        elif ret < bear_threshold:
            return 1  # Bear
        else:
            return 2  # Sideways
    
    df['regime'] = df['forward_return'].apply(classify_regime)
    df = df[:-lookback]  # Drop last N rows without forward return
    
    return df

def train_model(X_train, y_train, X_val, y_val, feature_cols):
    """Train XGBoost model."""
    # Create DMatrix
    dtrain = xgb.DMatrix(X_train, label=y_train, feature_names=feature_cols)
    dval = xgb.DMatrix(X_val, label=y_val, feature_names=feature_cols)
    
    # Hyperparameters
    params = {
        'objective': 'multi:softmax',
        'num_class': 3,
        'max_depth': 3,
        'learning_rate': 0.05,
        'subsample': 0.8,
        'colsample_bytree': 0.8,
        'lambda': 1.0,
        'eval_metric': 'mlogloss'
    }
    
    # Train
    evals = [(dtrain, 'train'), (dval, 'val')]
    model = xgb.train(
        params,
        dtrain,
        num_boost_round=200,
        evals=evals,
        early_stopping_rounds=20,
        verbose_eval=10
    )
    
    return model

def evaluate_model(model, X_test, y_test, feature_cols):
    """Evaluate model and print metrics."""
    dtest = xgb.DMatrix(X_test, label=y_test, feature_names=feature_cols)
    y_pred = model.predict(dtest)
    
    print("\n=== Test Set Performance ===")
    print(classification_report(y_test, y_pred, target_names=['Bull', 'Bear', 'Sideways']))
    
    # Confusion matrix
    cm = confusion_matrix(y_test, y_pred)
    plt.figure(figsize=(8, 6))
    sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', 
                xticklabels=['Bull', 'Bear', 'Sideways'],
                yticklabels=['Bull', 'Bear', 'Sideways'])
    plt.ylabel('True')
    plt.xlabel('Predicted')
    plt.title('Confusion Matrix - Test Set')
    plt.tight_layout()
    plt.savefig('../reports/regime_confusion_matrix.png')
    print("Saved confusion matrix to reports/regime_confusion_matrix.png")
    
    # Feature importance
    xgb.plot_importance(model, max_num_features=15)
    plt.title('Top 15 Feature Importances')
    plt.tight_layout()
    plt.savefig('../reports/regime_feature_importance.png')
    print("Saved feature importance to reports/regime_feature_importance.png")

def main():
    parser = argparse.ArgumentParser(description='Train XGBoost regime classifier')
    parser.add_argument('--csv', type=str, help='Path to CSV file with OHLCV data')
    parser.add_argument('--symbol', type=str, default='SPY', help='Symbol to fetch from IBKR')
    parser.add_argument('--start', type=str, default='2015-01-01', help='Start date')
    parser.add_argument('--end', type=str, default='2023-12-31', help='End date')
    parser.add_argument('--output', type=str, default='../models/xgb_regime_classifier.json',
                        help='Output model path')
    parser.add_argument('--report', type=str, default='../research/training_report.md',
                        help='Training report path')
    
    args = parser.parse_args()
    
    # Initialize markdown reporter
    reporter = MarkdownReporter(args.report)
    reporter.add_header("XGBoost Regime Classifier - Training Report")
    reporter.add_text(f"**Date**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    reporter.add_text(f"**Symbol**: {args.symbol if not args.csv else 'CSV: ' + args.csv}")
    reporter.add_text(f"**Period**: {args.start} to {args.end}\n")
    
    # Load data
    reporter.add_header("1. Data Loading", level=2)
    df = load_data(args.csv, args.symbol, args.start, args.end)
    df.columns = df.columns.str.lower() # Convert column names to lowercase
    reporter.add_text(f"Loaded **{len(df)}** rows of data")
    reporter.add_text("\n**Sample Data:**")
    reporter.add_dataframe(df[['open', 'high', 'low', 'close', 'volume']])
    
    # Generate features
    reporter.add_header("2. Feature Engineering", level=2)
    print("\nCalculating features...")
    fe = FeatureEngineer()
    df = fe.calculate_features(df)
    df = df.dropna()
    reporter.add_text(f"Calculated **{df.shape[1]}** features")
    reporter.add_text(f"Data after dropping NaN: **{len(df)}** rows\n")
    
    # Create labels
    reporter.add_header("3. Regime Labeling", level=2)
    print("\nCreating regime labels...")
    df = create_labels(df)
    regime_dist = df['regime'].value_counts()
    print(f"Regime distribution before split: {regime_dist}")
    reporter.add_text("**Regime Distribution:**")
    reporter.add_text(f"- Bull (0): {regime_dist.get(0, 0)} samples ({regime_dist.get(0, 0)/len(df)*100:.1f}%)")
    reporter.add_text(f"- Bear (1): {regime_dist.get(1, 0)} samples ({regime_dist.get(1, 0)/len(df)*100:.1f}%)")
    reporter.add_text(f"- Sideways (2): {regime_dist.get(2, 0)} samples ({regime_dist.get(2, 0)/len(df)*100:.1f}%)\n")
    
    # Prepare features
    feature_cols = [col for col in df.columns if col not in 
                    ['open', 'high', 'low', 'close', 'volume', 'forward_return', 'regime', 'average', 'barcount']]
    X = df[feature_cols].values
    y = df['regime'].values
    
    reporter.add_text(f"**Selected Features ({len(feature_cols)}):**")
    reporter.add_code(", ".join(feature_cols[:10]) + ("..." if len(feature_cols) > 10 else ""), language='text')
    
    # Time-series split
    reporter.add_header("4. Train/Val/Test Split", level=2)
    train_size = int(len(X) * 0.6)
    val_size = int(len(X) * 0.2)
    
    X_train, y_train = X[:train_size], y[:train_size]
    X_val, y_val = X[train_size:train_size+val_size], y[train_size:train_size+val_size]
    X_test, y_test = X[train_size+val_size:], y[train_size+val_size:]
    
    reporter.add_text(f"- **Train**: {X_train.shape[0]} samples (60%)")
    reporter.add_text(f"- **Validation**: {X_val.shape[0]} samples (20%)")
    reporter.add_text(f"- **Test**: {X_test.shape[0]} samples (20%)\n")
    
    # Train model
    reporter.add_header("5. Model Training", level=2)
    print("\nTraining XGBoost model...")
    model = train_model(X_train, y_train, X_val, y_val, feature_cols)
    reporter.add_metrics({
        'Best Iteration': model.best_iteration,
        'Best Validation Loss': model.best_score
    })
    
    # Evaluate
    reporter.add_header("6. Model Evaluation", level=2)
    dtest = xgb.DMatrix(X_test, label=y_test, feature_names=feature_cols)
    y_pred = model.predict(dtest)
    print(f"Unique classes in y_test: {np.unique(y_test)}")
    print(f"y_test class counts: {pd.Series(y_test).value_counts()}")
    
    # Classification report
    report_dict = classification_report(y_test, y_pred, target_names=['Bull', 'Bear', 'Sideways'], output_dict=True)
    reporter.add_text("**Classification Report:**\n")
    report_df = pd.DataFrame(report_dict).transpose()
    reporter.add_dataframe(report_df)
    
    # Confusion matrix
    cm = confusion_matrix(y_test, y_pred)
    plt.figure(figsize=(8, 6))
    sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', 
                xticklabels=['Bull', 'Bear', 'Sideways'],
                yticklabels=['Bull', 'Bear', 'Sideways'])
    plt.ylabel('True')
    plt.xlabel('Predicted')
    plt.title('Confusion Matrix - Test Set')
    plt.tight_layout()
    cm_path = Path(args.output).parent / 'regime_confusion_matrix.png'
    plt.savefig(cm_path)
    plt.close()
    
    reporter.add_text("\n**Confusion Matrix:**")
    reporter.add_image(cm_path, "Confusion Matrix")
    
    # Feature importance
    fig, ax = plt.subplots(figsize=(10, 8))
    xgb.plot_importance(model, max_num_features=15, ax=ax)
    plt.title('Top 15 Feature Importances')
    plt.tight_layout()
    fi_path = Path(args.output).parent / 'regime_feature_importance.png'
    plt.savefig(fi_path)
    plt.close()
    
    reporter.add_text("\n**Feature Importance:**")
    reporter.add_image(fi_path, "Top 15 Features")
    
    # Save model
    reporter.add_header("7. Model Persistence", level=2)
    model.save_model(args.output)
    reporter.add_text(f"✓ Model saved to `{args.output}`")
    reporter.add_text(f"✓ Confusion matrix saved to `{cm_path}`")
    reporter.add_text(f"✓ Feature importance saved to `{fi_path}`")
    
    # Save report
    reporter.save()
    print(f"\n{'='*60}")
    print("Training complete!")
    print(f"Model: {args.output}")
    print(f"Report: {args.report}")
    print(f"{'='*60}")


if __name__ == '__main__':
    main()
