import json

with open("astro-frontend/src/data/repositories.json", "r") as f:
    data = json.load(f)

for repo in data:
    if repo.get("name") == "secure-proxy-manager":
        repo["description"] = "Containerized Squid proxy with zero-latency ICAP WAF (SQLi/XSS/DLP/Cmd injection/Unicode homograph), SSL/TLS inspection, L1+L2 caching, bandwidth throttling, time-based ACL."

with open("astro-frontend/src/data/repositories.json", "w") as f:
    json.dump(data, f, indent=2)

print("Updated secure-proxy-manager description.")
