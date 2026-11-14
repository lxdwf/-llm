import concurrent.futures
import time
import requests
from collections import Counter

def one(i):
    t0 = time.time()
    try:
        r = requests.get("http://127.0.0.1:8000/ping", timeout=10)
        return i, r.status_code, round(time.time() - t0, 2)
    except Exception as e:
        # 连接失败、超时等都归为错误，返回错误状态
        return i, "ERROR", round(time.time() - t0, 2)

if __name__ == "__main__":
    with concurrent.futures.ThreadPoolExecutor(max_workers=50) as ex:
        results = list(ex.map(one, range(500)))

    # 统计状态码分布，包含成功和失败
    print(Counter(r[1] for r in results))
