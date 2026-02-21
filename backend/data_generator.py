import numpy as np
import pandas as pd
from datetime import datetime, timedelta
import random

class TransactionDataGenerator:
    def __init__(self, seed=42):
        np.random.seed(seed)
        random.seed(seed)
        
    def generate_normal_transactions(self, n_transactions=10000):
        """Generate normal financial transactions with realistic patterns"""
        transactions = []
        
        for i in range(n_transactions):
            # Generate realistic amount distribution (log-normal)
            amount = np.random.lognormal(mean=3, sigma=1.5)
            amount = np.clip(amount, 1, 50000)
            
            # Transaction types with realistic probabilities
            transaction_types = ['purchase', 'transfer', 'withdrawal', 'payment']
            type_weights = [0.4, 0.25, 0.2, 0.15]
            transaction_type = np.random.choice(transaction_types, p=type_weights)
            
            # Account age (most accounts are established)
            account_age_days = np.random.gamma(shape=2, scale=365)
            
            # Risk scores (mostly low, occasional medium)
            location_risk_score = np.random.beta(a=2, b=10)
            device_risk_score = np.random.beta(a=3, b=8)
            
            # Transaction hour (daytime weighted)
            hour_weights = np.array([0.02, 0.01, 0.01, 0.01, 0.02, 0.03, 0.05, 0.08, 
                           0.10, 0.09, 0.08, 0.07, 0.06, 0.07, 0.08, 0.09,
                           0.10, 0.12, 0.15, 0.08, 0.05, 0.03, 0.02, 0.01])
            hour_weights = hour_weights / hour_weights.sum()  # Normalize to sum to 1
            transaction_hour = np.random.choice(24, p=hour_weights)
            
            # Past transactions (normal activity)
            past_transactions_24h = np.random.poisson(lam=5)
            
            transaction = {
                'transaction_id': f'TXN_{i+1:06d}',
                'amount': round(amount, 2),
                'transaction_type': transaction_type,
                'account_age_days': int(account_age_days),
                'location_risk_score': round(location_risk_score, 3),
                'device_risk_score': round(device_risk_score, 3),
                'transaction_hour': transaction_hour,
                'past_transactions_24h': past_transactions_24h,
                'is_anomaly': 0
            }
            transactions.append(transaction)
            
        return transactions
    
    def generate_fraudulent_transactions(self, n_transactions=400):
        """Generate fraudulent transactions with suspicious patterns"""
        transactions = []
        
        for i in range(n_transactions):
            fraud_type = np.random.choice(['high_amount', 'late_night', 'high_risk', 'burst'])
            
            if fraud_type == 'high_amount':
                # Extremely high amounts
                amount = np.random.lognormal(mean=8, sigma=1.5)
                amount = np.clip(amount, 10000, 100000)
                transaction_type = np.random.choice(['transfer', 'purchase'])
                transaction_hour = np.random.choice(range(9, 21))  # Daytime to avoid suspicion
                
            elif fraud_type == 'late_night':
                # Late night activity
                amount = np.random.lognormal(mean=4, sigma=1.5)
                amount = np.clip(amount, 100, 10000)
                transaction_type = np.random.choice(['transfer', 'withdrawal'])
                transaction_hour = np.random.choice([0, 1, 2, 3, 4, 5, 22, 23])
                
            elif fraud_type == 'high_risk':
                # High risk scores
                amount = np.random.lognormal(mean=5, sigma=1.5)
                amount = np.clip(amount, 500, 20000)
                transaction_type = np.random.choice(['transfer', 'purchase'])
                transaction_hour = np.random.choice(24)
                location_risk_score = np.random.uniform(0.7, 1.0)
                device_risk_score = np.random.uniform(0.7, 1.0)
                
            else:  # burst
                # Burst activity pattern
                amount = np.random.lognormal(mean=3.5, sigma=1.0)
                amount = np.clip(amount, 50, 5000)
                transaction_type = np.random.choice(['purchase', 'payment'])
                transaction_hour = np.random.choice(24)
                past_transactions_24h = np.random.randint(20, 50)
            
            # Generate base values
            if fraud_type != 'high_risk':
                location_risk_score = np.random.beta(a=1, b=3)
                device_risk_score = np.random.beta(a=1, b=2)
            
            if fraud_type != 'burst':
                past_transactions_24h = np.random.poisson(lam=8)
            
            account_age_days = np.random.gamma(shape=1, scale=180)  # Often newer accounts
            
            transaction = {
                'transaction_id': f'FRD_{i+1:06d}',
                'amount': round(amount, 2),
                'transaction_type': transaction_type,
                'account_age_days': int(account_age_days),
                'location_risk_score': round(location_risk_score, 3),
                'device_risk_score': round(device_risk_score, 3),
                'transaction_hour': transaction_hour,
                'past_transactions_24h': past_transactions_24h,
                'is_anomaly': 1
            }
            transactions.append(transaction)
            
        return transactions
    
    def generate_dataset(self):
        """Generate complete dataset with normal and fraudulent transactions"""
        print("Generating normal transactions...")
        normal_transactions = self.generate_normal_transactions(10000)
        
        print("Generating fraudulent transactions...")
        fraudulent_transactions = self.generate_fraudulent_transactions(400)
        
        # Combine and shuffle
        all_transactions = normal_transactions + fraudulent_transactions
        np.random.shuffle(all_transactions)
        
        df = pd.DataFrame(all_transactions)
        print(f"Dataset generated: {len(df)} total transactions")
        print(f"Normal transactions: {len(df[df['is_anomaly'] == 0])}")
        print(f"Fraudulent transactions: {len(df[df['is_anomaly'] == 1])}")
        
        return df
    
    def get_sample_transaction(self, is_fraudulent=None):
        """Get a random sample transaction"""
        df = self.generate_dataset()
        
        if is_fraudulent is True:
            sample_df = df[df['is_anomaly'] == 1]
        elif is_fraudulent is False:
            sample_df = df[df['is_anomaly'] == 0]
        else:
            sample_df = df
            
        sample = sample_df.iloc[np.random.randint(0, len(sample_df))]
        return sample.to_dict()
