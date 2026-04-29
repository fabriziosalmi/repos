import json

with open("astro-frontend/src/data/repositories.json", "r") as f:
    data = json.load(f)

for repo in data:
    # 1. Typo
    if "You-Know-Whst-AI-Mean" in repo.get("name", ""):
        repo["name"] = repo["name"].replace("Whst", "What")
    
    # 2. Metadata for zion and llmproxy
    if repo.get("name") == "zion":
        repo["license"] = {"name": "MIT License"}
        repo["topics"] = ["rust", "waf", "security"]
    
    if repo.get("name") == "llmproxy":
        repo["license"] = {"name": "MIT License"}
        repo["topics"] = ["python", "llm", "security"]

with open("astro-frontend/src/data/repositories.json", "w") as f:
    json.dump(data, f, indent=2)

print("Updated repositories.json (typo and licenses).")
