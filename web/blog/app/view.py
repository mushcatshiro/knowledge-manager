
class BaseConfig:
    pass

class LocalConfig(BaseConfig):
    pass

class CloudConfig(BaseConfig):
    pass


config = {
    'development': BaseConfig,
    'default': LocalConfig,
    'cloud': CloudConfig
}