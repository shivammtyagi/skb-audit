import yaml

class ConfigError(Exception):
    pass

def load_config(path):
    with open(path, encoding="utf-8") as f:
        cfg = yaml.safe_load(f) or {}
    _validate(cfg)
    cfg.setdefault("article_types", {"default": "operational"})
    cfg.setdefault("options", {})
    cfg.setdefault("team_members", [])
    return cfg

def _validate(cfg):
    cs = cfg.get("content_source")
    if not isinstance(cs, dict):
        raise ConfigError("missing content_source block")
    if not cs.get("wxr_export") and not cs.get("live_url"):
        raise ConfigError("content_source needs wxr_export or live_url")
    if not cs.get("post_types"):
        raise ConfigError("content_source.post_types is required")
    tax = cs.get("taxonomies") or {}
    if not tax.get("category") or not tax.get("tag"):
        raise ConfigError("content_source.taxonomies.category and .tag are required")
    if not cfg.get("products"):
        raise ConfigError("at least one product is required")
