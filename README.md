# Client Throttler

[![license](https://img.shields.io/badge/license-MIT-brightgreen.svg?style=flat)](https://github.com/OVINC-CN/ClientThrottler/blob/main/LICENSE)
[![Release Version](https://img.shields.io/badge/release-1.1.0-brightgreen.svg)](https://github.com/OVINC-CN/ClientThrottler/releases)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](https://github.com/OVINC-CN/ClientThrottler/pulls)
[![Unittest](https://github.com/OVINC-CN/ClientThrottler/actions/workflows/test.yml/badge.svg)](https://github.com/OVINC-CN/ClientThrottler/actions/workflows/test.yml)
[![codecov](https://codecov.io/github/OVINC-CN/ClientThrottler/graph/badge.svg?token=X3M2H1E59O)](https://codecov.io/github/OVINC-CN/ClientThrottler)

## Overview

A proactive rate-limiting tool utilizing Redis.

Users can actively limit the call frequency of functions or methods, and calls that would cause exceeding the limit will
be delayed until they can be executed.

## Getting started

### Installation

```bash
$ pip install client_throttler
```

### Usage

1. [Optional] Configure a default config for all Throttler rate limiters.

    ```python
    from redis.client import Redis
    from client_throttler import setup, ThrottlerConfig
    
    setup(ThrottlerConfig(redis_client=Redis(host="localhost", port=1234, db=1), rate="100/s"))
    ```

2. Simply add a decorator to the function or method that needs to have its calls limited.

    ```python
    from redis.client import Redis
    from client_throttler import throttler, ThrottlerConfig, Throttler
    
    redis_client = Redis(host="localhost", port=1234, db=2)
    
    # use default config
    @throttler()
    def func_a(*args, **kwargs):
        return args, kwargs
   
    # use default config, and change custom config
    @throttler(ThrottlerConfig(rate="1/2s"))
    def func_b(*args, **kwargs):
        return args, kwargs
    
    # use default config, and change redis client and some custom config
    @throttler(ThrottlerConfig(rate="1/2s", redis_client=redis_client))
    def func_c(*args, **kwargs):
        return args, kwargs
   
    # change a callable into throttled callable
    def func_d(*args, **kwargs):
        return args, kwargs
    func = Throttler(ThrottlerConfig(func=func_d))
    func(*args, **kwargs)
    ```
   
3. [Optinal] get metric data
   
    ```python
    from redis.client import Redis
    from client_throttler import MetricManager, ThrottlerConfig, Throttler
   
    redis_client = Redis(host="localhost", port=1234, db=2)
    
    def func_a(*args, **kwargs):
        return args, kwargs
    
    # enable_metric_record=True should be set when collect metric
    config = ThrottlerConfig(func=func_a, redis_client=redis_client, rate="100/s", enable_metric_record=True)
    func = Throttler(config)
    
    """
    call your func
    """
    
    metrics = MetricManager(config).load_metrics()
    ```

## License

Based on the MIT protocol. Please refer to [LICENSE](https://github.com/OVINC-CN/ClientThrottler/blob/main/LICENSE)
