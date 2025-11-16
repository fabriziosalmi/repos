# Using pip-tools for Reproducible Builds

This project uses `pip-tools` to ensure reproducible and secure Python builds.

## Setup

1. **Install pip-tools**:
   ```bash
   pip install pip-tools
   ```

## Workflow

### Adding/Updating Dependencies

1. **Edit `requirements.in`**: Add or update high-level dependencies here
   ```
   requests>=2.28.0
   rich>=12.0.0
   ```

2. **Compile to generate locked requirements.txt**:
   ```bash
   pip-compile requirements.in --generate-hashes --output-file=requirements.txt
   ```
   
   This creates `requirements.txt` with:
   - All transitive dependencies
   - Exact pinned versions
   - SHA256 hashes for verification

3. **Install dependencies**:
   ```bash
   pip-sync requirements.txt
   ```
   
   Or for CI/CD:
   ```bash
   pip install -r requirements.txt --require-hashes
   ```

### Updating All Dependencies

```bash
pip-compile --upgrade requirements.in --generate-hashes
pip-sync
```

### Updating a Single Package

```bash
pip-compile --upgrade-package requests requirements.in --generate-hashes
pip-sync
```

## CI/CD Integration

Update `.github/workflows/deploy.yml` to use hashed requirements:

```yaml
- name: Install Python dependencies
  run: pip install -r requirements.txt --require-hashes
```

## Benefits

✅ **Reproducible builds**: Same versions every time  
✅ **Security**: Hash verification prevents tampering  
✅ **Transparency**: See all dependencies explicitly  
✅ **Control**: Pin exactly what you need  
✅ **Updates**: Easy to update when you want

## References

- [pip-tools Documentation](https://pip-tools.readthedocs.io/)
- [PEP 665: Lockfiles](https://peps.python.org/pep-0665/)
