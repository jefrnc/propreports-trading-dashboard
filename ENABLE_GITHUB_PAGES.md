# Enable GitHub Pages

To enable GitHub Pages for this repository:

1. Go to your repository on GitHub
2. Click on **Settings** tab
3. Scroll down to **Pages** section in the left sidebar
4. Under **Source**, select **GitHub Actions**
5. Save the changes

The dashboard will be available at:
```
https://[your-username].github.io/[repository-name]/
```

For example:
```
https://jefrnc.github.io/test-propreports-export/
```

The workflow will automatically deploy updates to GitHub Pages whenever:
- New trading data is exported
- Statistics are updated
- You manually trigger the workflow

## Manual Trigger

To manually update the dashboard:
1. Go to Actions tab
2. Select "Update Trading Statistics" workflow
3. Click "Run workflow"
4. Select the branch and click "Run workflow"

The dashboard will be updated within a few minutes.