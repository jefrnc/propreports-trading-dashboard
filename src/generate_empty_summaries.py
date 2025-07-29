#!/usr/bin/env python3
"""
Generate empty monthly summaries for months without trading data
"""

import json
import os
from pathlib import Path
from datetime import datetime

def generate_empty_monthly_summary(year, month, export_dir="exports"):
    """Generate empty monthly summary for months without trades"""
    
    month_names = ["", "January", "February", "March", "April", "May", "June",
                   "July", "August", "September", "October", "November", "December"]
    
    summary = {
        "generateDate": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "month": month,
        "monthName": month_names[month],
        "year": year,
        "account": "N/A",
        "overview": {
            "totalTradingDays": 0,
            "totalTrades": 0,
            "grossPnL": 0.0,
            "totalCommissions": 0.0,
            "netPnL": 0.0,
            "avgDailyPnL": 0.0,
            "avgTradePerDay": 0.0,
            "winningTrades": 0,
            "losingTrades": 0,
            "winRate": 0.0,
            "avgWin": 0.0,
            "avgLoss": 0.0,
            "profitFactor": 0.0
        },
        "extremes": {
            "bestTrade": None,
            "worstTrade": None,
            "bestDay": None,
            "worstDay": None
        },
        "dailyBreakdown": [],
        "symbolPerformance": {},
        "performanceAnalysis": {
            "risk_metrics": {
                "sharpe_ratio": 0.0,
                "max_consecutive_wins": 0,
                "max_consecutive_losses": 0
            },
            "drawdown_analysis": {
                "max_drawdown": 0.0,
                "max_drawdown_percent": 0.0
            }
        },
        "summary": f"No trading activity in {month_names[month]} {year}"
    }
    
    # Create directory if it doesn't exist
    monthly_dir = Path(export_dir) / "monthly"
    monthly_dir.mkdir(parents=True, exist_ok=True)
    
    # Save JSON file
    json_file = monthly_dir / f"{year}-{month:02d}.json"
    with open(json_file, 'w') as f:
        json.dump(summary, f, indent=2)
    
    # Save text summary
    txt_file = monthly_dir / f"{year}-{month:02d}.txt"
    with open(txt_file, 'w') as f:
        f.write(f"MONTHLY SUMMARY - {month_names[month]} {year}\n")
        f.write("=" * 50 + "\n\n")
        f.write("No trading activity recorded for this month.\n")
    
    print(f"✅ Generated empty summary for {month_names[month]} {year}")
    return json_file

def main():
    # Generate for April 2025 (and any other months without data)
    generate_empty_monthly_summary(2025, 4)
    
    # Also check for other months that might need empty summaries
    months_to_check = [1, 2, 3, 4]  # January through April
    for month in months_to_check:
        monthly_file = Path("exports/monthly") / f"2025-{month:02d}.json"
        if not monthly_file.exists():
            generate_empty_monthly_summary(2025, month)

if __name__ == "__main__":
    main()