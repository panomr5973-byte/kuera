#!/usr/bin/env python3
"""
Web Data Enricher - Fetch internet data to enrich training dataset
Integrates with kuera_web_access for AI improvement
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from kuera_web_access import WebAccessAgent
from data_collector import DataCollector
import pandas as pd
from datetime import datetime
import logging

logger = logging.getLogger('WebEnricher')

class WebEnricher:
    def __init__(self):
        self.web_agent = WebAccessAgent(max_results=10)
        self.collector = DataCollector()
    
    def generate_training_queries(self, num_queries=50):
        """Generate diverse training queries from Indonesian context"""
        topics = [
            'cuaca jakarta hari ini',
            'harga beras hari ini',
            'lowongan kerja jakarta',
            'resep nasi goreng enak',
            'cara daftar cpns 2026',
            'update bbm pertamina',
            'jadwal sholat jakarta',
            'kurs rupiah usd',
            'berita bola liga 1',
            'harga emas antam',
            'cara bikin kue lebaran',
            'tips hemat bensin motor'
        ] * 5  # Repeat for volume
        
        import random
        queries = random.sample(topics * 2, num_queries)
        return queries
    
    def enrich_from_web(self, num_queries=100, output_csv='data/web_enriched.csv'):
        """
        Fetch web data and log as interactions for retraining
        """
        queries = self.generate_training_queries(num_queries)
        enriched_data = []
        
        logger.info(f'Enriching with {num_queries} web queries...')
        
        for i, query in enumerate(queries):
            try:
                # Get web response
                result = self.web_agent.answer_with_web(query)
                
                if result['web_available'] and result.get('answer'):
                    # Simulate positive feedback interaction
                    interaction_id = self.collector.log_interaction(
                        user_input=query,
                        ai_response=result['answer'][:1000],  # Truncate
                        model_used='web_agent_v1',
                        user_feedback=1,  # Assume good web data
                        metadata={
                            'sources': len(result['sources']),
                            'avg_score': result.get('avg_score', 0),
                            'time_ms': result['time_ms']
                        }
                    )
                    
                    # Collect for CSV training
                    enriched_data.append({
                        'user_input': query,
                        'ai_response': result['answer'][:500],
                        'label': 1,  # Positive example
                        'sources_count': len(result['sources']),
                        'interaction_id': interaction_id
                    })
                    
                    logger.info(f'[{i+1}/{num_queries}] OK: {query} ({len(result["sources"])} sources)')
                
            except Exception as e:
                logger.error(f'Query {query}: {e}')
                continue
        
        # Save enriched dataset
        if enriched_data:
            df = pd.DataFrame(enriched_data)
            df.to_csv(output_csv, index=False)
            logger.info(f'Saved {len(df)} web-enriched examples to {output_csv}')
            
            # Log metric
            self.collector.log_model_metric(
                model_id='web_enricher',
                metric_name='enriched_samples',
                metric_value=len(df)
            )
        
        return enriched_data
    
    def retrain_with_web_data(self, web_csv='data/web_enriched.csv'):
        """Trigger retraining with new web data"""
        print('Integrate web CSV with existing data, then:')
        print('python self_evolving/retrainer.py --data web_enriched.csv')

if __name__ == '__main__':
    enricher = WebEnricher()
    
    # Enrich dataset
    data = enricher.enrich_from_web(num_queries=50)
    
    print(f'\n✅ Enriched {len(data)} examples from web')
    print('Next: python self_evolving/retrainer.py (add web data)')
    print('Web sources logged to DB for continuous learning!')

