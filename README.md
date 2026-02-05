# Unforgettable - v0.1.0

Unforgettable is a simple cache class you can used for tiny repetitive executions.

It uses a [temp dir](https://docs.python.org/3/library/tempfile.html) for each
execution. But you can define a your own directory and use the cache as much as
you want setting `SIMPLE_CACHE_ROOT_DIR` env var.

### How to install and use

Install with `uv` or `pip`
```shell
uv add unforgettable
# or
pip unforgettable
```

Setting values:
```python
cache = unforgettable()

cache.set(content=code, cache_id=cache_id=cache_id)
```

Setting values:
```python
cache = unforgettable()

cached_code = cache.get(cache_id=cache_id)
```


```python
SIMPLE_CACHE_ROOT_DIR = os.getenv("SIMPLE_CACHE_ROOT_DIR", None)
cache = unforgettable(cache_folder=SIMPLE_CACHE_ROOT_DIR)
```

And you can clean the cache with:
```python
unforgettable.clean()
```

### Example of Usage

```python
import requests
from unforgettable import unforgettable

cache = unforgettable()

def my_request():
    url = "https://github.com/bouli/unforgettable"

    url_request_1 = requests_get(url) #no cache yet
    url_request_2 = requests_get(url) #with cache

def requests_get(url):
    cached_code = cache.get(cache_id=url)

    if cached_code is not None:
        print("You are using cached")
        return cached_code

    req = requests.get(url=url, timeout=5)
    if req.status_code != 200:
        return None

    code = req.content
    cache.set(content=code, cache_id=url)
    return code
```

## See Also

- Github: https://github.com/bouli/unforgettable
- PyPI: https://pypi.org/project/unforgettable/

## License
This package is distributed under the [MIT license](https://opensource.org/license/MIT).
