# SRE Observability Stack

A production-style observability setup running on Kubernetes, built to demonstrate SRE principles including SLO tracking, metrics collection, and automated alerting.

## Architecture

Flask App → Prometheus (scrape /metrics) → Grafana (dashboards + alerts) → Webhook (notifications)
TODO: add architecture diagrram
￼
## Stack

- **Kubernetes** (k3s) — container orchestration
- **Prometheus** — metrics collection and storage
- **Grafana** — dashboards and alerting
- **Flask + prometheus_client** — instrumented Python app

## The App

A Flask HTTP service that simulates real traffic patterns:
- 95% success rate (HTTP 200)
- 5% error rate (HTTP 500)
- Random latency between 0-500ms

Exposes a `/metrics` endpoint in Prometheus format.

## SLOs Defined

| Metric | Target |
|--------|--------|
| Request Success Rate | ≥ 99% |
| P95 Latency | ≤ 200ms |

## Dashboards

- **Request Success Rate** — tracked against 99% SLO
- **Requests Per Second** — real-time request rate
- **Error Rate** — percentage of 500 responses
- **P95 Latency** — 95th percentile response time

## Alerting

Grafana alert fires when success rate drops below 99% for more than 2 minutes, notifying via webhook. Pending period prevents noisy false positives.

## Running Locally

### Prerequisites
- k3s
- Helm
- Docker

### Deploy

```bash
# Deploy the app
kubectl apply -f deployment.yaml

# Install Prometheus
helm install prometheus prometheus-community/prometheus --namespace monitoring --create-namespace

# Install Grafana
helm install grafana grafana/grafana --namespace monitoring
```

## Key SRE Concepts Demonstrated

- **SLI/SLO definition and tracking** — measurable reliability targets
- **Golden signals monitoring** — latency, traffic, errors
- **Alerting with noise reduction** — pending periods to avoid false positives
- **Kubernetes-native service discovery** — Prometheus scrapes pods via annotations
