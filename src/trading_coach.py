#!/usr/bin/env python3
"""
Trading Coach - AI-powered trading performance analysis using OpenAI GPT-4
"""

import json
import os
import sys
import argparse
import requests
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple

class TradingCoach:
    def __init__(self, api_key: str, export_dir: str = "exports"):
        self.api_key = api_key
        self.export_dir = Path(export_dir)
        self.base_url = "https://api.openai.com/v1/chat/completions"
        
    def _call_openai(self, prompt: str, model: str = "gpt-4o-mini") -> str:
        """Make a call to OpenAI API"""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        data = {
            "model": model,
            "messages": [
                {
                    "role": "system",
                    "content": "You are an expert trading coach analyzing performance data. Provide specific, actionable insights in a structured format. Be encouraging but honest about areas needing improvement."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "temperature": 0.7,
            "max_tokens": 1000
        }
        
        try:
            response = requests.post(self.base_url, headers=headers, json=data)
            response.raise_for_status()
            return response.json()['choices'][0]['message']['content']
        except Exception as e:
            print(f"Error calling OpenAI API: {e}")
            return None
    
    def _format_coaching_response(self, raw_response: str) -> Dict:
        """Format the coaching response into structured data"""
        # Default structure
        coaching = {
            "overall_performance": "",
            "strengths": [],
            "areas_for_improvement": [],
            "specific_recommendations": [],
            "risk_management": "",
            "psychological_insights": "",
            "next_week_focus": [],
            "next_month_focus": []
        }
        
        if not raw_response:
            return coaching
            
        # Parse sections from response
        sections = raw_response.split('\n\n')
        current_section = None
        
        for section in sections:
            section = section.strip()
            if not section:
                continue
                
            # Identify section headers
            if "Overall Performance" in section or "General Assessment" in section:
                coaching["overall_performance"] = section.split(':', 1)[-1].strip()
            elif "Strengths" in section:
                current_section = "strengths"
            elif "Areas for Improvement" in section or "Weaknesses" in section:
                current_section = "areas_for_improvement"
            elif "Recommendations" in section:
                current_section = "specific_recommendations"
            elif "Risk Management" in section:
                coaching["risk_management"] = section.split(':', 1)[-1].strip()
            elif "Psychological" in section or "Mental" in section:
                coaching["psychological_insights"] = section.split(':', 1)[-1].strip()
            elif "Next Week" in section:
                current_section = "next_week_focus"
            elif "Next Month" in section:
                current_section = "next_month_focus"
            else:
                # Add to current section if it's a list item
                if current_section and section.startswith(('-', '*', '•', '1.', '2.', '3.')):
                    item = section.lstrip('-*•1234567890. ').strip()
                    if current_section in coaching and isinstance(coaching[current_section], list):
                        coaching[current_section].append(item)
        
        return coaching
    
    def analyze_monthly_performance(self, year: int, month: int) -> Optional[Dict]:
        """Analyze monthly trading performance"""
        # Load monthly summary
        monthly_file = self.export_dir / f"monthly/{year}-{month:02d}.json"
        if not monthly_file.exists():
            print(f"Monthly summary not found: {monthly_file}")
            return None
            
        with open(monthly_file, 'r') as f:
            monthly_data = json.load(f)
        
        # Create prompt with key metrics
        overview = monthly_data['overview']
        analysis = monthly_data.get('performanceAnalysis', {})
        
        prompt = f"""
Analyze the following monthly trading performance for {monthly_data['monthName']} {year}:

OVERVIEW:
- Total Trades: {overview['totalTrades']}
- Net P&L: ${overview['netPnL']}
- Win Rate: {overview['winRate']*100:.1f}%
- Profit Factor: {overview.get('profitFactor', 0):.2f}
- Average Win: ${overview.get('avgWin', 0):.2f}
- Average Loss: ${overview.get('avgLoss', 0):.2f}
- Trading Days: {overview['totalTradingDays']}

PERFORMANCE DETAILS:
- Max Drawdown: ${analysis.get('drawdown_analysis', {}).get('max_drawdown', 0):.2f} ({analysis.get('drawdown_analysis', {}).get('max_drawdown_percent', 0):.1f}%)
- Sharpe Ratio: {analysis.get('risk_metrics', {}).get('sharpe_ratio', 0):.2f}
- Max Consecutive Losses: {analysis.get('risk_metrics', {}).get('max_consecutive_losses', 0)}
- Profitable Days: {analysis.get('consistency_metrics', {}).get('profitable_days', 0)} ({analysis.get('consistency_metrics', {}).get('win_rate_days', 0)*100:.1f}%)

SYMBOL PERFORMANCE:
"""
        
        # Add top performing and worst performing symbols
        symbol_perf = analysis.get('symbol_performance', {})
        if symbol_perf:
            sorted_symbols = sorted(symbol_perf.items(), key=lambda x: x[1].get('pnl', 0), reverse=True)
            
            prompt += "Top 3 Winners:\n"
            for symbol, stats in sorted_symbols[:3]:
                prompt += f"- {symbol}: ${stats['pnl']:.2f} ({stats['trades']} trades, {stats['win_rate']*100:.0f}% win rate)\n"
            
            prompt += "\nTop 3 Losers:\n"
            for symbol, stats in sorted_symbols[-3:]:
                if stats['pnl'] < 0:
                    prompt += f"- {symbol}: ${stats['pnl']:.2f} ({stats['trades']} trades, {stats['win_rate']*100:.0f}% win rate)\n"
        
        prompt += """
Please provide:
1. Overall performance assessment
2. Key strengths demonstrated this month
3. Specific areas for improvement
4. Actionable recommendations for next month
5. Risk management observations and suggestions
6. Psychological insights based on the trading patterns
7. Top 3 focus areas for next month

Format the response with clear sections and bullet points where appropriate.
"""
        
        # Get AI analysis
        raw_response = self._call_openai(prompt)
        if not raw_response:
            return None
            
        # Format and save the coaching report
        coaching = self._format_coaching_response(raw_response)
        
        report = {
            "period": f"{monthly_data['monthName']} {year}",
            "generated_at": datetime.now().isoformat(),
            "performance_summary": {
                "net_pnl": overview['netPnL'],
                "total_trades": overview['totalTrades'],
                "win_rate": overview['winRate'],
                "profit_factor": overview.get('profitFactor', 0)
            },
            "coaching": coaching
        }
        
        # Save the report
        coaching_dir = self.export_dir / "coaching/monthly"
        coaching_dir.mkdir(parents=True, exist_ok=True)
        
        report_file = coaching_dir / f"{year}-{month:02d}.json"
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)
        
        print(f"✅ Monthly coaching report saved: {report_file}")
        return report
    
    def analyze_weekly_performance(self, year: int, week: int) -> Optional[Dict]:
        """Analyze weekly trading performance"""
        # Load weekly summary
        weekly_file = self.export_dir / f"weekly/{year}-W{week:02d}.json"
        if not weekly_file.exists():
            print(f"Weekly summary not found: {weekly_file}")
            return None
            
        with open(weekly_file, 'r') as f:
            weekly_data = json.load(f)
        
        # Create prompt with key metrics
        summary = weekly_data['summary']
        patterns = weekly_data.get('tradingPatterns', {})
        
        prompt = f"""
Analyze the following weekly trading performance for Week {week}, {year} ({weekly_data['weekPeriod']}):

WEEK OVERVIEW:
- Total Trades: {summary.get('totalTrades', 0)}
- Net P&L: ${summary.get('netPnL', 0)}
- Win Rate: {summary.get('winRate', 0)*100:.1f}%
- Trading Days: {summary.get('tradingDays', 'N/A')}
- Average Trades/Day: {summary.get('avgTradesPerDay', 0):.1f}

DAILY BREAKDOWN:
"""
        
        # Add extremes info if available
        extremes = weekly_data.get('extremes', {})
        if extremes:
            best_trade = extremes.get('bestTrade', {})
            worst_trade = extremes.get('worstTrade', {})
            if best_trade:
                prompt += f"- Best Trade: ${best_trade.get('pnl', 0):.2f} ({best_trade.get('symbol', 'N/A')} on {best_trade.get('date', 'N/A')})\n"
            if worst_trade:
                prompt += f"- Worst Trade: ${worst_trade.get('pnl', 0):.2f} ({worst_trade.get('symbol', 'N/A')} on {worst_trade.get('date', 'N/A')})\n"
        
        prompt += f"""
TRADING PATTERNS:
- Max Consecutive Wins: {patterns.get('maxConsecutiveWins', 'N/A')}
- Max Consecutive Losses: {patterns.get('maxConsecutiveLosses', 'N/A')}

Please provide:
1. Overall weekly performance assessment
2. Key strengths shown this week
3. Specific mistakes or areas to improve
4. Tactical adjustments for next week
5. Risk management observations
6. Psychological/discipline observations
7. Top 3 focus areas for next week

Keep the response concise but actionable.
"""
        
        # Get AI analysis
        raw_response = self._call_openai(prompt)
        if not raw_response:
            return None
            
        # Format and save the coaching report
        coaching = self._format_coaching_response(raw_response)
        
        report = {
            "period": f"Week {week}, {year}",
            "week_period": weekly_data['weekPeriod'],
            "generated_at": datetime.now().isoformat(),
            "performance_summary": {
                "net_pnl": summary['netPnL'],
                "total_trades": summary['totalTrades'],
                "win_rate": summary['winRate'],
                "trading_days": summary['tradingDays']
            },
            "coaching": coaching
        }
        
        # Save the report
        coaching_dir = self.export_dir / "coaching/weekly"
        coaching_dir.mkdir(parents=True, exist_ok=True)
        
        report_file = coaching_dir / f"{year}-W{week:02d}.json"
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)
        
        print(f"✅ Weekly coaching report saved: {report_file}")
        return report

