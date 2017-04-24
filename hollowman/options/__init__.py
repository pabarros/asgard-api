#encoding: utf-8

import os

ENV_NAME_PATTERN = "HOLLOWMAN_FILTER_{filter_name}_PARAM_{option}"


def get_option(filter_name, option_name):
    """
    Gets an options based on filter and option name.
    All option are read from Environ variables. The formation name is:
    HOLLOWMAN_FILTER_<FILTERNAME>_PARAM_<OPTIONNAME>
    If OPTIONNAME is a multi-value (list) option a numver suffix can be used, eg:
        HOLLOWMAN_FILTER_<FILTERNAME>_PARAM_<OPTIONNAME>_<INDEX>


    :filter_name: Name of the filter who owns this option
    :option_name: Name of the option
    :returns: The option value, **always** as a list of values

    """
    envvalue = _get_env_value(filter_name, option_name)

    idx = 0
    final_value = []

    if envvalue:
        final_value.append(envvalue)

    while _get_env_value(filter_name, option_name, idx):
        final_value.append(_get_env_value(filter_name, option_name, idx))
        idx += 1

    return final_value

def _get_env_value(filter_name, option_name, idx=None):
    base_envname = ENV_NAME_PATTERN.format(filter_name=filter_name.upper(), option=option_name.upper())
    if idx is None:
        return os.getenv(base_envname)
    return os.getenv("{}_{}".format(base_envname, idx))
