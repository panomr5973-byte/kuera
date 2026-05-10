#!/usr/bin/env python
"""
KUWERA World Bank Integration
Integrasi data World Bank untuk melatih AI Kuera dengan data ekonomi Indonesia
"""

import requests
import pandas as pd
import sqlite3
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from pathlib import Path
from dataclasses import dataclass

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class WorldBankIndicator:
    """Struktur data indikator World Bank"""
    code: str
    name: str
    description: str
    category: str


class WorldBankClient:
    """
    Client untuk mengakses API World Bank
    """
    BASE_URL = "https://api.worldbank.org/v2"
    
    # Indikator ekonomi penting untuk Indonesia
    INDICATORS = {
        'NY.GDP.MKTP.CD': WorldBankIndicator('NY.GDP.MKTP.CD', 'GDP (current US$)', 'Produk Domestik Bruto', 'Ekonomi'),
        'NY.GDP.MKTP.KD.ZG': WorldBankIndicator('NY.GDP.MKTP.KD.ZG', 'GDP growth (annual %)', 'Pertumbuhan GDP', 'Ekonomi'),
        'NY.GDP.PCAP.CD': WorldBankIndicator('NY.GDP.PCAP.CD', 'GDP per capita', 'GDP per kapita', 'Ekonomi'),
        'FP.CPI.TOTL.ZG': WorldBankIndicator('FP.CPI.TOTL.ZG', 'Inflation (consumer prices)', 'Inflasi', 'Ekonomi'),
        'NE.EXP.GNFS.CD': WorldBankIndicator('NE.EXP.GNFS.CD', 'Exports of goods and services', 'Ekspor', 'Perdagangan'),
        'NE.IMP.GNFS.CD': WorldBankIndicator('NE.IMP.GNFS.CD', 'Imports of goods and services', 'Impor', 'Perdagangan'),
        'SL.UEM.TOTL.ZS': WorldBankIndicator('SL.UEM.TOTL.ZS', 'Unemployment rate', 'Tingkat pengangguran', 'Ketenagakerjaan'),
        'SI.POV.NAHC': WorldBankIndicator('SI.POV.NAHC', 'Poverty headcount ratio', 'Tingkat kemiskinan', 'Sosial'),
        'SI.POV.GINI': WorldBankIndicator('SI.POV.GINI', 'GINI index', 'Indeks GINI', 'Sosial'),
        'SE.PRM.ENRR': WorldBankIndicator('SE.PRM.ENRR', 'School enrollment, primary', 'Tingkat pendaftaran SD', 'Pendidikan'),
        'SP.DYN.LE00.IN': WorldBankIndicator('SP.DYN.LE00.IN', 'Life expectancy at birth', 'Harapan hidup', 'Kesehatan'),
        'IT.NET.USER.ZS': WorldBankIndicator('IT.NET.USER.ZS', 'Internet users (% of population)', 'Pengguna internet', 'Infrastruktur'),
        'EG.ELC.ACCS.ZS': WorldBankIndicator('EG.ELC.ACCS.ZS', 'Access to electricity', 'Akses listrik', 'Infrastruktur'),
        'EN.ATM.CO2E.KT': WorldBankIndicator('EN.ATM.CO2E.KT', 'CO2 emissions (kt)', 'Emisi CO2', 'Lingkungan'),
        'SP.POP.TOTL': WorldBankIndicator('SP.POP.TOTL', 'Population, total', 'Total populasi', 'Demografi'),
    }
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({'User-Agent': 'Kuera-WorldBank-Integration/1.0'})
    
    def fetch_indicator(self, indicator_code: str, country: str = 'IDN', 
                        start_year: int = 2010, end_year: int = None) -> pd.DataFrame:
        """Fetch data indikator dari World Bank"""
        if end_year is None:
            end_year = datetime.now().year
        
        url = f"{self.BASE_URL}/country/{country}/indicator/{indicator_code}"
        params = {
            'date': f'{start_year}:{end_year}',
            'format': 'json',
            'per_page': 100
        }
        
        try:
            response = self.session.get(url, params=params, timeout=30)
            response.raise_for_status()
            data = response.json()
            
            if len(data) > 1 and data[1]:
                records = []
                for item in data[1]:
                    indicator_info = self.INDICATORS.get(indicator_code, 
                        WorldBankIndicator(indicator_code, indicator_code, '', 'Lainnya'))
                    records.append({
                        'year': int(item['date']) if item['date'] else None,
                        'value': item['value'],
                        'indicator_code': indicator_code,
                        'indicator_name': indicator_info.name,
                        'country': item['country']['value'],
                        'country_code': item['countryiso3code'],
                        'category': indicator_info.category,
                        'fetched_at': datetime.now().isoformat()
                    })
                
                df = pd.DataFrame(records)
                df = df.dropna(subset=['value'])
                return df.sort_values('year')
            
            return pd.DataFrame()
            
        except Exception as e:
            logger.error(f"Error fetching {indicator_code}: {e}")
            return pd.DataFrame()
    
    def fetch_all_indicators(self, country: str = 'IDN', start_year: int = 2010) -> pd.DataFrame:
        """Fetch semua indikator untuk Indonesia"""
        all_data = []
        
        logger.info(f"Fetching {len(self.INDICATORS)} indicators for {country}...")
        
        for code in self.INDICATORS.keys():
            df = self.fetch_indicator(code, country, start_year)
            if not df.empty:
                all_data.append(df)
                logger.info(f"  {code}: {len(df)} records")
        
        if all_data:
            return pd.concat(all_data, ignore_index=True)
        return pd.DataFrame()


