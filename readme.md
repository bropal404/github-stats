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

## License

MIT