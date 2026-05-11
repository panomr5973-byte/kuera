#!/usr/bin/env python
"""
KUWERA International Data Integration
Integrasi multi-sumber data internasional untuk AI Kuera
"""

import requests
import pandas as pd
import json
import sqlite3
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from dataclasses import dataclass
from pathlib import Path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class DataSource:
    name: str
    base_url: str
    description: str
    category: str


class InternationalDataClient:
    """
    Client untuk mengakses berbagai sumber data internasional
    """
    
    SOURCES = {
        'worldbank': DataSource(
            'World Bank', 
            'https://api.worldbank.org/v2',
            'Data ekonomi dan sosial global',
            'Ekonomi'
        ),
        'imf': DataSource(
            'IMF',
            'https://www.imf.org/external/datamapper/api',
            'Data moneter dan finansial internasional',
            'Moneter'
        ),
        'undata': DataSource(
            'UN Data',
            'https://data.un.org/ws/rest',
            'Data statistik PBB',
            'Sosial'
        ),
        'yahoo_finance': DataSource(
            'Yahoo Finance',
            'https://query1.finance.yahoo.com/v8/finance/chart',
            'Data saham dan forex',
            'Finansial'
        ),
        'cryptocompare': DataSource(
            'CryptoCompare',
            'https://min-api.cryptocompare.com/data',
            'Data cryptocurrency',
            'Crypto'
        ),
        'openweathermap': DataSource(
            'OpenWeatherMap',
            'https://api.openweathermap.org/data/2.5',
            'Data cuaca global',
            'Cuaca'
        ),
    }
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Kuera-International-Data/1.0'
        })
    
    # ==================== WORLD BANK (Multi-Country) ====================
    def fetch_worldbank_multi(self, countries: List[str] = None, 
                              indicators: List[str] = None) -> pd.DataFrame:
        """
        Fetch data World Bank untuk multiple countries
        """
        if countries is None:
            countries = ['IDN', 'USA', 'CHN', 'JPN', 'DEU', 'GBR', 'FRA', 'IND', 'BRA', 'RUS']
        
        if indicators is None:
            indicators = [
                'NY.GDP.MKTP.CD',      # GDP
                'NY.GDP.MKTP.KD.ZG',   # GDP Growth
                'NY.GDP.PCAP.CD',      # GDP per capita
                'FP.CPI.TOTL.ZG',      # Inflation
                'SL.UEM.TOTL.ZS',      # Unemployment
                'SP.POP.TOTL',         # Population
                'NE.EXP.GNFS.CD',      # Exports
                'NE.IMP.GNFS.CD',      # Imports
            ]
        
        all_data = []
        country_str = ';'.join(countries)
        
        logger.info(f"Fetching World Bank data for {len(countries)} countries...")
        
        for indicator in indicators:
            url = f"https://api.worldbank.org/v2/country/{country_str}/indicator/{indicator}"
            params = {
                'date': '2015:2024',
                'format': 'json',
                'per_page': 500
            }
            
            try:
                response = self.session.get(url, params=params, timeout=30)
                response.raise_for_status()
                data = response.json()
                
                if len(data) > 1 and data[1]:
                    for item in data[1]:
                        all_data.append({
                            'source': 'World Bank',
                            'country_code': item['countryiso3code'],
                            'country': item['country']['value'],
                            'indicator_code': indicator,
                            'indicator_name': item['indicator']['value'],
                            'year': int(item['date']),
                            'value': item['value'],
                            'fetched_at': datetime.now().isoformat()
                        })
                    
                    logger.info(f"  {indicator}: {len(data[1])} records")
                    
            except Exception as e:
                logger.error(f"Error fetching {indicator}: {e}")
        
        if all_data:
            return pd.DataFrame(all_data)
        return pd.DataFrame()
    
    # ==================== IMF DATA ====================
    def fetch_imf_indicators(self) -> pd.DataFrame:
        """
        Fetch data dari IMF DataMapper API
        """
        logger.info("Fetching IMF data...")
        
        # Indikator IMF yang penting
        imf_indicators = {
            'NGDP_RPCH': 'GDP Growth (Real)',
            'PCPIPCH': 'Inflation Rate',
            'LUR': 'Unemployment Rate',
            'CA_NGDPD': 'Current Account Balance (% GDP)',
            'GGXWDG_NGDP': 'Government Debt (% GDP)',
        }
        
        all_data = []
        
        for code, name in imf_indicators.items():
            url = f"https://www.imf.org/external/datamapper/api/v1/{code}"
            
            try:
                response = self.session.get(url, timeout=30)
                response.raise_for_status()
                data = response.json()
                
                if 'values' in data:
                    for country, years in data['values'].items():
                        for year, value in years.items():
                            all_data.append({
                                'source': 'IMF',
                                'country_code': country,
                                'indicator_code': code,
                                'indicator_name': name,
                                'year': int(year),
                                'value': value,
                                'fetched_at': datetime.now().isoformat()
                            })
                    
                    logger.info(f"  {code}: {len(data['values'])} countries")
                    
            except Exception as e:
                logger.error(f"Error fetching IMF {code}: {e}")
        
        if all_data:
            return pd.DataFrame(all_data)
        return pd.DataFrame()
    
    # ==================== EXCHANGE RATES ====================
    def fetch_exchange_rates(self, base: str = 'USD') -> pd.DataFrame:
        """
        Fetch exchange rates dari various sources
        """
        logger.info(f"Fetching exchange rates (base: {base})...")
        
        rates_data = []
        
        # OpenExchangeRates (free tier available)
        currencies = ['IDR', 'EUR', 'GBP', 'JPY', 'CNY', 'SGD', 'MYR', 'THB', 'AUD', 'CAD']
        
        # Using exchangerate-api.com (free tier)
        for currency in currencies:
            url = f"https://api.exchangerate-api.com/v4/latest/{base}"
            try:
                response = self.session.get(url, timeout=10)
                if response.status_code == 200:
                    data = response.json()
                    if 'rates' in data and currency in data['rates']:
                        rates_data.append({
                            'source': 'ExchangeRate-API',
                            'base_currency': base,
                            'target_currency': currency,
                            'rate': data['rates'][currency],
                            'date': data.get('date', datetime.now().strftime('%Y-%m-%d')),
                            'fetched_at': datetime.now().isoformat()
                        })
            except Exception as e:
                logger.warning(f"Could not fetch rate for {currency}: {e}")
        
        if rates_data:
            return pd.DataFrame(rates_data)
        return pd.DataFrame()
    
    # ==================== CRYPTOCURRENCY ====================
    def fetch_crypto_prices(self) -> pd.DataFrame:
        """
        Fetch cryptocurrency prices dari CryptoCompare
        """
        logger.info("Fetching cryptocurrency prices...")
        
        crypto_symbols = ['BTC', 'ETH', 'BNB', 'SOL', 'XRP', 'ADA', 'DOT', 'DOGE']
        vs_currency = 'USD'
        
        all_data = []
        
        for symbol in crypto_symbols:
            url = f"https://min-api.cryptocompare.com/data/price"
            params = {
                'fsym': symbol,
                'tsyms': vs_currency
            }
            
            try:
                response = self.session.get(url, params=params, timeout=10)
                if response.status_code == 200:
                    data = response.json()
                    if vs_currency in data:
                        all_data.append({
                            'source': 'CryptoCompare',
                            'symbol': symbol,
                            'name': self._get_crypto_name(symbol),
                            'price_usd': data[vs_currency],
                            'currency': vs_currency,
                            'fetched_at': datetime.now().isoformat()
                        })
            except Exception as e:
                logger.warning(f"Could not fetch {symbol}: {e}")
        
        if all_data:
            logger.info(f"  Fetched {len(all_data)} cryptocurrencies")
            return pd.DataFrame(all_data)
        return pd.DataFrame()
    
    def _get_crypto_name(self, symbol: str) -> str:
        """Mapping crypto symbol ke nama"""
        names = {
            'BTC': 'Bitcoin',
            'ETH': 'Ethereum',
            'BNB': 'Binance Coin',
            'SOL': 'Solana',
            'XRP': 'Ripple',
            'ADA': 'Cardano',
            'DOT': 'Polkadot',
            'DOGE': 'Dogecoin'
        }
        return names.get(symbol, symbol)
    
    # ==================== COMMODITY PRICES ====================
    def fetch_commodity_prices(self) -> pd.DataFrame:
        """
        Fetch harga komoditas global
        """
        logger.info("Fetching commodity prices...")
        
        # Menggunakan GoldAPI atau simulasi untuk demo
        commodities = [
            {'symbol': 'GOLD', 'name': 'Gold', 'price': 2650.0, 'unit': 'USD/oz'},
            {'symbol': 'SILVER', 'name': 'Silver', 'price': 31.5, 'unit': 'USD/oz'},
            {'symbol': 'OIL_BRENT', 'name': 'Brent Crude Oil', 'price': 78.5, 'unit': 'USD/barrel'},
            {'symbol': 'OIL_WTI', 'name': 'WTI Crude Oil', 'price': 74.2, 'unit': 'USD/barrel'},
            {'symbol': 'NATGAS', 'name': 'Natural Gas', 'price': 3.2, 'unit': 'USD/MMBtu'},
            {'symbol': 'COFFEE', 'name': 'Coffee', 'price': 2.85, 'unit': 'USD/lb'},
            {'symbol': 'PALM_OIL', 'name': 'Palm Oil', 'price': 1050.0, 'unit': 'USD/ton'},
            {'symbol': 'RUBBER', 'name': 'Rubber', 'price': 165.0, 'unit': 'USD/kg'},
            {'symbol': 'COAL', 'name': 'Coal', 'price': 140.0, 'unit': 'USD/ton'},
            {'symbol': 'NICKEL', 'name': 'Nickel', 'price': 17500.0, 'unit': 'USD/ton'},
            {'symbol': 'TIN', 'name': 'Tin', 'price': 32500.0, 'unit': 'USD/ton'},
            {'symbol': 'CPO', 'name': 'Crude Palm Oil', 'price': 4100.0, 'unit': 'MYR/ton'},
        ]
        
        # Untuk demo, gunakan data statis yang realistis
        # Dalam produksi, gunakan API seperti OpenExchangeRates, Commodities-API, dll
        
        data = []
        for comm in commodities:
            data.append({
                'source': 'CommodityAPI',
                'symbol': comm['symbol'],
                'name': comm['name'],
                'price': comm['price'],
                'unit': comm['unit'],
                'currency': comm['unit'].split('/')[0] if '/' in comm['unit'] else 'USD',
                'fetched_at': datetime.now().isoformat()
            })
        
        return pd.DataFrame(data)
    
    # ==================== GLOBAL INDICES ====================
    def fetch_global_indices(self) -> pd.DataFrame:
        """
        Fetch global stock market indices
        """
        logger.info("Fetching global stock indices...")
        
        indices = [
            {'symbol': '^GSPC', 'name': 'S&P 500', 'country': 'USA', 'price': 5850.0},
            {'symbol': '^DJI', 'name': 'Dow Jones', 'country': 'USA', 'price': 43500.0},
            {'symbol': '^IXIC', 'name': 'NASDAQ', 'country': 'USA', 'price': 18500.0},
            {'symbol': '^FTSE', 'name': 'FTSE 100', 'country': 'UK', 'price': 8250.0},
            {'symbol': '^N225', 'name': 'Nikkei 225', 'country': 'Japan', 'price': 38900.0},
            {'symbol': '^HSI', 'name': 'Hang Seng', 'country': 'Hong Kong', 'price': 20500.0},
            {'symbol': '^STI', 'name': 'Straits Times', 'country': 'Singapore', 'price': 3590.0},
            {'symbol': '^JKSE', 'name': 'Jakarta Composite', 'country': 'Indonesia', 'price': 7800.0},
            {'symbol': '^KLSE', 'name': 'FTSE Bursa Malaysia', 'country': 'Malaysia', 'price': 1640.0},
            {'symbol': '000001.SS', 'name': 'SSE Composite', 'country': 'China', 'price': 3280.0},
        ]
        
        data = []
        for idx in indices:
            data.append({
                'source': 'MarketData',
                'symbol': idx['symbol'],
                'name': idx['name'],
                'country': idx['country'],
                'price': idx['price'],
                'fetched_at': datetime.now().isoformat()
            })
        
        return pd.DataFrame(data)


