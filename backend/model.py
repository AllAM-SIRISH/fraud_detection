import numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.model_selection import train_test_split
import joblib
import os

class FraudDetectionModel:
    def __init__(self):
        self.model = None
        self.scaler = None
        self.label_encoder = None
        self.feature_columns = None
        self.is_trained = False
        
    def preprocess_features(self, df):
        """Preprocess features for model training/prediction"""
        # Make a copy to avoid modifying original
        df_processed = df.copy()
        
        # Encode categorical variables
        if self.label_encoder is None:
            self.label_encoder = LabelEncoder()
            df_processed['transaction_type_encoded'] = self.label_encoder.fit_transform(
                df_processed['transaction_type']
            )
        else:
            df_processed['transaction_type_encoded'] = self.label_encoder.transform(
                df_processed['transaction_type']
            )
        
        # Select features for model
        feature_columns = [
            'amount',
            'transaction_type_encoded',
            'account_age_days',
            'location_risk_score',
            'device_risk_score',
            'transaction_hour',
            'past_transactions_24h'
        ]
        
        # Ensure all feature columns exist
        for col in feature_columns:
            if col not in df_processed.columns:
                raise ValueError(f"Feature column '{col}' not found in data")
        
        X = df_processed[feature_columns].copy()
        
        # Handle missing values
        X = X.fillna(X.mean())
        
        return X, feature_columns
    
    def train(self, df):
        """Train the Isolation Forest model"""
        print("Preprocessing features for training...")
        X, self.feature_columns = self.preprocess_features(df)
        
        # Scale features
        print("Scaling features...")
        self.scaler = StandardScaler()
        X_scaled = self.scaler.fit_transform(X)
        
        # Train Isolation Forest
        print("Training Isolation Forest model...")
        self.model = IsolationForest(
            n_estimators=100,
            max_samples='auto',
            contamination=0.04,  # Expected proportion of anomalies
            random_state=42,
            n_jobs=-1
        )
        
        self.model.fit(X_scaled)
        self.is_trained = True
        
        # Print training statistics
        predictions = self.model.predict(X_scaled)
        anomaly_scores = self.model.decision_function(X_scaled)
        
        n_anomalies = np.sum(predictions == -1)
        n_normal = np.sum(predictions == 1)
        
        print(f"Training completed!")
        print(f"Model detected {n_anomalies} anomalies out of {len(X)} transactions")
        print(f"Anomaly detection rate: {n_anomalies/len(X)*100:.2f}%")
        print(f"Average anomaly score: {np.mean(anomaly_scores):.4f}")
        
        return self.model
    
    def predict(self, transaction_data):
        """Make prediction on a single transaction"""
        if not self.is_trained:
            raise ValueError("Model must be trained before making predictions")
        
        # Convert to DataFrame if dict
        if isinstance(transaction_data, dict):
            df = pd.DataFrame([transaction_data])
        else:
            df = transaction_data.copy()
        
        # Preprocess features
        X, _ = self.preprocess_features(df)
        
        # Scale features
        X_scaled = self.scaler.transform(X)
        
        # Make prediction
        prediction = self.model.predict(X_scaled)[0]
        anomaly_score = self.model.decision_function(X_scaled)[0]
        
        # Convert prediction to human-readable format
        prediction_label = "FRAUD" if prediction == -1 else "SAFE"
        
        # Determine risk level based on anomaly score
        if anomaly_score < -0.1:
            risk_level = "HIGH"
        elif anomaly_score < 0:
            risk_level = "MEDIUM"
        else:
            risk_level = "LOW"
        
        # Generate explanation
        explanation = self._generate_explanation(transaction_data, anomaly_score, prediction_label)
        
        return {
            "prediction": prediction_label,
            "anomaly_score": float(anomaly_score),
            "risk_level": risk_level,
            "explanation": explanation
        }
    
    def _generate_explanation(self, transaction_data, anomaly_score, prediction_label):
        """Generate human-readable explanation for the prediction"""
        explanations = []
        
        if prediction_label == "FRAUD":
            explanations.append("Transaction flagged as potentially fraudulent")
            
            # Check specific risk factors
            amount = transaction_data.get('amount', 0)
            if amount > 10000:
                explanations.append(f"High transaction amount: ${amount:,.2f}")
            
            location_risk = transaction_data.get('location_risk_score', 0)
            if location_risk > 0.7:
                explanations.append(f"High location risk score: {location_risk:.3f}")
            
            device_risk = transaction_data.get('device_risk_score', 0)
            if device_risk > 0.7:
                explanations.append(f"High device risk score: {device_risk:.3f}")
            
            hour = transaction_data.get('transaction_hour', 0)
            if hour < 6 or hour > 22:
                explanations.append(f"Unusual transaction time: {hour}:00")
            
            past_tx = transaction_data.get('past_transactions_24h', 0)
            if past_tx > 20:
                explanations.append(f"High activity: {past_tx} transactions in 24h")
            
            account_age = transaction_data.get('account_age_days', 0)
            if account_age < 30:
                explanations.append(f"New account: {account_age} days old")
        else:
            explanations.append("Transaction appears normal")
            if anomaly_score > 0.1:
                explanations.append("Low risk profile detected")
        
        return " | ".join(explanations)
    
    def save_model(self, filepath):
        """Save the trained model and preprocessing objects"""
        if not self.is_trained:
            raise ValueError("Model must be trained before saving")
        
        model_data = {
            'model': self.model,
            'scaler': self.scaler,
            'label_encoder': self.label_encoder,
            'feature_columns': self.feature_columns,
            'is_trained': self.is_trained
        }
        
        joblib.dump(model_data, filepath)
        print(f"Model saved to {filepath}")
    
    def load_model(self, filepath):
        """Load a trained model and preprocessing objects"""
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"Model file not found: {filepath}")
        
        model_data = joblib.load(filepath)
        
        self.model = model_data['model']
        self.scaler = model_data['scaler']
        self.label_encoder = model_data['label_encoder']
        self.feature_columns = model_data['feature_columns']
        self.is_trained = model_data['is_trained']
        
        print(f"Model loaded from {filepath}")
