"""
v2 配置读取器

跟 v1 util/config_reader.py 几乎一样,只是放在 v2/util/ 下
保持 v1 / v2 独立,避免互相污染。
"""
import configparser
import os


class ConfigReader:
    """读 ui-test/resource/config/config.ini"""

    def __init__(self):
        # v2 配置直接指向 v1 那份 ini(共享同一份配置,避免双份漂移)
        ui_test_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
        self._config_path = os.path.join(ui_test_dir, "resource", "config", "config.ini")
        self._cache = {}

    def read(self, section: str) -> dict:
        """读 [section] 段,返回 dict"""
        if section in self._cache:
            return self._cache[section]

        cp = configparser.ConfigParser()
        if not os.path.exists(self._config_path):
            raise FileNotFoundError(
                f"Config not found: {self._config_path}. "
                f"v2 shares the v1 config — make sure ui-test/resource/config/config.ini exists."
            )
        cp.read(self._config_path, encoding="utf-8")
        if not cp.has_section(section):
            raise KeyError(f"Section [{section}] not found in config.ini")
        result = dict(cp.items(section))
        self._cache[section] = result
        return result

    def get_config_path(self) -> str:
        return self._config_path
