import yaml


class ConfigManager:
    '''
    Configuration loader and accessor for the crawler and sentiment analysis system.

    This class provides a unified interface for:
        - Loading the YAML settings file
        - Fetching website-specific crawling configurations
        - Providing scheduler-friendly spider config structures
        - Reading model-related parameters

    Attributes:
        path (str):
            Filesystem path to the YAML configuration file.
        config (dict):
            Parsed YAML configuration stored as a Python dictionary.
    '''

    def __init__(self, path: str = 'config/settings.yaml'):
        '''
        Initialize and load the YAML configuration file.

        Args:
            path:
                Path to the YAML settings file.
                Defaults to `'config/settings.yaml'`.

        Raises:
            FileNotFoundError:
                If the given configuration file does not exist.
            yaml.YAMLError:
                If the file contains invalid YAML syntax.
        '''
        self.path = path
        with open(self.path, 'r', encoding='utf-8') as f:
            self.config = yaml.safe_load(f)

    def get_websites(self) -> dict:
        '''
        Retrieve the full `websites` configuration block.

        Returns:
            A dictionary of website configurations from YAML.
        '''
        return self.config.get('websites', {})

    def get_site(self, name: str) -> dict:
        '''
        Retrieve configuration for a specific website.

        Args:
            name: The website key within the `websites` section.

        Returns:
            The website's configuration dictionary, or None if missing.
        '''
        return self.config['websites'].get(name)

    def get_path(self) -> dict:
        '''
        Retrieve path-related configuration entries.

        Returns:
            Path configuration fields such as output folders.
        '''
        return self.config.get('path')

    def get_spider_configs(self) -> list[dict]:
        '''
        Convert website configuration entries into scheduler-friendly spider configs.

        This structure is used by the Scheduler component to determine:
            - Which spiders to run
            - At what time intervals
            - Ignore websites that have an `end_date` (i.e., disabled)

        Returns:
            
                A list of spider config objects:
                [
                    {'spider': 'isna', 'interval': 15},
                    {'spider': 'irna', 'interval': 20},
                    ...
                ]
        '''
        spider_configs = []
        for name, cfg in self.get_websites().items():
            if cfg['end_date']:
                continue
            spider_configs.append({
                'spider': name,
                'interval': cfg.get('interval', 15)
            })
        return spider_configs

    def get_website_date_config(self) -> list[dict]:
        '''
        Retrieve date-based crawling configuration for all websites.

        Used for determining:
            - Initial crawl start date
            - Whether the website has an end-date (stop crawling)

        Returns:
            
                List of objects:
                [
                    {'name': 'isna', 'start_date': '...', 'end_date': '...'},
                    ...
                ]
        '''
        date_configs = []
        for name, cfg in self.get_websites().items():
            date_configs.append({
                'name': name,
                'start_date': cfg.get('start_date', 15),
                'end_date': cfg.get('end_date', None)
            })
        return date_configs

    def get_model_info(self) -> dict:
        '''
        Retrieve the model configuration section.

        Typically includes:
            - Model name
            - Prompt template path
            - Additional model parameters

        Returns:
            dict: Model-related configuration values.
        '''
        return self.config['model']