class WorldBankDatabase:
    """
    Database untuk menyimpan data World Bank
    """
    def __init__(self, db_path: str = "data/worldbank_indonesia.db"):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()
    
    def _init_db(self):
        """Inisialisasi database schema"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Tabel data indikator
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS worldbank_indicators (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                year INTEGER,
                value REAL,
                indicator_code TEXT,
                indicator_name TEXT,
                country TEXT,
                country_code TEXT,
                category TEXT,
                fetched_at TEXT,
                UNIQUE(year, indicator_code)
            )
        ''')
        
        # Tabel metadata indikator
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS indicator_metadata (
                code TEXT PRIMARY KEY,
                name TEXT,
                description TEXT,
                category TEXT,
                unit TEXT,
                last_updated TEXT
            )
        ''')
        
        # Tabel training data (gabungan dengan feedback)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS worldbank_training (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                year INTEGER,
                gdp_growth REAL,
                inflation REAL,
                unemployment REAL,
                poverty_rate REAL,
                gini_index REAL,
                life_expectancy REAL,
                school_enrollment REAL,
                internet_users REAL,
                co2_emissions REAL,
                label INTEGER,
                description TEXT,
                created_at TEXT
            )
        ''')
        
        conn.commit()
        conn.close()
        logger.info(f"[OK] World Bank database initialized at {self.db_path}")
    
    def store_indicators(self, df: pd.DataFrame):
        """Simpan data indikator ke database"""
        if df.empty:
            logger.warning("No data to store")
            return
        
        conn = sqlite3.connect(self.db_path)
        
        for _, row in df.iterrows():
            try:
                conn.execute('''
                    INSERT OR REPLACE INTO worldbank_indicators 
                    (year, value, indicator_code, indicator_name, country, country_code, category, fetched_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    row['year'], row['value'], row['indicator_code'],
                    row['indicator_name'], row['country'], row['country_code'],
                    row['category'], row['fetched_at']
                ))
            except Exception as e:
                logger.error(f"Error storing row: {e}")
        
        conn.commit()
        conn.close()
        logger.info(f"[OK] Stored {len(df)} indicator records")
    
    def get_indicator_data(self, indicator_code: str) -> pd.DataFrame:
        """Ambil data indikator tertentu"""
        conn = sqlite3.connect(self.db_path)
        df = pd.read_sql_query('''
            SELECT * FROM worldbank_indicators 
            WHERE indicator_code = ? 
            ORDER BY year
        ''', conn, params=[indicator_code])
        conn.close()
        return df
    
    def get_all_data_pivot(self) -> pd.DataFrame:
        """Ambil semua data dalam format pivot (years x indicators)"""
        conn = sqlite3.connect(self.db_path)
        df = pd.read_sql_query('''
            SELECT year, indicator_code, value 
            FROM worldbank_indicators 
            ORDER BY year
        ''', conn)
        conn.close()
        
        if df.empty:
            return pd.DataFrame()
        
        pivot_df = df.pivot(index='year', columns='indicator_code', values='value')
        return pivot_df.reset_index()
    
    def get_latest_values(self) -> Dict:
        """Ambil nilai terbaru dari setiap indikator"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT wi.indicator_code, wi.indicator_name, wi.year, wi.value, wi.category
            FROM worldbank_indicators wi
            INNER JOIN (
                SELECT indicator_code, MAX(year) as max_year
                FROM worldbank_indicators
                GROUP BY indicator_code
            ) wm ON wi.indicator_code = wm.indicator_code AND wi.year = wm.max_year
        ''')
        
        results = {}
        for row in cursor.fetchall():
            code, name, year, value, category = row
            results[code] = {
                'name': name,
                'year': year,
                'value': value,
                'category': category
            }
        
        conn.close()
        return results


class WorldBankTrainer:
    """
    Trainer untuk melatih AI dengan data World Bank
    """
    def __init__(self, wb_db: WorldBankDatabase, ai_db_path: str = "logs/feedback/self_improve.db"):
        self.wb_db = wb_db
        self.ai_db_path = ai_db_path
    
    def prepare_economic_dataset(self) -> pd.DataFrame:
        """
        Siapkan dataset ekonomi untuk training
        Label: 1 = Ekonomi baik, 0 = Ekonomi perlu perhatian
        """
        pivot_df = self.wb_db.get_all_data_pivot()
        
        if pivot_df.empty:
            logger.error("No World Bank data available")
            return pd.DataFrame()
        
        # Rename columns untuk kemudahan - hanya yang ada
        column_mapping = {
            'NY.GDP.MKTP.KD.ZG': 'gdp_growth',
            'FP.CPI.TOTL.ZG': 'inflation',
            'SL.UEM.TOTL.ZS': 'unemployment',
            'SI.POV.NAHC': 'poverty_rate',
            'SI.POV.GINI': 'gini_index',
            'SP.DYN.LE00.IN': 'life_expectancy',
            'SE.PRM.ENRR': 'school_enrollment',
            'IT.NET.USER.ZS': 'internet_users',
            'EN.ATM.CO2E.KT': 'co2_emissions'
        }
        
        # Filter mapping hanya untuk kolom yang ada
        available_mapping = {k: v for k, v in column_mapping.items() if k in pivot_df.columns}
        df = pivot_df.rename(columns=available_mapping)
        
        # Buat label: Ekonomi baik jika GDP growth > 5% dan inflasi < 5%
        gdp_col = 'gdp_growth' if 'gdp_growth' in df.columns else None
        infl_col = 'inflation' if 'inflation' in df.columns else None
        
        if gdp_col and infl_col:
            df['label'] = ((df[gdp_col] > 5) & (df[infl_col] < 5)).astype(int)
        else:
            df['label'] = 0
        
        # Buat deskripsi
        def create_description(row):
            desc = f"Tahun {int(row['year'])}: "
            if 'gdp_growth' in row and pd.notna(row['gdp_growth']):
                desc += f"Pertumbuhan GDP {row['gdp_growth']:.1f}%, "
            if 'inflation' in row and pd.notna(row['inflation']):
                desc += f"Inflasi {row['inflation']:.1f}%, "
            if 'unemployment' in row and pd.notna(row['unemployment']):
                desc += f"Pengangguran {row['unemployment']:.1f}%"
            return desc.rstrip(", ")
        
        df['description'] = df.apply(create_description, axis=1)
        df['created_at'] = datetime.now().isoformat()
        
        return df
    
    def store_training_data(self, df: pd.DataFrame):
        """Simpan training data ke database World Bank"""
        conn = sqlite3.connect(self.wb_db.db_path)
        
        for _, row in df.iterrows():
            try:
                conn.execute('''
                    INSERT OR REPLACE INTO worldbank_training 
                    (year, gdp_growth, inflation, unemployment, poverty_rate, 
                     gini_index, life_expectancy, school_enrollment, internet_users,
                     co2_emissions, label, description, created_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    row.get('year'), row.get('gdp_growth'), row.get('inflation'),
                    row.get('unemployment'), row.get('poverty_rate'), row.get('gini_index'),
                    row.get('life_expectancy'), row.get('school_enrollment'),
                    row.get('internet_users'), row.get('co2_emissions'),
                    row.get('label'), row.get('description'), row.get('created_at')
                ))
            except Exception as e:
                logger.error(f"Error storing training row: {e}")
        
        conn.commit()
        conn.close()
        logger.info(f"[OK] Stored {len(df)} training records")
    
    def integrate_with_ai_feedback(self):
        """
        Integrasi data World Bank dengan feedback AI
        """
        conn = sqlite3.connect(self.ai_db_path)
        cursor = conn.cursor()
        
        # Tambah kolom metadata jika belum ada
        try:
            cursor.execute("ALTER TABLE interactions ADD COLUMN economic_context TEXT")
        except:
            pass
        
        # Get latest economic data
        latest = self.wb_db.get_latest_values()
        economic_summary = json.dumps(latest, ensure_ascii=False)
        
        # Update recent interactions dengan konteks ekonomi
        cursor.execute('''
            UPDATE interactions 
            SET economic_context = ?
            WHERE timestamp > datetime('now', '-1 day')
            AND economic_context IS NULL
        ''', (economic_summary,))
        
        conn.commit()
        conn.close()
        logger.info("[OK] Integrated economic context with AI feedback")


