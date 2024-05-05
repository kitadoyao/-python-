import json
import os
class ConfigManager:
    config_file_path='config.json'
    config_file_mtime=None
    config_cache={}
    @classmethod
    def updata(cls):
        file_mtime=os.path.getmtime(cls.config_file_path)
        if cls.config_file_mtime!=file_mtime:
            cls.config_file_mtime=file_mtime
            cls.config_cache.clear()
            with open(cls.config_file_path,'r') as file:
                cls.config_cache=json.loads(file.read())
    @classmethod
    def get(cls,section,option):
        ConfigManager.updata()
        return cls.config_cache[section][option]
