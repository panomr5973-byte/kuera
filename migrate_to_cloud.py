#!/usr/bin/env python3
"""
KUERA Cloud Migration Tool
Mudah migrasi dari SQLite local ke PostgreSQL cloud

Supported:
- Supabase (Free tier available)
- AWS RDS PostgreSQL
- Google Cloud SQL
- Azure PostgreSQL
- PlanetScale (MySQL)
"""

import sqlite3
import os
import json
from datetime import datetime

class CloudMigrator:
    def __init__(self, local_db="data/kuera_database.db"):
        self.local_db = local_db
        self.conn = None
        self.cursor = None
        
    def connect(self):
        if not os.path.exists(self.local_db):
            print(f"[ERROR] Database tidak ditemukan: {self.local_db}")
            print("Jalankan: python kuera_setup_database.py")
            return False
            
        self.conn = sqlite3.connect(self.local_db)
        self.conn.row_factory = sqlite3.Row
        self.cursor = self.conn.cursor()
        print(f"[OK] Connected to: {self.local_db}")
        return True
    
    def get_migration_sql(self):
        """Generate PostgreSQL-compatible SQL dump"""
        
        migration_sql = """-- KUERA Cloud Migration Script
-- Generated: {}
-- Source: SQLite Local
-- Target: PostgreSQL Cloud

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Create tables
""".format(datetime.now().isoformat())

        tables = [
            ("interactions", """
                CREATE TABLE interactions (
                    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
                    user_id TEXT NOT NULL,
                    user_message TEXT NOT NULL,
                    ai_response TEXT NOT NULL,
                    intent TEXT,
                    sentiment TEXT,
                    confidence REAL DEFAULT 0.0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    session_id TEXT,
                    metadata JSONB DEFAULT '{{}}'
                );
                CREATE INDEX idx_interactions_user ON interactions(user_id);
                CREATE INDEX idx_interactions_time ON interactions(created_at);
            """),
            ("user_profiles", """
                CREATE TABLE user_profiles (
                    user_id TEXT PRIMARY KEY,
                    name TEXT,
                    province TEXT,
                    language TEXT DEFAULT 'id',
                    age_group TEXT,
                    gender TEXT,
                    occupation TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_active TIMESTAMP,
                    metadata JSONB DEFAULT '{{}}'
                );
            """),
            ("model_metrics", """
                CREATE TABLE model_metrics (
                    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
                    model_name TEXT NOT NULL,
                    f1_score REAL,
                    accuracy REAL,
                    training_samples INTEGER,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    metadata JSONB DEFAULT '{{}}'
                );
            """),
            ("sessions", """
                CREATE TABLE sessions (
                    session_id TEXT PRIMARY KEY,
                    user_id TEXT NOT NULL,
                    start_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    end_time TIMESTAMP,
                    messages_count INTEGER DEFAULT 0,
                    metadata JSONB DEFAULT '{{}}'
                );
            """),
            ("knowledge_base", """
                CREATE TABLE knowledge_base (
                    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
                    topic TEXT NOT NULL,
                    subtopic TEXT,
                    content TEXT NOT NULL,
                    language TEXT DEFAULT 'id',
                    province TEXT,
                    priority INTEGER DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """),
            ("analytics_daily", """
                CREATE TABLE analytics_daily (
                    date DATE PRIMARY KEY,
                    total_interactions INTEGER DEFAULT 0,
                    unique_users INTEGER DEFAULT 0,
                    avg_confidence REAL DEFAULT 0.0,
                    satisfaction_score REAL DEFAULT 0.0
                );
            """),
            ("sync_status", """
                CREATE TABLE sync_status (
                    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
                    last_sync TIMESTAMP,
                    sync_type TEXT,
                    status TEXT,
                    records_synced INTEGER DEFAULT 0
                );
            """)
        ]
        
        for table_name, ddl in tables:
            migration_sql += f"\n-- Table: {table_name}\n"
            migration_sql += ddl + "\n"
        
        # Get data from local database
        for table_name, _ in tables:
            try:
                self.cursor.execute(f"SELECT * FROM {table_name} LIMIT 1000")  # Limit for demo
                rows = self.cursor.fetchall()
                
                if rows:
                    migration_sql += f"\n-- Insert data into {table_name}\n"
                    columns = [desc[0] for desc in self.cursor.description]
                    
                    for row in rows:
                        values = []
                        for i, col in enumerate(row):
                            if col is None:
                                values.append("NULL")
                            elif isinstance(col, (int, float)):
                                values.append(str(col))
                            else:
                                # Escape single quotes
                                safe_val = str(col).replace("'", "''")
                                values.append(f"'{safe_val}'")
                        
                        migration_sql += f"INSERT INTO {table_name} ({', '.join(columns)}) VALUES ({', '.join(values)});\n"
            except Exception as e:
                migration_sql += f"-- Table {table_name}: {str(e)}\n"
        
        migration_sql += """
-- Create views
CREATE OR REPLACE VIEW daily_stats AS
SELECT 
    DATE(created_at) as date,
    COUNT(*) as total_interactions,
    COUNT(DISTINCT user_id) as unique_users,
    AVG(confidence) as avg_confidence
FROM interactions
GROUP BY DATE(created_at);

-- Migration complete
INSERT INTO sync_status (last_sync, sync_type, status, records_synced)
VALUES (CURRENT_TIMESTAMP, 'initial_migration', 'completed', 0);
"""
        
        return migration_sql
    
    def export_migration_script(self, output_path="exports/kuera_cloud_migration.sql"):
        """Export SQL for cloud migration"""
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        migration_sql = self.get_migration_sql()
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(migration_sql)
        
        print(f"[OK] Migration script exported: {output_path}")
        print(f"   Size: {len(migration_sql)} bytes")
        
        return output_path
    
    def get_supabase_config(self):
        """Generate Supabase configuration"""
        config = {
            "platform": "Supabase",
            "steps": [
                "1. Buat akun di supabase.com",
                "2. Create New Project (free tier)",
                "3. Buka SQL Editor",
                "4. Copy-paste isi kuera_cloud_migration.sql",
                "5. Run SQL",
                "6. Get connection string dari Settings > Database",
                "7. Update .env dengan SUPABASE_URL dan SUPABASE_KEY"
            ],
            "connection_template": "postgresql://postgres:[password]@db.[project-ref].supabase.co:5432/postgres",
            "features": [
                "Free tier: 500MB database",
                "Real-time subscriptions",
                "Auto-generated APIs",
                "Authentication ready"
            ]
        }
        return config
    
    def get_planetscale_config(self):
        """Generate PlanetScale configuration"""
        config = {
            "platform": "PlanetScale",
            "steps": [
                "1. Buat akun di planetscale.com",
                "2. Create New Database (free tier)",
                "3. Buka Console > SQL",
                "4. Import kuera_cloud_migration.sql",
                "5. Deploy to production",
                "6. Get connection string",
                "7. Update .env dengan DATABASE_URL"
            ],
            "connection_template": "mysql://[user]:[pass]@[host]/kuera?sslmode=require",
            "features": [
                "Free tier: 5GB storage",
                "MySQL compatible",
                "Branching & deploy requests",
                "Automatic backups"
            ]
        }
        return config
    
    def print_migration_guide(self):
        """Print complete migration guide"""
        print("\n" + "="*60)
        print("=== KUERA CLOUD MIGRATION GUIDE ===")
        print("="*60)
        
        print("\n LOCAL DATABASE STATS:")
        stats = self.get_stats()
        for key, value in stats.items():
            print(f"   {key}: {value}")
        
        print("\n" + "-"*60)
        print("[OPTION 1] SUPABASE (Recommended for beginners)")
        print("-"*60)
        supabase = self.get_supabase_config()
        for step in supabase["steps"]:
            print(f"   {step}")
        print(f"\n   Connection: {supabase['connection_template']}")
        print("\n   Features:")
        for feat in supabase["features"]:
            print(f"    {feat}")
        
        print("\n" + "-"*60)
        print("[OPTION 2] PLANETSCALE (MySQL compatible)")
        print("-"*60)
        planetscale = self.get_planetscale_config()
        for step in planetscale["steps"]:
            print(f"   {step}")
        print(f"\n   Connection: {planetscale['connection_template']}")
        print("\n   Features:")
        for feat in planetscale["features"]:
            print(f"    {feat}")
        
        print("\n" + "-"*60)
        print("[MIGRATION FILES]")
        print("-"*60)
        print(f"   SQL Script: exports/kuera_cloud_migration.sql")
        print(f"   Config Template: exports/cloud_config.json")
        print(f"   Run: python migrate_to_cloud.py --export")
        
        print("\n" + "="*60)
    
    def get_stats(self):
        """Get local database statistics"""
        stats = {}
        
        # Count interactions
        try:
            self.cursor.execute("SELECT COUNT(*) FROM interactions")
            stats["total_interactions"] = self.cursor.fetchone()[0]
        except:
            stats["total_interactions"] = 0
        
        # Count users
        try:
            self.cursor.execute("SELECT COUNT(DISTINCT user_id) FROM user_profiles")
            stats["unique_users"] = self.cursor.fetchone()[0]
        except:
            stats["unique_users"] = 0
        
        # Database file size
        if os.path.exists(self.local_db):
            size_mb = os.path.getsize(self.local_db) / (1024 * 1024)
            stats["database_size_mb"] = f"{size_mb:.2f}"
        
        return stats
    
    def close(self):
        if self.conn:
            self.conn.close()


def main():
    print("="*60)
    print("=== KUERA CLOUD MIGRATION TOOL ===")
    print("="*60)
    
    migrator = CloudMigrator()
    
    if not migrator.connect():
        return
    
    # Export migration script
    migrator.export_migration_script()
    
    # Print guide
    migrator.print_migration_guide()
    
    migrator.close()
    
    print("\n Migration preparation complete!")
    print("   Next: Choose a cloud provider and upload the SQL script")


if __name__ == "__main__":
    main()
