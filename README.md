# SRE Observability Stack

A production-style observability setup running on Kubernetes, built to demonstrate SRE principles including SLO tracking, metrics collection, and automated alerting.

<img width="1592" height="839" alt="image" src="https://github.com/user-attachments/assets/a0ca8a34-e4cc-4ba3-b627-d346c18da3d0" />


## The app
 
`app.py` is a Flask HTTP service that simulates realistic traffic patterns:
 
- 95% of requests return HTTP 200
- 5% of requests return HTTP 500
- Response latency is randomized between 0 and 500ms
It tracks two metrics using `prometheus_client`:
 
- `app_requests_total` — counter, labeled by method, endpoint, and status code
- `app_request_latency_seconds` — histogram of response times
## SLOs
 
| Signal | Target |
|--------|--------|
| Request success rate | >= 99% |
| P95 latency | <= 200ms |
 
## Grafana dashboard panels
 
| Panel | Query |
|-------|-------|
| Request Success Rate | `sum(rate(app_requests_total{status="200"}[5m])) / sum(rate(app_requests_total[5m])) * 100` |
| Requests Per Second | `sum(rate(app_requests_total[5m]))` |
| Error Rate | `sum(rate(app_requests_total{status="500"}[5m])) / sum(rate(app_requests_total[5m])) * 100` |
| P95 Latency | `histogram_quantile(0.95, sum(rate(app_request_latency_seconds_bucket[5m])) by (le))` |
 
## Running
 
 
Start k3s and export the kubeconfig:
 
```bash
sudo systemctl start k3s
export KUBECONFIG=/etc/rancher/k3s/k3s.yaml
```
 
Build the image and import it into k3s's container runtime:
 
```bash
sudo docker build -t sre-app:latest .
sudo docker save sre-app:latest | sudo k3s ctr images import -
```
 
k3s uses containerd internally, not the local Docker daemon, so the import step is required.
 
Deploy the app:
 
```bash
sudo kubectl apply -f deployment.yaml
```
 
Get the cluster IP:
 
```bash
sudo kubectl get svc sre-app -n monitoring
```
 
Generate traffic in a separate terminal:
 
```bash
while true; do curl -s http://<CLUSTER-IP>:5000/ > /dev/null; sleep 0.5; done
```
 
Get the Grafana admin password:
 
```bash
sudo kubectl get secret --namespace monitoring grafana \
  -o jsonpath="{.data.admin-password}" | base64 --decode; echo
```
 
Forward the Grafana port:
 
```bash
sudo kubectl port-forward --namespace monitoring svc/grafana 3000:80
```
 
Open `http://localhost:3000` and log in with username `admin` and the password from above.
 
## Grafana setup
 
Add Prometheus as a data source:
 
1. Go to Connections > Data sources > Add data source
2. Select Prometheus
3. Set the URL to `http://prometheus-server.monitoring.svc.cluster.local`
4. Click Save and test
Create a new dashboard and add four panels using the queries from the table above. Set the time range to Last 5 minutes.
 
## Alerting setup
 
1. Go to Alerting > Alert rules > New alert rule
2. Use the success rate query, set condition to fire when below 99
3. Evaluation interval: 1 minute, pending period: 2 minutes
4. Go to Alerting > Contact points and add your webhook URL
5. Set it as the default in Alerting > Notification policies
The 2-minute pending period prevents the alert from firing on momentary dips.
 
## Project structure
 
```
sre-app/
  app.py            Flask app with Prometheus instrumentation
  requirements.txt
  Dockerfile
  deployment.yaml   Kubernetes Deployment and Service
```
 
