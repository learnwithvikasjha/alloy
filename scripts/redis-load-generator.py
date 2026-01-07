import redis
import time
import random
import string
import threading
import os
from datetime import datetime

# ==========================
# CONFIG
# ==========================
REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", "6379"))
REDIS_DB = int(os.getenv("REDIS_DB", "0"))
REDIS_PASSWORD = os.getenv("REDIS_PASSWORD")

SLEEP_BETWEEN_OPS = 0.05   # Lower = more load
KEY_PREFIX = "demo"
RUN_FOREVER = True

# ==========================
# REDIS CLIENT
# ==========================
r = redis.Redis(
    host=REDIS_HOST,
    port=REDIS_PORT,
    db=REDIS_DB,
    password=REDIS_PASSWORD,
    decode_responses=True,
)

# ==========================
# HELPERS
# ==========================
def random_string(n=12):
    return "".join(random.choices(string.ascii_letters + string.digits, k=n))


def log(msg):
    print(f"[{datetime.utcnow().isoformat()}] {msg}")


# ==========================
# WORKLOAD FUNCTIONS
# ==========================
def kv_ops():
    """SET / GET with TTL"""
    while RUN_FOREVER:
        key = f"{KEY_PREFIX}:kv:{random.randint(1, 1000)}"
        value = random_string(50)

        r.set(key, value, ex=random.randint(10, 120))
        r.get(key)

        time.sleep(SLEEP_BETWEEN_OPS)


def counter_ops():
    """INCR counters"""
    while RUN_FOREVER:
        key = f"{KEY_PREFIX}:counter:{random.randint(1, 50)}"
        r.incr(key)
        time.sleep(SLEEP_BETWEEN_OPS)


def hash_ops():
    """HSET / HGETALL"""
    while RUN_FOREVER:
        key = f"{KEY_PREFIX}:hash:{random.randint(1, 100)}"
        r.hset(key, mapping={
            "views": random.randint(1, 10000),
            "likes": random.randint(1, 5000),
            "updated_at": time.time(),
        })
        r.hgetall(key)
        time.sleep(SLEEP_BETWEEN_OPS)


def list_ops():
    """LPUSH / RPOP"""
    while RUN_FOREVER:
        key = f"{KEY_PREFIX}:list:{random.randint(1, 20)}"
        r.lpush(key, random_string(20))
        r.rpop(key)
        time.sleep(SLEEP_BETWEEN_OPS)


def pubsub_ops():
    """Publish messages"""
    channel = f"{KEY_PREFIX}:events"
    i = 0
    while RUN_FOREVER:
        r.publish(channel, f"event-{i}")
        i += 1
        time.sleep(0.2)


def delete_ops():
    """Random deletes to show key churn"""
    while RUN_FOREVER:
        key = f"{KEY_PREFIX}:kv:{random.randint(1, 1000)}"
        r.delete(key)
        time.sleep(0.3)


def pipeline_ops():
    """Pipeline burst to show latency spikes"""
    while RUN_FOREVER:
        pipe = r.pipeline()
        for i in range(20):
            pipe.set(f"{KEY_PREFIX}:pipe:{i}", random_string(10))
        pipe.execute()
        time.sleep(1)


# ==========================
# MAIN
# ==========================
if __name__ == "__main__":
    log("Starting Redis load generator")
    log(f"Redis: {REDIS_HOST}:{REDIS_PORT} db={REDIS_DB}")

    threads = [
        threading.Thread(target=kv_ops, daemon=True),
        threading.Thread(target=counter_ops, daemon=True),
        threading.Thread(target=hash_ops, daemon=True),
        threading.Thread(target=list_ops, daemon=True),
        threading.Thread(target=pubsub_ops, daemon=True),
        threading.Thread(target=delete_ops, daemon=True),
        threading.Thread(target=pipeline_ops, daemon=True),
    ]

    for t in threads:
        t.start()

    try:
        while True:
            time.sleep(5)
            log("Load generator running...")
    except KeyboardInterrupt:
        log("Stopping load generator")
