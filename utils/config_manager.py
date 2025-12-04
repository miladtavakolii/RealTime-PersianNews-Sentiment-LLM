import yaml


class ConfigManager:
    '''Load and manage crawler configuration from YAML.'''

    def __init__(self, path: str = 'config/settings.yaml'):
        self.path = path
        with open(self.path, 'r', encoding='utf-8') as f:
            self.config = yaml.safe_load(f)

    def get_websites(self) -> dict:
        return self.config.get('websites', {})

    def get_site(self, name: str) -> dict:
        return self.config['websites'].get(name)
    
    def get_path(self) -> dict:
        return self.config.get('path')
    
    def get_spider_configs(self) -> list[dict]:
            """
            Convert YAML websites section to the format Scheduler expects:
            [{"spider": "isna", "interval": 15}, ...]
            """
            spider_configs = []
            for name, cfg in self.get_websites().items():
                if cfg['end_date']:
                    continue
                spider_configs.append({
                    "spider": name,
                    "interval": cfg.get("interval", 15)
                })
            return spider_configs

    def get_website_date_config(self) -> list[dict]:
        date_configs = []
        for name, cfg in self.get_websites().items():
            date_configs.append({
                "name": name,
                "start_date": cfg.get("start_date", 15),
                "end_date": cfg.get("end_date", None)
            })
        return date_configs
