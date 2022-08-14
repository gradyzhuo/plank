from plank import logger

def show_deprecated_warnning(deprecated_namespace:str, instead_namespace:str, level:str="module"):
    logger.warn(f"The {level} `{deprecated_namespace}` was deprecated, `{instead_namespace}` instead.")