def main():
    """Main execution"""
    print("="*70)
    print("KUWERA WORLD BANK INTEGRATION")
    print("="*70)
    print(f"Time: {datetime.now()}")
    print("="*70)
    
    # 1. Inisialisasi database
    print("\n[1/4] Initializing World Bank database...")
    wb_db = WorldBankDatabase()
    
    # 2. Fetch data dari World Bank
    print("\n[2/4] Fetching data from World Bank API...")
    client = WorldBankClient()
    
    # Fetch data Indonesia
    df = client.fetch_all_indicators(country='IDN', start_year=2010)
    
    if not df.empty:
        print(f"\n[OK] Fetched {len(df)} records")
        print("\nIndicators available:")
        for code in df['indicator_code'].unique():
            count = len(df[df['indicator_code'] == code])
            name = df[df['indicator_code'] == code]['indicator_name'].iloc[0]
            print(f"  - {code}: {name} ({count} years)")
        
        # 3. Simpan ke database
        print("\n[3/4] Storing to database...")
        wb_db.store_indicators(df)
        
        # 4. Prepare training data
        print("\n[4/4] Preparing training dataset...")
        trainer = WorldBankTrainer(wb_db)
        training_df = trainer.prepare_economic_dataset()
        
        if not training_df.empty:
            trainer.store_training_data(training_df)
            
            print(f"\n[OK] Training dataset prepared with {len(training_df)} records")
            print("\nSample data:")
            print(training_df[['year', 'gdp_growth', 'inflation', 'unemployment', 'label']].head())
            
            # Integrasi dengan AI feedback
            trainer.integrate_with_ai_feedback()
        else:
            print("\n[WARNING] Could not prepare training dataset")
    else:
        print("\n[ERROR] Failed to fetch data from World Bank")
    
    # Show latest values
    print("\n" + "="*70)
    print("LATEST ECONOMIC INDICATORS - INDONESIA")
    print("="*70)
    latest = wb_db.get_latest_values()
    
    for code, data in sorted(latest.items(), key=lambda x: x[1]['category']):
        print(f"\n[{data['category']}] {data['name']}")
        print(f"  Tahun {data['year']}: {data['value']:,.2f}")
    
    print("\n" + "="*70)
    print("[DONE] World Bank integration complete!")
    print("="*70)


if __name__ == "__main__":
    main()
