# Publish to GitHub

```bash
cd cloudcart-sentinel
git init
git add .
git commit -m "feat: launch CloudCart Sentinel reliability platform"
git branch -M main
git remote add origin https://github.com/YOUR-USERNAME/cloudcart-sentinel.git
git push -u origin main
```

## Recommended repository settings

- Description: `Production-style e-commerce reliability platform using FastAPI, PostgreSQL, Redis, Prometheus, Docker, Terraform, and AWS.`
- Topics: `fastapi`, `aws`, `terraform`, `postgresql`, `redis`, `prometheus`, `grafana`, `devops`, `sre`, `ecommerce`, `linux`
- Enable Issues and Discussions.
- Protect `main`: require CI, one approval, and resolved conversations.
- Add `JWT_SECRET`, `ADMIN_PASSWORD`, and AWS credentials only as encrypted GitHub Actions secrets.

## Suggested first release

Tag `v1.0.0` after CI passes and attach the architecture screenshot or a short demo GIF to the release and README.
