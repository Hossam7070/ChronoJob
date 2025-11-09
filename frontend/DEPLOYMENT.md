# ChronoJob Dashboard - Deployment Guide

Complete guide for deploying the ChronoJob dashboard to production.

## Table of Contents

1. [Build Process](#build-process)
2. [Deployment Options](#deployment-options)
3. [Environment Configuration](#environment-configuration)
4. [Production Checklist](#production-checklist)
5. [Monitoring](#monitoring)

## Build Process

### Development Build

For testing the production build locally:

```bash
# Build the application
npm run build

# Preview the build
npm run preview
```

The build output will be in the `dist/` directory.

### Production Build

```bash
# Install dependencies
npm ci --production=false

# Run build
npm run build

# Verify build
ls -la dist/
```

**Build Output:**
- `dist/index.html` - Main HTML file
- `dist/assets/` - JavaScript, CSS, and other assets
- All files are minified and optimized

## Deployment Options

### Option 1: Static File Server (Nginx)

**1. Install Nginx:**
```bash
sudo apt update
sudo apt install nginx
```

**2. Copy build files:**
```bash
sudo cp -r dist/* /var/www/chronojob-dashboard/
```

**3. Configure Nginx:**

Create `/etc/nginx/sites-available/chronojob-dashboard`:

```nginx
server {
    listen 80;
    server_name your-domain.com;
    root /var/www/chronojob-dashboard;
    index index.html;

    # Gzip compression
    gzip on;
    gzip_types text/plain text/css application/json application/javascript text/xml application/xml application/xml+rss text/javascript;

    # Cache static assets
    location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg|woff|woff2|ttf|eot)$ {
        expires 1y;
        add_header Cache-Control "public, immutable";
    }

    # API proxy
    location /api {
        proxy_pass http://localhost:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # SPA fallback
    location / {
        try_files $uri $uri/ /index.html;
    }
}
```

**4. Enable site:**
```bash
sudo ln -s /etc/nginx/sites-available/chronojob-dashboard /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

### Option 2: Docker

**1. Create Dockerfile:**

Create `frontend/Dockerfile`:

```dockerfile
# Build stage
FROM node:18-alpine AS builder

WORKDIR /app

# Copy package files
COPY package*.json ./

# Install dependencies
RUN npm ci

# Copy source code
COPY . .

# Build application
RUN npm run build

# Production stage
FROM nginx:alpine

# Copy custom nginx config
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Copy built files
COPY --from=builder /app/dist /usr/share/nginx/html

# Expose port
EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
```

**2. Create nginx.conf:**

Create `frontend/nginx.conf`:

```nginx
server {
    listen 80;
    server_name localhost;
    root /usr/share/nginx/html;
    index index.html;

    gzip on;
    gzip_types text/plain text/css application/json application/javascript text/xml application/xml application/xml+rss text/javascript;

    location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg|woff|woff2|ttf|eot)$ {
        expires 1y;
        add_header Cache-Control "public, immutable";
    }

    location /api {
        proxy_pass http://backend:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
    }

    location / {
        try_files $uri $uri/ /index.html;
    }
}
```

**3. Build and run:**

```bash
# Build image
docker build -t chronojob-dashboard:latest .

# Run container
docker run -d \
  --name chronojob-dashboard \
  -p 3000:80 \
  --network chronojob-network \
  chronojob-dashboard:latest
```

### Option 3: Docker Compose (Full Stack)

Create `docker-compose.yml` in project root:

```yaml
version: '3.8'

services:
  backend:
    build: .
    container_name: chronojob-backend
    ports:
      - "8000:8000"
    environment:
      - SMTP_SERVER=${SMTP_SERVER}
      - SMTP_PORT=${SMTP_PORT}
      - SMTP_USERNAME=${SMTP_USERNAME}
      - SMTP_PASSWORD=${SMTP_PASSWORD}
      - SENDER_EMAIL=${SENDER_EMAIL}
    volumes:
      - ./data:/app/data
    restart: unless-stopped

  frontend:
    build: ./frontend
    container_name: chronojob-dashboard
    ports:
      - "80:80"
    depends_on:
      - backend
    restart: unless-stopped

networks:
  default:
    name: chronojob-network
```

**Deploy:**
```bash
docker-compose up -d
```

### Option 4: Vercel

**1. Install Vercel CLI:**
```bash
npm install -g vercel
```

**2. Configure vercel.json:**

Create `frontend/vercel.json`:

```json
{
  "rewrites": [
    {
      "source": "/api/:path*",
      "destination": "https://your-backend-url.com/api/:path*"
    },
    {
      "source": "/(.*)",
      "destination": "/index.html"
    }
  ],
  "headers": [
    {
      "source": "/assets/(.*)",
      "headers": [
        {
          "key": "Cache-Control",
          "value": "public, max-age=31536000, immutable"
        }
      ]
    }
  ]
}
```

**3. Deploy:**
```bash
cd frontend
vercel --prod
```

### Option 5: Netlify

**1. Create netlify.toml:**

Create `frontend/netlify.toml`:

```toml
[build]
  command = "npm run build"
  publish = "dist"

[[redirects]]
  from = "/api/*"
  to = "https://your-backend-url.com/api/:splat"
  status = 200

[[redirects]]
  from = "/*"
  to = "/index.html"
  status = 200

[[headers]]
  for = "/assets/*"
  [headers.values]
    Cache-Control = "public, max-age=31536000, immutable"
```

**2. Deploy:**
```bash
# Install Netlify CLI
npm install -g netlify-cli

# Deploy
cd frontend
netlify deploy --prod
```

## Environment Configuration

### Backend URL Configuration

Update the API proxy target based on your deployment:

**Development:**
```typescript
// vite.config.ts
proxy: {
  '/api': {
    target: 'http://localhost:8000',
    changeOrigin: true,
  },
}
```

**Production (Nginx/Docker):**
- Configure in nginx.conf or docker-compose.yml
- No changes needed in application code

**Production (Vercel/Netlify):**
- Configure in vercel.json or netlify.toml
- Update rewrite rules with production backend URL

### Environment Variables

Create `.env.production` if needed:

```env
VITE_API_URL=https://api.your-domain.com
```

Update `vite.config.ts`:

```typescript
export default defineConfig({
  // ...
  define: {
    'import.meta.env.VITE_API_URL': JSON.stringify(process.env.VITE_API_URL),
  },
})
```

## Production Checklist

### Pre-Deployment

- [ ] Run `npm run build` successfully
- [ ] Test production build locally with `npm run preview`
- [ ] Verify all API endpoints work
- [ ] Check browser console for errors
- [ ] Test on multiple browsers
- [ ] Test responsive design on mobile devices
- [ ] Verify all forms and validations work
- [ ] Test job creation and deletion
- [ ] Check error handling

### Security

- [ ] Enable HTTPS (SSL/TLS certificate)
- [ ] Configure CORS on backend
- [ ] Set secure headers (CSP, X-Frame-Options, etc.)
- [ ] Implement rate limiting on backend
- [ ] Validate all user inputs
- [ ] Sanitize data before display
- [ ] Use environment variables for sensitive data

### Performance

- [ ] Enable gzip compression
- [ ] Configure asset caching
- [ ] Optimize images
- [ ] Minimize bundle size
- [ ] Enable CDN if available
- [ ] Configure proper cache headers

### Monitoring

- [ ] Set up error tracking (Sentry, etc.)
- [ ] Configure analytics (Google Analytics, etc.)
- [ ] Set up uptime monitoring
- [ ] Configure log aggregation
- [ ] Set up alerts for errors

## SSL/TLS Configuration

### Using Let's Encrypt with Nginx

**1. Install Certbot:**
```bash
sudo apt install certbot python3-certbot-nginx
```

**2. Obtain certificate:**
```bash
sudo certbot --nginx -d your-domain.com
```

**3. Auto-renewal:**
```bash
sudo certbot renew --dry-run
```

### Using Cloudflare

1. Add your domain to Cloudflare
2. Update nameservers
3. Enable "Full (strict)" SSL mode
4. Configure page rules for caching

## Monitoring

### Application Monitoring

**Sentry Integration:**

```bash
npm install @sentry/react
```

Update `main.tsx`:

```typescript
import * as Sentry from "@sentry/react";

Sentry.init({
  dsn: "your-sentry-dsn",
  environment: "production",
  tracesSampleRate: 1.0,
});
```

### Uptime Monitoring

Use services like:
- UptimeRobot
- Pingdom
- StatusCake
- Better Uptime

### Log Monitoring

Configure nginx access and error logs:

```nginx
access_log /var/log/nginx/chronojob-access.log;
error_log /var/log/nginx/chronojob-error.log;
```

## Backup and Recovery

### Backup Strategy

**What to backup:**
- Backend job configurations
- Database (if applicable)
- Environment variables
- SSL certificates

**Automated backups:**
```bash
# Create backup script
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
tar -czf /backups/chronojob-$DATE.tar.gz /var/www/chronojob-dashboard
```

### Recovery

**Restore from backup:**
```bash
tar -xzf /backups/chronojob-20240101_120000.tar.gz -C /var/www/
sudo systemctl reload nginx
```

## Scaling

### Horizontal Scaling

Use a load balancer (nginx, HAProxy) to distribute traffic:

```nginx
upstream chronojob_backend {
    server backend1:8000;
    server backend2:8000;
    server backend3:8000;
}

server {
    location /api {
        proxy_pass http://chronojob_backend;
    }
}
```

### CDN Integration

Use CDN for static assets:
- Cloudflare
- AWS CloudFront
- Fastly
- Akamai

## Troubleshooting

### Build Failures

**Issue:** Build fails with memory error
**Solution:** Increase Node memory
```bash
NODE_OPTIONS=--max-old-space-size=4096 npm run build
```

### API Connection Issues

**Issue:** Frontend can't connect to backend
**Solution:** Check proxy configuration and CORS settings

### Performance Issues

**Issue:** Slow page loads
**Solution:** 
- Enable gzip compression
- Configure caching
- Use CDN
- Optimize bundle size

## Support

For deployment issues:
1. Check build logs
2. Verify nginx/server configuration
3. Check browser console
4. Review backend logs
5. Test API endpoints directly

---

**Happy Deploying!** 🚀
