# Grafana Alloy configuration snippets

This repo contains Grafana Alloy `.alloy` configs to collect metrics, logs,
traces, and profiles from a Linux host and ship them to Grafana Cloud. Each
file is a standalone component; combine only what you need. Configs live in
`alloy/`. 

Grafana Alloy is installed using the Grafana Cloud Alloy Onboarding configuration provided by Grafana. You can get the snippet from your Grafana cloud instance:
`https://<username>.grafana.net/a/grafana-collector-app/alloy`


## Environment Variables:
Make sure to udpate the file with the required environment variables at this location: `/etc/systemd/system/alloy.service.d/env.conf`
```
[Service]
Environment=GCLOUD_RW_API_KEY=glc_hc3QtMCJ9fQ==
Environment=GCLOUD_FM_COLLECTOR_ID=<hostname>
Enviornment=LOKI_USERNAME=<YOUR-GRAFANA-CLOUD-LOKI-USERNAME>
Environment=PROMETHEUS_USERNAME=<YOUR-GRAFANA-CLOUD-PROMETHEUS-USERNAME>
Environment=REMOTE_CFG_USERNAME=<YOUR-GRAFANA-CLOUD-REMOTE-CFG-USERNAME>
Environment=TEMPO_USERNAME=<YOUR-GRAFANA-CLOUD-TEMPO-USERNAME>
Environment=PYROSCOPE_USERNAME=<YOUR-GRAFANA-CLOUD-PYROSCOPE-USERNAME>
```

Make sure to change the CONFIG_FILE to point to /etc/alloy directory at the following location `/etc/default/alloy`

```
## Path:
## Description: Grafana Alloy settings
## Type:        string
## Default:     ""
## ServiceRestart: alloy
#
# Command line options for Alloy.
#
# The configuration file holding the Alloy config.
CONFIG_FILE="/etc/alloy/"

# User-defined arguments to pass to the run command.
CUSTOM_ARGS=""

# Restart on system upgrade. Defaults to true.
RESTART_ON_UPGRADE=true
```


Alloy service file: `/usr/lib/systemd/system/alloy.service`

```
[Unit]
Description= Vendor-agnostic OpenTelemetry Collector distribution with programmable pipelines
Documentation=https://grafana.com/docs/alloy
Wants=network-online.target
After=network-online.target

[Service]
Restart=always
User=alloy
Environment=HOSTNAME=%H
Environment=ALLOY_DEPLOY_MODE=deb
EnvironmentFile=/etc/default/alloy
WorkingDirectory=/var/lib/alloy
ExecStart=/usr/bin/alloy run $CUSTOM_ARGS --storage.path=/var/lib/alloy/data $CONFIG_FILE
ExecReload=/usr/bin/env kill -HUP $MAINPID
TimeoutStopSec=20s

[Install]
WantedBy=multi-user.target
```

for some of the stuff to run, you may need to run alloy as the root user, you can make changes in the following file  `/usr/lib/systemd/system/alloy.service` and set the `User=root`

## Contents
- `alloy/01-global-remotecfg.alloy`: remote config and live debugging.
- `alloy/01-global-prometheus.alloy`: Prometheus remote_write and common relabels.
- `alloy/01-global-loki.alloy`: Loki write endpoint.
- `alloy/01-global-otel.alloy`: OTLP exporter and auth for traces.
- `alloy/01-global-pyroscope.alloy`: Pyroscope write endpoint for profiles.
- `alloy/02-system.alloy`: host metrics via `prometheus.exporter.unix`.
- `alloy/03-redis.alloy`: Redis metrics from `localhost:6379`.
- `alloy/04-docker-metrics.alloy`: cAdvisor metrics from the Docker socket.
- `alloy/04a-docker-logs.alloy`: Docker container logs to Loki.
- `alloy/05-traefik.alloy`: Traefik metrics from `localhost:8080`.
- `alloy/06-blackbox.alloy`: HTTP blackbox probes for example URLs.
- `alloy/07-system-logs.alloy`: syslog/auth/kern log files to Loki.
- `alloy/08-journal-logs.alloy`: systemd journal logs to Loki with relabels.
- `alloy/09-ebpf.alloy`: Beyla eBPF traces for a service on port `8002`.
- `alloy/10-receiver.alloy`: OTLP receiver (gRPC `:4317`) for app traces.
- `alloy/11-github.alloy`: GitHub exporter for repository stats.
- `alloy/12-profiling.alloy`: eBPF profiling for all processes.
- `alloy/13-profiling-a-process.alloy`: eBPF profiling for a filtered process.

## Prerequisites
- Grafana Alloy installed on Linux.
- Access to `/var/log` and `/var/run/docker.sock` for the log and Docker configs.
- Optional services: Redis on `localhost:6379`, Traefik metrics on `localhost:8080`.
- eBPF-based configs require root or the right kernel capabilities.
- Environment variables:
  - `GCLOUD_RW_API_KEY` (Grafana Cloud API key)
  - `GITHUB_TOKEN` (for the GitHub exporter)


## Customization notes
- Replace the Grafana Cloud endpoints, instance IDs, and usernames in the
  `alloy/01-global-*.alloy` files with your own.
- Update the blackbox probe URLs and GitHub repositories to match your targets.
- For logs and eBPF profiling, run Alloy with sufficient permissions.

## Troubleshooting
- Permission errors for logs or Docker: run Alloy with the right user/group or
  elevate permissions.
- No data in Grafana: verify `GCLOUD_RW_API_KEY` and the tenant IDs/endpoints.