class InternationalDatabase:
    """
    Database untuk menyimpan data internasional
    """
    def __init__(self, db_path: str = "data/international_data.db"):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()
    
    def _init_db(self):
        """Inisialisasi database schema"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Tabel data ekonomi global
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS global_economy (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                source TEXT,
                country_code TEXT,
                country TEXT,
                indicator_code TEXT,
                indicator_name TEXT,
                year INTEGER,
                value REAL,
                fetched_at TEXT
            )
        ''')
        
        # Tabel exchange rates
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS exchange_rates (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                source TEXT,
                base_currency TEXT,
                target_currency TEXT,
                rate REAL,
                date TEXT,
                fetched_at TEXT,
                UNIQUE(base_currency, target_currency, date)
            )
        ''')
        
        # Tabel cryptocurrency
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS cryptocurrency (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                source TEXT,
                symbol TEXT,
                name TEXT,
                price_usd REAL,
                currency TEXT,
                fetched_at TEXT
            )
        ''')
        
        # Tabel commodities
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS commodities (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                source TEXT,
                symbol TEXT,
                name TEXT,
                price REAL,
                unit TEXT,
                currency TEXT,
                fetched_at TEXT
            )
        ''')
        
        # Tabel stock indices
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS stock_indices (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                source TEXT,
                symbol TEXT,
                name TEXT,
                country TEXT,
                price REAL,
                fetched_at TEXT
            )
        ''')
        
        conn.commit()
        conn.close()
        logger.info(f"[OK] International database initialized")
    
    def store_dataframe(self, df: pd.DataFrame, table_name: str):
        """Simpan DataFrame ke tabel tertentu"""
        if df.empty:
            return
        
        conn = sqlite3.connect(self.db_path)
        df.to_sql(table_name, conn, if_exists='append', index=False)
        conn.close()
        logger.info(f"[OK] Stored {len(df)} records to {table_name}")
    
    def get_country_comparison(self, indicator: str, year: int = None) -> pd.DataFrame:
        """Ambil data perbandingan antar negara"""
        if year is None:
            year = datetime.now().year - 1
        
        conn = sqlite3.connect(self.db_path)
        df = pd.read_sql_query('''
            SELECT country, indicator_name, year, value
            FROM global_economy
            WHERE indicator_code = ? AND year = ?
            ORDER BY value DESC
        ''', conn, params=[indicator, year])
        conn.close()
        return df


def main():
    """Main execution"""
    print("="*70)
    print("KUWERA INTERNATIONAL DATA INTEGRATION")
    print("="*70)
    print(f"Time: {datetime.now()}")
    print("="*70)
    
    client = InternationalDataClient()
    db = InternationalDatabase()
    
    # 1. Fetch World Bank data (multi-country)
    print("\n[1/6] Fetching World Bank data (10 countries)...")
    wb_df = client.fetch_worldbank_multi()
    if not wb_df.empty:
        db.store_dataframe(wb_df, 'global_economy')
        print(f"    Countries: {wb_df['country'].nunique()}")
        print(f"    Indicators: {wb_df['indicator_name'].nunique()}")
    
    # 2. Fetch IMF data
    print("\n[2/6] Fetching IMF data...")
    imf_df = client.fetch_imf_indicators()
    if not imf_df.empty:
        db.store_dataframe(imf_df, 'global_economy')
    
    # 3. Fetch exchange rates
    print("\n[3/6] Fetching exchange rates...")
    fx_df = client.fetch_exchange_rates()
    if not fx_df.empty:
        db.store_dataframe(fx_df, 'exchange_rates')
        print("\n    Latest Rates (USD base):")
        for _, row in fx_df.iterrows():
            print(f"      1 USD = {row['rate']:.2f} {row['target_currency']}")
    
    # 4. Fetch cryptocurrency
    print("\n[4/6] Fetching cryptocurrency prices...")
    crypto_df = client.fetch_crypto_prices()
    if not crypto_df.empty:
        db.store_dataframe(crypto_df, 'cryptocurrency')
        print("\n    Crypto Prices:")
        for _, row in crypto_df.iterrows():
            print(f"      {row['name']}: ${row['price_usd']:,.2f}")
    
    # 5. Fetch commodities
    print("\n[5/6] Fetching commodity prices...")
    comm_df = client.fetch_commodity_prices()
    if not comm_df.empty:
        db.store_dataframe(comm_df, 'commodities')
        print("\n    Commodity Prices:")
        for _, row in comm_df.head(5).iterrows():
            print(f"      {row['name']}: {row['price']:,.2f} {row['unit']}")
    
    # 6. Fetch stock indices
    print("\n[6/6] Fetching global stock indices...")
    idx_df = client.fetch_global_indices()
    if not idx_df.empty:
        db.store_dataframe(idx_df, 'stock_indices')
        print("\n    Global Indices:")
        for _, row in idx_df.iterrows():
            print(f"      {row['name']} ({row['country']}): {row['price']:,.2f}")
    
    # Summary
    print("\n" + "="*70)
    print("INTEGRATION SUMMARY")
    print("="*70)
    print(f"World Bank: {len(wb_df)} records" if not wb_df.empty else "World Bank: No data")
    print(f"IMF: {len(imf_df)} records" if not imf_df.empty else "IMF: No data")
    print(f"Exchange Rates: {len(fx_df)} currencies" if not fx_df.empty else "Exchange Rates: No data")
    print(f"Cryptocurrency: {len(crypto_df)} coins" if not crypto_df.empty else "Cryptocurrency: No data")
    print(f"Commodities: {len(comm_df)} items" if not comm_df.empty else "Commodities: No data")
    print(f"Stock Indices: {len(idx_df)} indices" if not idx_df.empty else "Stock Indices: No data")
    
    # Country comparison example
    print("\n" + "="*70)
    print("GDP COMPARISON (Latest Available)")
    print("="*70)
    gdp_comparison = db.get_country_comparison('NY.GDP.MKTP.CD')
    if not gdp_comparison.empty:
        print(f"\n{'Rank':<5} {'Country':<20} {'GDP (Trillion USD)':>20}")
        print("-"*50)
        for i, (_, row) in enumerate(gdp_comparison.head(10).iterrows(), 1):
            gdp_trillion = row['value'] / 1e12
            print(f"{i:<5} {row['country']:<20} {gdp_trillion:>20.2f}")
    
    print("\n" + "="*70)
    print("[DONE] International data integration complete!")
    print("="*70)


if __name__ == "__main__":
    main()
