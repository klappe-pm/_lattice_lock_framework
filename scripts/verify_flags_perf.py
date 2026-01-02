import time

from lattice_lock.config.feature_flags import Feature, _get_enabled_features, is_feature_enabled

# Reset cache
_get_enabled_features.cache_clear()

start = time.time()
for _ in range(10000):
    is_feature_enabled(Feature.SHERIFF)
end = time.time()

duration = end - start
print(f"10000 checks took {duration:.4f}s")

# Verify cache hit
info = _get_enabled_features.cache_info()
print(f"Cache info: {info}")

if info.hits < 9999:
    print("FAIL: Cache hits too low")
    exit(1)

if info.misses > 1:
    print("FAIL: Cache misses too high")
    exit(1)

print("SUCCESS: Feature flags caching verified")
