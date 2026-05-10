#!/usr/bin/env python
"""
KUWERA World Bank Chat
Chat interface yang dapat mengakses dan menganalisis data World Bank
"""

import json
import sqlite3
import pickle
import re
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional


class WorldBankChat:
    """
    Chat bot dengan kemampuan analisis data ekonomi World Bank
    """
    
    def __init__(self):
        self.wb_db_path = "data/worldbank_indonesia.db"
        self.models_dir = Path("models/worldbank")
        self.economic_model = None
        self.load_model()
    
    def load_model(self):
        """Load trained economic model"""
        if self.models_dir.exists():
            model_files = sorted(self.models_dir.glob("*.pkl"), 
                                key=lambda x: x.stat().st_mtime, reverse=True)
            if model_files:
                try:
                    with open(model_files[0], 'rb') as f:
                        model_package = pickle.load(f)
                    self.economic_model = model_package
                    print(f"[OK] Loaded economic model: {model_files[0].name}")
                except Exception as e:
                    print(f"[WARNING] Could not load model: {e}")
    
    def get_latest_data(self) -> Dict:
        """Ambil data ekonomi terbaru"""
        conn = sqlite3.connect(self.wb_db_path)
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
    
    def get_historical_data(self, indicator_code: str, years: int = 10) -> List[Dict]:
        """Ambil data historis untuk indikator tertentu"""
        conn = sqlite3.connect(self.wb_db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT year, value, indicator_name
            FROM worldbank_indicators
            WHERE indicator_code = ?
            ORDER BY year DESC
            LIMIT ?
        ''', (indicator_code, years))
        
        results = []
        for row in cursor.fetchall():
            results.append({
                'year': row[0],
                'value': row[1],
                'indicator': row[2]
            })
        
        conn.close()
        return results
    
    def analyze_economic_condition(self) -> str:
        """Analisis kondisi ekonomi saat ini"""
        data = self.get_latest_data()
        
        if not data:
            return "Maaf, data ekonomi belum tersedia. Silakan jalankan integrasi World Bank terlebih dahulu."
        
        analysis = []
        analysis.append("## Analisis Kondisi Ekonomi Indonesia")
        analysis.append("")
        
        # GDP Analysis
        if 'NY.GDP.MKTP.KD.ZG' in data:
            gdp = data['NY.GDP.MKTP.KD.ZG']
            analysis.append(f"**Pertumbuhan Ekonomi ({gdp['year']})**:")
            analysis.append(f"- GDP Growth: {gdp['value']:.2f}%")
            
            if gdp['value'] > 5:
                analysis.append("- Status: Pertumbuhan tinggi dan sehat")
            elif gdp['value'] > 3:
                analysis.append("- Status: Pertumbuhan moderat")
            else:
                analysis.append("- Status: Pertumbuhan lambat, perlu stimulus")
            analysis.append("")
        
        # Inflation Analysis
        if 'FP.CPI.TOTL.ZG' in data:
            infl = data['FP.CPI.TOTL.ZG']
            analysis.append(f"**Inflasi ({infl['year']})**:")
            analysis.append(f"- Tingkat Inflasi: {infl['value']:.2f}%")
            
            if infl['value'] < 3:
                analysis.append("- Status: Inflasi rendah dan stabil (ideal)")
            elif infl['value'] < 5:
                analysis.append("- Status: Inflasi dalam batas target BI (3-5%)")
            else:
                analysis.append("- Status: Inflasi tinggi, tekanan harga perlu dikendalikan")
            analysis.append("")
        
        # Employment
        if 'SL.UEM.TOTL.ZS' in data:
            unemp = data['SL.UEM.TOTL.ZS']
            analysis.append(f"**Ketenagakerjaan ({unemp['year']})**:")
            analysis.append(f"- Tingkat Pengangguran: {unemp['value']:.2f}%")
            
            if unemp['value'] < 5:
                analysis.append("- Status: Pasar kerja ketat (low unemployment)")
            elif unemp['value'] < 7:
                analysis.append("- Status: Normal")
            else:
                analysis.append("- Status: Perlu menciptakan lebih banyak lapangan kerja")
            analysis.append("")
        
        # Poverty
        if 'SI.POV.NAHC' in data:
            pov = data['SI.POV.NAHC']
            analysis.append(f"**Kemiskinan ({pov['year']})**:")
            analysis.append(f"- Tingkat Kemiskinan: {pov['value']:.2f}%")
            analysis.append("")
        
        # Trade
        if 'NE.EXP.GNFS.CD' in data and 'NE.IMP.GNFS.CD' in data:
            exp = data['NE.EXP.GNFS.CD']
            imp = data['NE.IMP.GNFS.CD']
            balance = exp['value'] - imp['value']
            analysis.append(f"**Perdagangan ({exp['year']})**:")
            analysis.append(f"- Ekspor: US${exp['value']/1e9:.2f} miliar")
            analysis.append(f"- Impor: US${imp['value']/1e9:.2f} miliar")
            analysis.append(f"- Neraca: {'Surplus' if balance > 0 else 'Defisit'} US${abs(balance)/1e9:.2f} miliar")
            analysis.append("")
        
        # Overall assessment
        analysis.append("**Kesimpulan:**")
        
        # Hitung skor ekonomi sederhana
        score = 0
        factors = 0
        
        if 'NY.GDP.MKTP.KD.ZG' in data:
            gdp_val = data['NY.GDP.MKTP.KD.ZG']['value']
            score += min(gdp_val / 5, 2)  # Max 2 poin untuk GDP > 5%
            factors += 1
        
        if 'FP.CPI.TOTL.ZG' in data:
            infl_val = data['FP.CPI.TOTL.ZG']['value']
            score += 2 if 2 <= infl_val <= 4 else 1  # 2 poin untuk inflasi ideal
            factors += 1
        
        if 'SL.UEM.TOTL.ZS' in data:
            unemp_val = data['SL.UEM.TOTL.ZS']['value']
            score += 2 if unemp_val < 5 else 1
            factors += 1
        
        avg_score = score / factors if factors > 0 else 0
        
        if avg_score >= 1.5:
            analysis.append("Kondisi ekonomi Indonesia saat ini **BAIK** dengan pertumbuhan yang solid dan inflasi terkendali.")
        elif avg_score >= 1.0:
            analysis.append("Kondisi ekonomi Indonesia **STABIL** dengan beberapa area yang perlu perhatian.")
        else:
            analysis.append("Kondisi ekonomi perlu **PERHATIAN KHUSUS** dengan beberapa indikator yang menunjukkan tekanan.")
        
        return "\n".join(analysis)
    
    def predict_economic_outlook(self) -> str:
        """Prediksi prospek ekonomi"""
        if not self.economic_model:
            return "Model prediksi belum tersedia. Silakan train model terlebih dahulu."
        
        # Get latest data untuk prediksi
        data = self.get_latest_data()
        
        features = {
            'gdp_growth': data.get('NY.GDP.MKTP.KD.ZG', {}).get('value', 5.0),
            'inflation': data.get('FP.CPI.TOTL.ZG', {}).get('value', 3.0),
            'unemployment': data.get('SL.UEM.TOTL.ZS', {}).get('value', 5.0),
            'poverty_rate': data.get('SI.POV.NAHC', {}).get('value', 10.0),
            'gini_index': data.get('SI.POV.GINI', {}).get('value', 38.0),
            'life_expectancy': data.get('SP.DYN.LE00.IN', {}).get('value', 71.0),
            'school_enrollment': data.get('SE.PRM.ENRR', {}).get('value', 95.0),
            'internet_users': data.get('IT.NET.USER.ZS', {}).get('value', 70.0),
            'co2_emissions': data.get('EN.ATM.CO2E.KT', {}).get('value', 600000.0)
        }
        
        # Prediksi
        model = self.economic_model['model']
        scaler = self.economic_model['scaler']
        feature_names = self.economic_model['feature_names']
        
        import numpy as np
        input_data = [features.get(f, 0) for f in feature_names]
        X = np.array([input_data])
        
        if self.economic_model['model_type'] in ['lr', 'ensemble']:
            X = scaler.transform(X)
        
        prediction = model.predict(X)[0]
        probabilities = model.predict_proba(X)[0]
        
        result = []
        result.append("## Prospek Ekonomi Indonesia")
        result.append("")
        result.append(f"**Prediksi Model:** {'Ekonomi Baik' if prediction == 1 else 'Perlu Perhatian'}")
        result.append(f"**Confidence:** {max(probabilities):.1%}")
        result.append("")
        result.append("**Probabilitas:**")
        result.append(f"- Ekonomi Baik: {probabilities[1]:.1%}")
        result.append(f"- Perlu Perhatian: {probabilities[0]:.1%}")
        result.append("")
        
        if prediction == 1:
            result.append("Prospek ekonomi menunjukkan tren positif dengan pertumbuhan yang berkelanjutan.")
        else:
            result.append("Perlu kebijakan proaktif untuk mengatasi tantangan ekonomi yang dihadapi.")
        
        return "\n".join(result)
    
    def compare_with_neighbors(self) -> str:
        """Bandingkan ekonomi Indonesia dengan negara tetangga"""
        # Data statis untuk perbandingan (dapat diperluas dengan fetch data)
        comparison = {
            'Indonesia': {'gdp_growth': 5.0, 'inflation': 3.0, 'gdp_per_capita': 4788},
            'Malaysia': {'gdp_growth': 4.0, 'inflation': 2.5, 'gdp_per_capita': 11371},
            'Thailand': {'gdp_growth': 3.5, 'inflation': 2.0, 'gdp_per_capita': 6908},
            'Vietnam': {'gdp_growth': 6.5, 'inflation': 3.5, 'gdp_per_capita': 4163},
            'Filipina': {'gdp_growth': 5.5, 'inflation': 4.0, 'gdp_per_capita': 3548}
        }
        
        result = []
        result.append("## Perbandingan Ekonomi Regional")
        result.append("")
        result.append("| Negara | GDP Growth | Inflasi | GDP per Kapita (US$) |")
        result.append("|--------|------------|---------|---------------------|")
        
        for country, data in comparison.items():
            result.append(f"| {country} | {data['gdp_growth']}% | {data['inflation']}% | ${data['gdp_per_capita']:,} |")
        
        result.append("")
        result.append("**Analisis:**")
        result.append("- Indonesia memiliki pertumbuhan GDP yang kompetitif di kawasan")
        result.append("- GDP per kapita Indonesia masih di bawah Malaysia dan Thailand")
        result.append("- Inflasi Indonesia relatif terkendali dibanding Filipina")
        result.append("- Vietnam menunjukkan pertumbuhan tertinggi di ASEAN")
        
        return "\n".join(result)
    
    def process_query(self, query: str) -> str:
        """Proses query pengguna"""
        query_lower = query.lower()
        
        # Analisis kondisi ekonomi
        if any(word in query_lower for word in ['kondisi', 'analisis', 'analisa', 'ekonomi', 'bagaimana', 'gimana']):
            return self.analyze_economic_condition()
        
        # Prediksi/Prospek
        if any(word in query_lower for word in ['prediksi', 'prospek', 'masa depan', 'future', 'outlook', 'ramalan']):
            return self.predict_economic_outlook()
        
        # Perbandingan
        if any(word in query_lower for word in ['banding', 'compare', 'negeri', 'tetangga', 'asean', 'regional']):
            return self.compare_with_neighbors()
        
        # GDP
        if 'gdp' in query_lower or 'pertumbuhan' in query_lower:
            data = self.get_historical_data('NY.GDP.MKTP.KD.ZG', 5)
            if data:
                result = ["## Data Pertumbuhan GDP Indonesia"]
                for d in data:
                    result.append(f"- {d['year']}: {d['value']:.2f}%")
                return "\n".join(result)
        
        # Inflasi
        if 'inflasi' in query_lower or 'inflation' in query_lower:
            data = self.get_historical_data('FP.CPI.TOTL.ZG', 5)
            if data:
                result = ["## Data Inflasi Indonesia"]
                for d in data:
                    result.append(f"- {d['year']}: {d['value']:.2f}%")
                return "\n".join(result)
        
        # Default response
        return """Saya dapat membantu Anda dengan informasi ekonomi Indonesia dari data World Bank:

**Perintah yang tersedia:**
- "Analisis ekonomi" - Kondisi ekonomi terkini
- "Prediksi ekonomi" - Prospek dan ramalan
- "Bandingkan dengan negara tetangga" - Perbandingan regional
- "Data GDP" - Histori pertumbuhan GDP
- "Data inflasi" - Histori inflasi

Silakan ajukan pertanyaan spesifik tentang indikator ekonomi Indonesia!"""
    
    def chat(self):
        """Interactive chat session"""
        print("="*70)
        print("KUWERA WORLD BANK CHAT")
        print("AI dengan analisis data ekonomi Indonesia dari World Bank")
        print("="*70)
        print("Ketik 'exit' untuk keluar")
        print("-"*70)
        
        while True:
            try:
                query = input("\nAnda: ").strip()
                
                if query.lower() in ['exit', 'quit', 'keluar']:
                    print("\nTerima kasih telah menggunakan Kuwera World Bank Chat!")
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
    chat = WorldBankChat()
    chat.chat()


if __name__ == "__main__":
    main()
