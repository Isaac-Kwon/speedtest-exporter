
# Requirement

## python package

* Flask>=2.1.0
* prometheus_client>=0.14.1

## other app

* speedtest-cli

# input-output

## HTTP Request Input

| name       | type   | decription                                        | note     |
|:----------:|:------:|:-------------------------------------------------:|:--------:|
| id         | string | speedtest server id                               | optional |
| host       | string | speedtest server hostname                         | optional |
| interface  | string | interface(client-side) using for speedtest        | optional |
| ip         | string | ip of interface(client-side) using for speedtest  | optional |

## Metrics

```url
   /metrics/
```

| metric name                      | type   | unit     | note                      |
|:--------------------------------:|:------:|:--------:|:-------------------------:|
| speedtest-jitter-seconds         | float  | seconds  |                           |
| speedtest-latency-seconds        | float  | seconds  |                           |
| speedtest-bandwidth-bytesseconds | float  | byte/sec | type="download or upload" |
| speedtest-byte                   | int    | byte     | type="download or upload" |
| speedtest-time                   | int    | seconds  | type="download or upload" |
| speedtest-isp                    | string |          |                           |
| speedtest-interface              | string |          |                           |
| speedtest-server                 | int    |          |                           |

## Other Method

```url
   /servers/
```
