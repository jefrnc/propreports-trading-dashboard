#!/usr/bin/env python3
"""
Script to add coaching section to dashboard-data.json
"""

import json
import os

def main():
    # Load existing dashboard data
    dashboard_file = 'docs/dashboard-data.json'
    
    with open(dashboard_file, 'r') as f:
        data = json.load(f)
    
    # Add coaching section if not exists
    if 'coaching' not in data:
        data['coaching'] = {
            'monthly': [],
            'weekly': [],
            'enabled': True
        }
    
    # Save updated data
    with open(dashboard_file, 'w') as f:
        json.dump(data, f, indent=2)
    
    print(f"✅ Updated {dashboard_file} with coaching section")

if __name__ == "__main__":
    main()