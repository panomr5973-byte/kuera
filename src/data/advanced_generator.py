"""
Advanced Data Generator
=======================
Generator data realistis untuk berbagai use case bisnis.
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random
from pathlib import Path


class BusinessDataGenerator:
    """
    Generator data bisnis realistis.
    
    Use Cases:
    1. Customer Churn Prediction
    2. Sales Forecasting
    3. Fraud Detection
    4. Credit Scoring
    5. Product Recommendation
    """
    
    def __init__(self, n_samples=10000, random_state=42):
        self.n_samples = n_samples
        np.random.seed(random_state)
        random.seed(random_state)
    
    def generate_customer_churn_data(self, output_path='data/raw/customer_churn.csv'):
        """
        Generate data untuk customer churn prediction.
        Realistis untuk telecom/banking/subscription business.
        """
        print(f"Generating Customer Churn Dataset ({self.n_samples} samples)...")
        
        # Customer demographics
        customer_id = range(1, self.n_samples + 1)
        age = np.random.normal(42, 13, self.n_samples).astype(int)
        age = np.clip(age, 18, 80)
        
        gender = np.random.choice(['Male', 'Female'], self.n_samples, p=[0.52, 0.48])
        
        # Location
        cities = ['Jakarta', 'Surabaya', 'Bandung', 'Medan', 'Semarang', 'Makassar', 'Palembang']
        city_weights = [0.35, 0.15, 0.12, 0.10, 0.10, 0.10, 0.08]
        city = np.random.choice(cities, self.n_samples, p=city_weights)
        
        # Account info
        tenure = np.random.exponential(24, self.n_samples).astype(int)
        tenure = np.clip(tenure, 0, 72)  # 0-72 months
        
        contract_types = ['Month-to-month', 'One year', 'Two year']
        contract = np.random.choice(contract_types, self.n_samples, p=[0.55, 0.25, 0.20])
        
        # Services
        phone_service = np.random.choice([0, 1], self.n_samples, p=[0.10, 0.90])
        internet_service = np.random.choice(['DSL', 'Fiber optic', 'No'], self.n_samples, p=[0.35, 0.45, 0.20])
        online_security = np.random.choice([0, 1], self.n_samples, p=[0.72, 0.28])
        tech_support = np.random.choice([0, 1], self.n_samples, p=[0.65, 0.35])
        streaming_tv = np.random.choice([0, 1], self.n_samples, p=[0.60, 0.40])
        
        # Financial
        monthly_charges = np.random.gamma(2, 30, self.n_samples) + 20
        monthly_charges = np.round(monthly_charges, 2)
        
        total_charges = monthly_charges * tenure + np.random.normal(0, 100, self.n_samples)
        total_charges = np.round(np.maximum(total_charges, 0), 2)
        
        # Payment
        payment_methods = ['Electronic check', 'Mailed check', 'Bank transfer', 'Credit card']
        payment_method = np.random.choice(payment_methods, self.n_samples, p=[0.35, 0.20, 0.25, 0.20])
        paperless_billing = np.random.choice([0, 1], self.n_samples, p=[0.40, 0.60])
        
        # Support tickets (churn indicator)
        num_support_tickets = np.random.poisson(1.5, self.n_samples)
        avg_resolution_time = np.random.exponential(3, self.n_samples)
        
        # Satisfaction score
        satisfaction = np.random.beta(2, 5, self.n_samples) * 10
        satisfaction = np.round(satisfaction, 1)
        
        # Create correlation for churn (target)
        churn_probability = (
            0.3 * (contract == 'Month-to-month').astype(float) +
            0.2 * (1 - (tenure / 72)) +
            0.15 * (monthly_charges / 120) +
            0.15 * (num_support_tickets / 5) +
            0.1 * (1 - tech_support) +
            0.1 * (satisfaction / 10)
        )
        
        # Add noise
        churn_probability += np.random.normal(0, 0.1, self.n_samples)
        churn_probability = np.clip(churn_probability, 0, 1)
        churn = (churn_probability > 0.5).astype(int)
        
        df = pd.DataFrame({
            'customer_id': customer_id,
            'age': age,
            'gender': gender,
            'city': city,
            'tenure_months': tenure,
            'contract_type': contract,
            'phone_service': phone_service,
            'internet_service': internet_service,
            'online_security': online_security,
            'tech_support': tech_support,
            'streaming_tv': streaming_tv,
            'monthly_charges': monthly_charges,
            'total_charges': total_charges,
            'payment_method': payment_method,
            'paperless_billing': paperless_billing,
            'num_support_tickets': num_support_tickets,
            'avg_resolution_time': np.round(avg_resolution_time, 1),
            'satisfaction_score': satisfaction,
            'churn': churn
        })
        
        # Add some missing values (realistic)
        missing_cols = ['satisfaction_score', 'avg_resolution_time']
        for col in missing_cols:
            mask = np.random.random(self.n_samples) < 0.03
            df.loc[mask, col] = np.nan
        
        # Save
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        df.to_csv(output_path, index=False)
        
        print(f"[OK] Saved to {output_path}")
        print(f"   Shape: {df.shape}")
        print(f"   Churn rate: {df['churn'].mean():.2%}")
        print(f"   Missing values: {df.isnull().sum().sum()}")
        
        return df
    
    def generate_sales_data(self, output_path='data/raw/sales_data.csv', days=365):
        """Generate sales forecasting data"""
        print(f"Generating Sales Dataset ({days} days)...")
        
        dates = pd.date_range(start='2023-01-01', periods=days, freq='D')
        
        # Base trend + seasonality
        base_sales = 1000
        trend = np.linspace(0, 200, days)  # Growth trend
        seasonality = 200 * np.sin(2 * np.pi * np.arange(days) / 365.25)  # Annual cycle
        weekly_pattern = [100, 150, 130, 140, 180, 250, 200] * (days // 7 + 1)
        weekly_pattern = weekly_pattern[:days]
        
        # Special events (promotions, holidays)
        events = np.zeros(days)
        event_days = np.random.choice(days, size=20, replace=False)
        events[event_days] = np.random.uniform(300, 800, 20)
        
        # Combine all components
        sales = base_sales + trend + seasonality + weekly_pattern + events
        sales += np.random.normal(0, 50, days)  # Noise
        sales = np.maximum(sales, 0).astype(int)
        
        # Features
        df = pd.DataFrame({
            'date': dates,
            'sales': sales,
            'day_of_week': dates.dayofweek,
            'month': dates.month,
            'is_month_start': dates.is_month_start.astype(int),
            'is_month_end': dates.is_month_end.astype(int),
            'is_weekend': (dates.dayofweek >= 5).astype(int),
            'promotion': (events > 0).astype(int),
            'temperature': np.random.normal(28, 5, days),  # Weather effect
            'competitor_price': np.random.uniform(80, 120, days),
        })
        
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        df.to_csv(output_path, index=False)
        
        print(f"[OK] Saved to {output_path}")
        print(f"   Shape: {df.shape}")
        print(f"   Total sales: ${df['sales'].sum():,}")
        print(f"   Avg daily: ${df['sales'].mean():.0f}")
        
        return df
    
    def generate_fraud_detection_data(self, output_path='data/raw/fraud_data.csv'):
        """Generate fraud detection data for banking/e-commerce"""
        print(f"Generating Fraud Detection Dataset ({self.n_samples} samples)...")
        
        n_fraud = int(self.n_samples * 0.02)  # 2% fraud rate
        n_normal = self.n_samples - n_fraud
        
        # Normal transactions
        normal_data = {
            'transaction_id': range(1, n_normal + 1),
            'amount': np.random.lognormal(4, 1.5, n_normal),
            'transaction_hour': np.random.choice(range(24), n_normal, p=self._hour_weights_normal()),
            'day_of_week': np.random.choice(range(7), n_normal),
            'merchant_category': np.random.choice(['retail', 'food', 'transport', 'entertainment', 'bills'], n_normal),
            'distance_from_home': np.random.exponential(5, n_normal),
            'days_since_last_transaction': np.random.exponential(3, n_normal),
            'transaction_count_24h': np.random.poisson(2, n_normal),
            'is_international': np.random.choice([0, 1], n_normal, p=[0.95, 0.05]),
            'is_fraud': 0
        }
        
        # Fraud transactions (anomalous patterns)
        fraud_data = {
            'transaction_id': range(n_normal + 1, self.n_samples + 1),
            'amount': np.random.lognormal(6, 2, n_fraud),  # Higher amounts
            'transaction_hour': np.random.choice(range(24), n_fraud, p=self._hour_weights_fraud()),
            'day_of_week': np.random.choice(range(7), n_fraud),
            'merchant_category': np.random.choice(['retail', 'food', 'transport', 'entertainment', 'bills'], n_fraud),
            'distance_from_home': np.random.exponential(500, n_fraud),  # Far from home
            'days_since_last_transaction': np.random.exponential(30, n_fraud),  # Inactive then sudden
            'transaction_count_24h': np.random.poisson(10, n_fraud),  # Many transactions
            'is_international': np.random.choice([0, 1], n_fraud, p=[0.60, 0.40]),  # More international
            'is_fraud': 1
        }
        
        df_normal = pd.DataFrame(normal_data)
        df_fraud = pd.DataFrame(fraud_data)
        
        df = pd.concat([df_normal, df_fraud], ignore_index=True)
        df = df.sample(frac=1).reset_index(drop=True)  # Shuffle
        
        # Round amounts
        df['amount'] = np.round(df['amount'], 2)
        df['distance_from_home'] = np.round(df['distance_from_home'], 1)
        
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        df.to_csv(output_path, index=False)
        
        print(f"[OK] Saved to {output_path}")
        print(f"   Shape: {df.shape}")
        print(f"   Fraud rate: {df['is_fraud'].mean():.2%}")
        print(f"   Avg fraud amount: ${df[df['is_fraud']==1]['amount'].mean():.2f}")
        print(f"   Avg normal amount: ${df[df['is_fraud']==0]['amount'].mean():.2f}")
        
        return df
    
    def _hour_weights_normal(self):
        """Normal transaction hour distribution"""
        weights = np.ones(24)
        weights[0:6] = 0.3  # Less activity at night
        weights[9:18] = 1.5  # Business hours
        weights[12:14] = 2.0  # Lunch time
        weights[18:22] = 1.8  # Evening shopping
        return weights / weights.sum()
    
    def _hour_weights_fraud(self):
        """Fraud transaction hour distribution"""
        weights = np.ones(24)
        weights[0:5] = 2.0  # More fraud at night when sleeping
        weights[9:18] = 0.5  # Less during business hours
        return weights / weights.sum()
    
    def generate_credit_scoring_data(self, output_path='data/raw/credit_data.csv'):
        """Generate credit scoring data"""
        print(f"Generating Credit Scoring Dataset ({self.n_samples} samples)...")
        
        # Personal info
        age = np.random.normal(40, 12, self.n_samples).astype(int)
        age = np.clip(age, 21, 70)
        
        income = np.random.lognormal(10.8, 0.8, self.n_samples)  # Annual income
        employment_years = np.random.exponential(5, self.n_samples)
        employment_years = np.clip(employment_years, 0, 40)
        
        # Credit history
        credit_history_length = np.random.exponential(8, self.n_samples)
        credit_history_length = np.clip(credit_history_length, 0, 40)
        
        num_credit_accounts = np.random.poisson(8, self.n_samples)
        num_credit_accounts = np.maximum(num_credit_accounts, 1)
        
        # Debt ratios
        debt_to_income = np.random.beta(2, 5, self.n_samples)
        credit_utilization = np.random.beta(3, 7, self.n_samples)
        
        # Payment behavior
        late_payments_12m = np.random.poisson(1, self.n_samples)
        max_delinquency = np.random.choice([0, 30, 60, 90, 120], self.n_samples, p=[0.7, 0.15, 0.08, 0.05, 0.02])
        
        # Recent inquiries (hard pulls)
        recent_inquiries = np.random.poisson(1, self.n_samples)
        
        # Bankruptcy/foreclosure
        bankruptcy = np.random.choice([0, 1], self.n_samples, p=[0.95, 0.05])
        
        # Calculate credit score based on features
        base_score = 600
        
        score = (
            base_score +
            0.2 * (age - 40) +
            50 * np.log(income / 50000) +
            5 * credit_history_length -
            30 * debt_to_income -
            40 * credit_utilization -
            20 * late_payments_12m -
            0.5 * max_delinquency -
            10 * recent_inquiries -
            100 * bankruptcy +
            np.random.normal(0, 30, self.n_samples)  # Randomness
        )
        
        score = np.clip(score, 300, 850).astype(int)
        
        # Risk category (using pandas for string handling)
        risk_category = pd.cut(score, 
            bins=[0, 550, 600, 650, 700, 750, 850],
            labels=['Risky', 'Very Poor', 'Poor', 'Fair', 'Good', 'Excellent']
        ).astype(str)
        
        df = pd.DataFrame({
            'applicant_id': range(1, self.n_samples + 1),
            'age': age,
            'annual_income': np.round(income, 2),
            'employment_years': np.round(employment_years, 1),
            'credit_history_years': np.round(credit_history_length, 1),
            'num_credit_accounts': num_credit_accounts,
            'debt_to_income_ratio': np.round(debt_to_income, 3),
            'credit_utilization': np.round(credit_utilization, 3),
            'late_payments_12m': late_payments_12m,
            'max_delinquency_days': max_delinquency,
            'recent_inquiries': recent_inquiries,
            'bankruptcy_history': bankruptcy,
            'credit_score': score,
            'risk_category': risk_category
        })
        
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        df.to_csv(output_path, index=False)
        
        print(f"[OK] Saved to {output_path}")
        print(f"   Shape: {df.shape}")
        print(f"   Avg credit score: {df['credit_score'].mean():.0f}")
        print(f"   Risk distribution:")
        for cat in ['Excellent', 'Good', 'Fair', 'Poor', 'Very Poor', 'Risky']:
            pct = (df['risk_category'] == cat).mean() * 100
            print(f"      {cat}: {pct:.1f}%")
        
        return df


def generate_all_datasets():
    """Generate all datasets"""
    generator = BusinessDataGenerator(n_samples=10000)
    
    print("="*60)
    print("GENERATING ALL DATASETS")
    print("="*60)
    print()
    
    # 1. Customer Churn
    generator.generate_customer_churn_data()
    print()
    
    # 2. Sales Data
    generator.generate_sales_data(days=730)
    print()
    
    # 3. Fraud Detection
    generator.generate_fraud_detection_data()
    print()
    
    # 4. Credit Scoring
    generator.generate_credit_scoring_data()
    print()
    
    print("="*60)
    print("ALL DATASETS GENERATED SUCCESSFULLY!")
    print("="*60)
    print()
    print("Files created:")
    print("  [OK] data/raw/customer_churn.csv")
    print("  [OK] data/raw/sales_data.csv")
    print("  [OK] data/raw/fraud_data.csv")
    print("  [OK] data/raw/credit_data.csv")


if __name__ == "__main__":
    generate_all_datasets()
