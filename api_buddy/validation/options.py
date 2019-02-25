from copy import deepcopy
from typing import cast, Dict, List, Union
from urllib.parse import urlparse
from ..typing import Options
from ..exceptions import APIBuddyException
from ..utils import HTTP_METHODS, GET


def _more_than_one_method_selected(
            opts: Dict[str, Union[str, bool]]
        ) -> bool:
    return sum(
        cast(bool, opts[method]) for method in HTTP_METHODS
    ) > 1


def _validate_method(
            opts: Dict[str, Union[str, bool]]
        ) -> Dict[str, Union[str, bool]]:
    """Converts named bools to str enum

    Implicitly removed the old docopt booleans from opts
    Defaults to 'get'
    """
    if _more_than_one_method_selected(opts):
        raise APIBuddyException(
            title='These HTTP methods are borked',
            message=(
                'It appears you selected more than one method...\n'
                'How did you even do this?'
            )
        )
    selected_method = GET
    for method in HTTP_METHODS:
        using_this_method = opts[method]
        del opts[method]
        if using_this_method is True:
            selected_method = method
    opts['method'] = selected_method
    return opts


def _validate_endpoint(endpoint: str) -> str:
    url_parts = urlparse(endpoint)
    if url_parts.scheme:
        raise APIBuddyException(
            title='Check your endpoint, dude',
            message=(
                'You don\'t need to supply the full url, just the path.\n'
                f'Did you mean "{url_parts.path}"?'
            ),
        )
    return endpoint


def _validate_params(
            params: List[str]
        ) -> Dict[str, Union[str, List[str]]]:
    """Parse query params

    ['key1=val1', 'key2=val2', 'key2=val3']
    => {'key1': 'val1', 'key2': ['val2', 'val3']}
    """
    keyed_params: Dict[str, Union[str, List[str]]] = {}
    for param in params:
        try:
            key, val = param.split('=')
        except ValueError:
            raise APIBuddyException(
                title='One of your query params is borked',
                message=f'"{param}" should contain one and only one "="',
            )
        prev_val = keyed_params.get(key)
        if prev_val is None:
            keyed_params[key] = val
        elif isinstance(prev_val, str):
            keyed_params[key] = [prev_val, val]
        else:
            prev_val.append(val)
    return keyed_params


def validate_options(
            opts: Dict[str, Union[str, bool]]
        ) -> Options:
    """Convert types and validate"""
    valid_opts = deepcopy(opts)
    valid_opts['<endpoint>'] = _validate_endpoint(str(opts['<endpoint>']))
    valid_opts['<params>'] = _validate_params(  # type: ignore
        cast(List[str], opts['<params>'])
    )
    _validate_method(valid_opts)
    return cast(Options, valid_opts)
