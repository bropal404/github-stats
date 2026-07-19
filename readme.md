# github-stats

A lightweight CGI script that generates a dynamic GitHub stats card as an SVG — dark-themed, self-hosted, and zero-dependency.

<div align="center">

![Stats](/demo.svg)

</div>

---


## Usage

### Option A — Embed in your README (use my hosted instance)

```markdown
![GitHub Stats](https://researchweb.iiit.ac.in/~gopal.kataria/cgi-bin/stats.py?user=YOUR_USERNAME)
```

Or centered:

```html
<div align="center">

![GitHub Stats](https://researchweb.iiit.ac.in/~gopal.kataria/cgi-bin/stats.py?user=YOUR_USERNAME)

</div>
```

---

### Weather option

The script now supports an optional `city` query parameter which fetches a small current-weather summary (temperature, short description and a glyph) from wttr.in and displays it on the card. The default city is `Hyderabad`.

Examples:

Embed with a city (London):

```markdown
![GitHub Stats](https://researchweb.iiit.ac.in/~gopal.kataria/cgi-bin/stats.py?user=YOUR_USERNAME&city=London)
```

Or centered HTML embed with a city (San Francisco):

```html
<div align="center">

![GitHub Stats](https://researchweb.iiit.ac.in/~gopal.kataria/cgi-bin/stats.py?user=YOUR_USERNAME&city=San%20Francisco)

</div>
```

---

### Option B — Self-host on `web.iiit.ac.in` / `researchweb.iiit.ac.in`

#### 1. SSH into your server

```bash
# Research students
ssh username@researchweb.iiit.ac.in

# UG/PG students
ssh username@web.iiit.ac.in
```

> See [docs.iiit.ac.in](https://docs.iiit.ac.in) for CGI setup instructions.

#### 2. Place the script

```bash
cp stats.py ~/public_html/cgi-bin/stats.py
chmod +x ~/public_html/cgi-bin/stats.py
```

#### 3. (Optional) Set a GitHub token to avoid rate limits

```bash
export GITHUB_TOKEN=ghp_your_token_here
```

#### 4. Embed in your README

```markdown
![GitHub Stats](https://researchweb.iiit.ac.in/~YOUR_USERNAME/cgi-bin/stats.py?user=YOUR_GITHUB_USERNAME)
```

---

### Option C — Run via GitHub Actions (Generate and save SVG automatically)

You can set up a GitHub Action to automatically generate the SVG in your repository on a schedule (e.g., every 6 hours).

#### 1. Add the GitHub Action workflow

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

#### 2. Embed the generated SVG in your README

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