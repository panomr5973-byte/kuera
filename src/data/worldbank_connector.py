"""KUERA AI — World Bank Data Connector.

Provides clean API access to World Bank economic data for Indonesia.
"""

import sqlite3
from pathlib import Path
from typing import Dict, List

from ..utils.config import settings


DB_PATH = settings.data_dir / "worldbank_indonesia.db"


def get_latest_economic_data() -> Dict:
    """Get the latest available data for all indicators.

    Returns:
        Dict grouped by category, each containing list of indicators
        with name, year, value, and unit.
    """
    if not DB_PATH.exists():
        return {"status": "error", "message": "Database not found. Run kuera_worldbank_setup.py first."}

    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        cursor.execute('''
            SELECT wi.indicator_code, wi.indicator_name, wi.year, wi.value, wi.category
            FROM worldbank_indicators wi
            INNER JOIN (
                SELECT indicator_code, MAX(year) as max_year
                FROM worldbank_indicators
                GROUP BY indicator_code
            ) wm ON wi.indicator_code = wm.indicator_code AND wi.year = wm.max_year
            ORDER BY wi.category, wi.indicator_name
        ''')

        results: Dict[str, List[Dict]] = {}
        for row in cursor.fetchall():
            code, name, year, value, category = row
            if category not in results:
                results[category] = []
            results[category].append({
                "code": code,
                "name": name,
                "year": year,
                "value": float(value) if value is not None else None,
            })

        conn.close()

        return {
            "status": "success",
            "total_indicators": sum(len(v) for v in results.values()),
            "categories": list(results.keys()),
            "data": results,
        }

    except Exception as e:
        return {"status": "error", "message": str(e)}


def get_historical_data(indicator_code: str, years: int = 10) -> Dict:
    """Get historical data for a specific indicator.

    Args:
        indicator_code: World Bank indicator code (e.g. 'NY.GDP.MKTP.CD')
        years: Number of years to fetch.

    Returns:
        Dict with historical values sorted by year descending.
    """
    if not DB_PATH.exists():
        return {"status": "error", "message": "Database not found."}

    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        cursor.execute('''
            SELECT year, value, indicator_name
            FROM worldbank_indicators
            WHERE indicator_code = ?
            ORDER BY year DESC
            LIMIT ?
        ''', (indicator_code, years))

        rows = []
        indicator_name = None
        for row in cursor.fetchall():
            year, value, name = row
            indicator_name = name
            rows.append({
                "year": year,
                "value": float(value) if value is not None else None,
            })

        conn.close()

        return {
            "status": "success",
            "indicator_code": indicator_code,
            "indicator_name": indicator_name,
            "count": len(rows),
            "data": rows,
        }

    except Exception as e:
        return {"status": "error", "message": str(e)}


def get_indicators_list() -> Dict:
    """Get list of all available indicators."""
    if not DB_PATH.exists():
        return {"status": "error", "message": "Database not found."}

    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        cursor.execute('''
            SELECT DISTINCT indicator_code, indicator_name, category
            FROM worldbank_indicators
            ORDER BY category, indicator_name
        ''')

        indicators = []
        for row in cursor.fetchall():
            indicators.append({
                "code": row[0],
                "name": row[1],
                "category": row[2],
            })

        conn.close()
        return {
            "status": "success",
            "count": len(indicators),
            "indicators": indicators,
        }

    except Exception as e:
        return {"status": "error", "message": str(e)}
