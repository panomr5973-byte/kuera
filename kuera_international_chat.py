#!/usr/bin/env python
"""
KUWERA International Chat
Chat interface dengan akses data global dan internasional
"""

import sqlite3
import pandas as pd
from datetime import datetime
from typing import Dict, List


class InternationalChat:
    """
    Chat bot dengan kemampuan analisis data internasional
    """
    
    def __init__(self):
        self.wb_db_path = "data/worldbank_indonesia.db"
        self.intl_db_path = "data/international_data.db"
    
    def get_exchange_rates(self) -> str:
        """Tampilkan kurs mata uang terkini"""
        try:
            conn = sqlite3.connect(self.intl_db_path)
            df = pd.read_sql_query('''
                SELECT target_currency, rate, date
                FROM exchange_rates
                ORDER BY fetched_at DESC
                LIMIT 10
            ''', conn)
            conn.close()
            
            if df.empty:
                return "Data kurs belum tersedia. Silakan jalankan integrasi internasional terlebih dahulu."
            
            result = ["## Kurs Mata Uang Terhadap USD"]
            result.append("")
            result.append(f"{'Mata Uang':<15} {'Kurs':>15} {'Tanggal':>15}")
            result.append("-" * 45)
            
            for _, row in df.iterrows():
                result.append(f"{row['target_currency']:<15} {row['rate']:>15.2f} {row['date']:>15}")
            
            result.append("")
            result.append(f"Catatan: 1 USD setara dengan nilai di atas")
            
            return "\n".join(result)
            
        except Exception as e:
            return f"Error fetching exchange rates: {e}"
    
    def get_crypto_prices(self) -> str:
        """Tampilkan harga cryptocurrency"""
        try:
            conn = sqlite3.connect(self.intl_db_path)
            df = pd.read_sql_query('''
                SELECT symbol, name, price_usd
                FROM cryptocurrency
                ORDER BY price_usd DESC
            ''', conn)
            conn.close()
            
            if df.empty:
                return "Data cryptocurrency belum tersedia."
            
            result = ["## Harga Cryptocurrency (USD)"]
            result.append("")
            result.append(f"{'Nama':<20} {'Simbol':<10} {'Harga (USD)':>20}")
            result.append("-" * 50)
            
            for _, row in df.iterrows():
                result.append(f"{row['name']:<20} {row['symbol']:<10} {row['price_usd']:>20,.2f}")
            
            return "\n".join(result)
            
        except Exception as e:
            return f"Error fetching crypto: {e}"
    
    def get_commodity_prices(self) -> str:
        """Tampilkan harga komoditas"""
        try:
            conn = sqlite3.connect(self.intl_db_path)
            df = pd.read_sql_query('''
                SELECT name, price, unit
                FROM commodities
                ORDER BY 
                    CASE 
                        WHEN name IN ('Gold', 'Silver', 'Brent Crude Oil', 'WTI Crude Oil') THEN 0
                        ELSE 1
                    END,
                    name
            ''', conn)
            conn.close()
            
            if df.empty:
                return "Data komoditas belum tersedia."
            
            result = ["## Harga Komoditas Global"]
            result.append("")
            result.append(f"{'Komoditas':<25} {'Harga':>20} {'Unit':>15}")
            result.append("-" * 60)
            
            for _, row in df.iterrows():
                result.append(f"{row['name']:<25} {row['price']:>20,.2f} {row['unit']:>15}")
            
            return "\n".join(result)
            
        except Exception as e:
            return f"Error fetching commodities: {e}"
    
    def get_global_indices(self) -> str:
        """Tampilkan indeks saham global"""
        try:
            conn = sqlite3.connect(self.intl_db_path)
            df = pd.read_sql_query('''
                SELECT name, country, price
                FROM stock_indices
                ORDER BY 
                    CASE country
                        WHEN 'USA' THEN 0
                        WHEN 'Japan' THEN 1
                        WHEN 'UK' THEN 2
                        WHEN 'China' THEN 3
                        WHEN 'Hong Kong' THEN 4
                        WHEN 'Indonesia' THEN 5
                        ELSE 6
                    END
            ''', conn)
            conn.close()
            
            if df.empty:
                return "Data indeks saham belum tersedia."
            
            result = ["## Indeks Saham Global"]
            result.append("")
            result.append(f"{'Indeks':<25} {'Negara':<15} {'Nilai':>15}")
            result.append("-" * 55)
            
            for _, row in df.iterrows():
                result.append(f"{row['name']:<25} {row['country']:<15} {row['price']:>15,.2f}")
            
            return "\n".join(result)
            
        except Exception as e:
            return f"Error fetching indices: {e}"
    
    def get_gdp_ranking(self) -> str:
        """Tampilkan ranking GDP dunia"""
        try:
            conn = sqlite3.connect(self.intl_db_path)
            df = pd.read_sql_query('''
                SELECT country, MAX(year) as year, MAX(value) as gdp
                FROM global_economy
                WHERE indicator_code = 'NY.GDP.MKTP.CD'
                GROUP BY country
                ORDER BY gdp DESC
                LIMIT 15
            ''', conn)
            conn.close()
            
            if df.empty:
                return "Data GDP global belum tersedia."
            
            result = ["## Ranking GDP Dunia (Top 15)"]
            result.append("")
            result.append(f"{'Rank':<6} {'Negara':<25} {'GDP (Triliun USD)':>20} {'Tahun':>8}")
            result.append("-" * 60)
            
            for i, (_, row) in enumerate(df.iterrows(), 1):
                gdp_trillion = row['gdp'] / 1e12
                result.append(f"{i:<6} {row['country']:<25} {gdp_trillion:>20.2f} {int(row['year']):>8}")
            
            return "\n".join(result)
            
        except Exception as e:
            return f"Error fetching GDP ranking: {e}"
    
    def get_global_inflation(self) -> str:
        """Tampilkan data inflasi global"""
        try:
            conn = sqlite3.connect(self.intl_db_path)
            df = pd.read_sql_query('''
                SELECT country, year, value as inflation
                FROM global_economy
                WHERE indicator_code = 'FP.CPI.TOTL.ZG'
                AND year >= 2022
                ORDER BY year DESC, value DESC
            ''', conn)
            conn.close()
            
            if df.empty:
                return "Data inflasi global belum tersedia."
            
            # Ambil data terbaru per negara
            latest = df.groupby('country').first().reset_index()
            latest = latest.sort_values('inflation', ascending=False).head(15)
            
            result = ["## Inflasi Global (Negara dengan Inflasi Tertinggi)"]
            result.append("")
            result.append(f"{'Negara':<30} {'Tahun':>8} {'Inflasi (%)':>15}")
            result.append("-" * 55)
            
            for _, row in latest.iterrows():
                result.append(f"{row['country']:<30} {int(row['year']):>8} {row['inflation']:>15.2f}")
            
            return "\n".join(result)
            
        except Exception as e:
            return f"Error fetching inflation: {e}"
    
    def compare_asean_economies(self) -> str:
        """Bandingkan ekonomi ASEAN"""
        asean_countries = ['Indonesia', 'Thailand', 'Malaysia', 'Philippines', 
                          'Singapore', 'Vietnam', 'Myanmar', 'Cambodia', 
                          'Brunei', 'Lao PDR']
        
        try:
            conn = sqlite3.connect(self.intl_db_path)
            
            # GDP
            gdp_df = pd.read_sql_query('''
                SELECT country, MAX(value) as gdp
                FROM global_economy
                WHERE indicator_code = 'NY.GDP.MKTP.CD'
                AND country IN ({})
                GROUP BY country
                ORDER BY gdp DESC
            '''.format(','.join(['?']*len(asean_countries))), 
            conn, params=asean_countries)
            
            # GDP per capita
            gdppc_df = pd.read_sql_query('''
                SELECT country, MAX(value) as gdppc
                FROM global_economy
                WHERE indicator_code = 'NY.GDP.PCAP.CD'
                AND country IN ({})
                GROUP BY country
                ORDER BY gdppc DESC
            '''.format(','.join(['?']*len(asean_countries))), 
            conn, params=asean_countries)
            
            # GDP Growth
            gdp_growth_df = pd.read_sql_query('''
                SELECT country, value as growth
                FROM global_economy
                WHERE indicator_code = 'NY.GDP.MKTP.KD.ZG'
                AND country IN ({})
                AND year = (SELECT MAX(year) FROM global_economy WHERE indicator_code = 'NY.GDP.MKTP.KD.ZG')
                ORDER BY growth DESC
            '''.format(','.join(['?']*len(asean_countries))), 
            conn, params=asean_countries)
            
            conn.close()
            
            result = ["## Perbandingan Ekonomi ASEAN"]
            result.append("")
            
            if not gdp_df.empty:
                result.append("**GDP Total (2023-2024):**")
                result.append(f"{'Negara':<25} {'GDP (Miliar USD)':>20}")
                result.append("-" * 45)
                for _, row in gdp_df.iterrows():
                    result.append(f"{row['country']:<25} {row['gdp']/1e9:>20,.0f}")
                result.append("")
            
            if not gdppc_df.empty:
                result.append("**GDP per Kapita:**")
                result.append(f"{'Negara':<25} {'GDP/Capita (USD)':>20}")
                result.append("-" * 45)
                for _, row in gdppc_df.iterrows():
                    result.append(f"{row['country']:<25} {row['gdppc']:>20,.0f}")
                result.append("")
            
            if not gdp_growth_df.empty:
                result.append("**Pertumbuhan GDP Terkini:**")
                result.append(f"{'Negara':<25} {'Growth (%)':>15}")
                result.append("-" * 40)
                for _, row in gdp_growth_df.iterrows():
                    result.append(f"{row['country']:<25} {row['growth']:>15.2f}")
            
            return "\n".join(result)
            
        except Exception as e:
            return f"Error fetching ASEAN data: {e}"
    
    def process_query(self, query: str) -> str:
        """Proses query pengguna"""
        query_lower = query.lower()
        
        # Exchange rates
        if any(word in query_lower for word in ['kurs', 'exchange rate', 'mata uang', 'currency', 'usd', 'idr']):
            return self.get_exchange_rates()
        
        # Cryptocurrency
        if any(word in query_lower for word in ['crypto', 'bitcoin', 'ethereum', 'btc', 'eth', 'cryptocurrency']):
            return self.get_crypto_prices()
        
        # Commodities
        if any(word in query_lower for word in ['komoditas', 'commodity', 'emas', 'gold', 'minyak', 'oil', 'palm']):
            return self.get_commodity_prices()
        
        # Stock indices
        if any(word in query_lower for word in ['saham', 'stock', 'index', 'indeks', 'bursa', 'market']):
            return self.get_global_indices()
        
        # GDP Ranking
        if any(word in query_lower for word in ['gdp ranking', 'ranking gdp', ' ekonomi dunia', 'largest economy']):
            return self.get_gdp_ranking()
        
        # Global inflation
        if any(word in query_lower for word in ['inflasi dunia', 'global inflation', 'inflasi negara']):
            return self.get_global_inflation()
        
        # ASEAN comparison
        if any(word in query_lower for word in ['asean', 'asean comparison', 'bandingkan asean']):
            return self.compare_asean_economies()
        
        # Default
        return """Saya dapat membantu dengan data internasional:

**Perintah yang tersedia:**
- "Kurs mata uang" - Exchange rates terhadap USD
- "Harga crypto" - Bitcoin, Ethereum, dll
- "Harga komoditas" - Emas, minyak, CPO, dll
- "Indeks saham global" - S&P 500, Nikkei, IHSG, dll
- "Ranking GDP dunia" - 15 ekonomi terbesar
- "Inflasi global" - Data inflasi berbagai negara
- "Perbandingan ASEAN" - Ekonomi negara-negara ASEAN

Silakan tanyakan tentang data internasional yang Anda butuhkan!"""
    
    def chat(self):
        """Interactive chat"""
        print("="*70)
        print("KUWERA INTERNATIONAL CHAT")
        print("AI dengan data global dan internasional")
        print("="*70)
        print("Ketik 'exit' untuk keluar")
        print("-"*70)
        
        while True:
            try:
                query = input("\nAnda: ").strip()
                
                if query.lower() in ['exit', 'quit', 'keluar']:
                    print("\nTerima kasih telah menggunakan Kuwera International Chat!")
                    break
                
                if not query:
                    continue
                
                response = self.process_query(query)
                print(f"\nKuwera:\n{response}")
                
            except KeyboardInterrupt:
                print("\n\nTerima kasih!")
                break
            except Exception as e:
                print(f"\n[ERROR] {e}")


def main():
    chat = InternationalChat()
    chat.chat()


if __name__ == "__main__":
    main()
