# Docker Testing & Deployment Guide

## Testing the Docker Build

### 1. Build the Image

```bash
cd /Users/kabo/Desktop/projects/youtube-transcript/backend

# Build the Docker image
docker build -t gospel-keys-api .

# Check image size (should be ~1.5-2GB with multi-stage)
docker images gospel-keys-api
```

### 2. Run Container Locally

```bash
# Run the container
docker run -d \
  --name gospel-keys-test \
  -p 8000:8000 \
  -v $(pwd)/uploads:/app/uploads \
  -v $(pwd)/outputs:/app/outputs \
  gospel-keys-api

# Check container status
docker ps

# View logs
docker logs -f gospel-keys-test

# Test health endpoint
curl http://localhost:8000/health

# Test API docs
open http://localhost:8000/docs
```

### 3. Test with Docker Compose

```bash
# Start all services (development mode)
docker-compose up -d

# View logs
docker-compose logs -f api

# Test API
curl http://localhost:8000/health/detailed

# Stop services
docker-compose down
```

### 4. Test Production Stack

```bash
# Start production stack with monitoring
docker-compose -f docker-compose.prod.yml up -d

# Check all services are running
docker-compose -f docker-compose.prod.yml ps

# Access services:
# - API: http://localhost:8000/docs
# - Prometheus: http://localhost:9090
# - Grafana: http://localhost:3001 (admin/admin)

# Stop production stack
docker-compose -f docker-compose.prod.yml down
```

## Common Issues

### Issue: ffmpeg not found
**Solution**: ffmpeg is included in the Docker image, no action needed

### Issue: Image too large
**Expected size**: 1.5-2GB (multi-stage build reduces from 3-4GB)
**Check**: Run `docker images gospel-keys-api`

### Issue: Permission denied
**Solution**: Container runs as non-root user (appuser), volumes should be writable
```bash
chmod 777 uploads outputs
```

### Issue: Database locked
**Solution**: SQLite file needs proper permissions
```bash
touch gospel_keys.db
chmod 666 gospel_keys.db
```

## Production Deployment

### Environment Variables

Create production `.env` file:

```env
# Application
APP_NAME=Gospel Keys API
VERSION=2.0.0
CORS_ORIGINS=https://your-frontend.com

# Logging
LOG_LEVEL=INFO

# Monitoring (optional)
PROMETHEUS_ENABLED=true

# Sentry (optional - for error tracking)
SENTRY_DSN=https://your-sentry-dsn@sentry.io/project
SENTRY_ENVIRONMENT=production
```

### Deploy to Cloud

**Docker Hub:**
```bash
# Tag image
docker tag gospel-keys-api your-username/gospel-keys-api:latest

# Push to Docker Hub
docker push your-username/gospel-keys-api:latest
```

**AWS ECS / Google Cloud Run / Azure Container Instances:**
```bash
# Build for platform
docker buildx build --platform linux/amd64 -t gospel-keys-api .

# Follow cloud provider's deployment docs
```

### Health Checks in Production

The Dockerfile includes a built-in health check:
```dockerfile
HEALTHCHECK --interval=30s --timeout=10s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1
```

Kubernetes health probes:
```yaml
livenessProbe:
  httpGet:
    path: /health/live
    port: 8000
  initialDelaySeconds: 40
  periodSeconds: 30

readinessProbe:
  httpGet:
    path: /health/ready
    port: 8000
  initialDelaySeconds: 20
  periodSeconds: 10
```

## Performance Optimization

### GPU Support (for faster transcription)

**Dockerfile.gpu:**
```dockerfile
FROM nvidia/cuda:11.8.0-cudnn8-runtime-ubuntu22.04 as builder
# ... rest of Dockerfile
```

**docker-compose.yml with GPU:**
```yaml
services:
  api:
    deploy:
      resources:
        reservations:
          devices:
            - driver: nvidia
              count: 1
              capabilities: [gpu]
```

**Run with GPU:**
```bash
docker run --gpus all -p 8000:8000 gospel-keys-api
```

## Monitoring & Metrics

### Prometheus Metrics

Available at `http://localhost:9090`:
- `http_requests_total` - Total requests by endpoint
- `http_request_duration_seconds` - Request latency
- `http_request_size_bytes` - Request sizes
- `http_response_size_bytes` - Response sizes

### Grafana Dashboards

Access at `http://localhost:3001`:
1. Login: admin/admin
2. Navigate to Dashboards
3. Import FastAPI dashboard (ID: 16110)

### Custom Metrics (Future)

Add to your FastAPI app:
```python
from prometheus_client import Counter, Histogram

transcription_counter = Counter(
    'transcriptions_total',
    'Total transcriptions',
    ['status', 'source_type']
)

transcription_duration = Histogram(
    'transcription_duration_seconds',
    'Transcription processing time',
    ['stage']
)
```

## Troubleshooting

### View Container Logs
```bash
docker logs gospel-keys-test
docker-compose logs -f api
```

### Execute Commands in Container
```bash
docker exec -it gospel-keys-test /bin/bash
```

### Check Resource Usage
```bash
docker stats gospel-keys-test
```

### Rebuild from Scratch
```bash
docker-compose down -v
docker-compose build --no-cache
docker-compose up -d
```

## Next Steps

1. ✅ Docker containerization complete
2. 🔄 Optional: Add structured logging (structlog)
3. 🔄 Optional: Add Sentry error tracking
4. 🔄 Optional: Add API rate limiting
5. 🔄 Optional: Build frontend React app

---

**Docker setup is complete and ready for testing!** 🎉
