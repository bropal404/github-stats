# github-stats

A lightweight CGI script that generates a dynamic GitHub stats card as an SVG — dark-themed, self-hosted, and zero-dependency.

<div align="center">

![Stats](/demo.svg)

</div>

---


## Usage

You can set up a GitHub Action to automatically generate the SVG in your repository on a schedule (e.g., every 6 hours).

### 1. Add the GitHub Action workflow

Create a file `.github/workflows/generate-svg.yml` in your repository with the following content:

```yaml
name: Generate GitHub Stats SVG

on:
  schedule:
    - cron: '0 */6 * * *' # Every 6 hours
  workflow_dispatch:      # Allow manual triggering

permissions:
  contents: write

jobs:
  build:
    runs-on: ubuntu-latest

    steps:
      - name: Checkout repository
        uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.10'

      - name: Generate SVG
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
          # You can customize the user and city by setting the QUERY_STRING
          # e.g., QUERY_STRING: "user=torvalds&city=Helsinki"
          QUERY_STRING: "user=YOUR_USERNAME&city=Hyderabad"
        run: |
          # Strip the CGI headers and save the SVG content
          python stats.py | awk '/<svg/{p=1} p' > demo.svg

      - name: Commit and Push
        run: |
          git config --local user.email "github-actions[bot]@users.noreply.github.com"
          git config --local user.name "github-actions[bot]"
          git add demo.svg
          git commit -m "chore: update GitHub stats SVG" || exit 0
          git push
```

### 2. Embed the generated SVG in your README

Once the Action runs and saves `demo.svg` to the root folder, you can embed it in your README like this:

```markdown
![GitHub Stats](./demo.svg)
```

Or centered:

```html
<div align="center">
  <img src="./demo.svg" alt="GitHub Stats" />
</div>
```

---

## License

MIT