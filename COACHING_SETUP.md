# AI Trading Coach Setup

This guide explains how to set up and use the AI Trading Coach feature in the PropReports Trading Dashboard.

## Overview

The AI Trading Coach provides automated performance analysis using OpenAI's GPT-4 to help improve your trading performance. It generates:

- **Monthly Reports**: Comprehensive analysis on the 2nd day of each month
- **Weekly Reports**: Tactical feedback every Monday

## Setup Instructions

### 1. Configure GitHub Secrets

You need to set the following secrets in your dashboard repository:

1. Go to your GitHub repository settings
2. Navigate to Settings → Secrets and variables → Actions
3. Add these repository secrets:

```bash
OPENAI_API_KEY=sk-your-api-key-here
ENABLE_COACHING=true
```

### 2. Enable GitHub Actions

The coaching workflows are already configured in `.github/workflows/`:
- `monthly-coaching.yml` - Runs on the 2nd of each month
- `weekly-coaching.yml` - Runs every Monday

These will automatically pull data from your exporter repository and generate coaching reports.

### 3. Manual Execution

You can manually trigger coaching reports:

1. Go to Actions tab in your GitHub repository
2. Select either "Monthly Trading Coaching Report" or "Weekly Trading Coaching Report"
3. Click "Run workflow"
4. Optionally specify year/month/week or leave blank for auto-detection

## How It Works

1. **Data Collection**: The workflows pull trading data from the exporter repository
2. **AI Analysis**: GPT-4 analyzes your performance metrics and patterns
3. **Report Generation**: Structured coaching reports are generated
4. **Dashboard Update**: Reports are integrated into your dashboard
5. **GitHub Issue**: A summary is posted as a GitHub issue for easy tracking

## Report Contents

### Monthly Reports Include:
- Overall performance assessment
- Key strengths demonstrated
- Areas for improvement
- Risk management observations
- Psychological insights
- Specific recommendations for next month

### Weekly Reports Include:
- Week performance summary
- Daily breakdown analysis
- Trading pattern insights
- Tactical adjustments
- Focus areas for next week

## Cost Considerations

- Uses OpenAI's GPT-4o-mini model (cost-efficient)
- Monthly report: ~$0.01-0.02 per report
- Weekly report: ~$0.005-0.01 per report
- Estimated monthly cost: < $0.10 with regular usage

## Troubleshooting

### Coaching Not Running?
1. Check if `ENABLE_COACHING` secret is set to `true`
2. Verify `OPENAI_API_KEY` is correctly configured
3. Ensure the exporter repository has data for the period

### No Reports Showing?
1. Check GitHub Actions logs for errors
2. Verify data exists in the exporter repository
3. Check if dashboard-data.json includes coaching section

## Privacy & Security

- OpenAI API calls include only aggregated performance metrics
- No personal information or account details are sent
- All data remains within your GitHub repositories