def main():
    parser = argparse.ArgumentParser(description='AI Trading Coach')
    parser.add_argument('type', choices=['monthly', 'weekly'], help='Type of analysis')
    parser.add_argument('--year', type=int, help='Year (default: current)')
    parser.add_argument('--month', type=int, help='Month for monthly analysis')
    parser.add_argument('--week', type=int, help='Week number for weekly analysis')
    parser.add_argument('--auto', action='store_true', help='Auto-detect period based on current date')
    
    args = parser.parse_args()
    
    # Get API key from environment
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        print("Error: OPENAI_API_KEY environment variable not set")
        sys.exit(1)
    
    # Get export directory
    export_dir = os.getenv('EXPORT_OUTPUT_DIR', 'exports')
    
    # Initialize coach
    coach = TradingCoach(api_key, export_dir)
    
    # Determine period to analyze
    now = datetime.now()
    
    if args.type == 'monthly':
        if args.auto:
            # For monthly, analyze the previous month on day 2 or later
            if now.day >= 2:
                target_date = now - timedelta(days=now.day)
                year = target_date.year
                month = target_date.month
            else:
                print("Too early in the month for auto monthly analysis")
                sys.exit(0)
        else:
            year = args.year or now.year
            month = args.month
            if not month:
                print("Error: --month required for monthly analysis (or use --auto)")
                sys.exit(1)
        
        print(f"Analyzing monthly performance: {year}-{month:02d}")
        result = coach.analyze_monthly_performance(year, month)
        
    else:  # weekly
        if args.auto:
            # For weekly, analyze the previous week on Monday
            if now.weekday() == 0:  # Monday
                target_date = now - timedelta(days=7)
                year = target_date.year
                week = target_date.isocalendar()[1]
            else:
                print("Auto weekly analysis only runs on Mondays")
                sys.exit(0)
        else:
            year = args.year or now.year
            week = args.week
            if not week:
                print("Error: --week required for weekly analysis (or use --auto)")
                sys.exit(1)
        
        print(f"Analyzing weekly performance: {year}-W{week:02d}")
        result = coach.analyze_weekly_performance(year, week)
    
    if result:
        print(f"✨ Coaching analysis complete!")
        print(f"Performance: ${result['performance_summary']['net_pnl']:.2f} "
              f"({result['performance_summary']['win_rate']*100:.1f}% win rate)")
    else:
        print("❌ Failed to generate coaching report")
        sys.exit(1)

if __name__ == "__main__":
    main()