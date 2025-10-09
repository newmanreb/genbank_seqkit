# src/utils/_force_list.py
from genbank_seqkit.logger import logger

def _force_list(x, verbose=False):
    """
    Ensure that x is always returned as a list.
    If x is None, return an empty list.
    If x is a single item (not a list), wrap it in a list.
    If x already a list, do nothing.

    Parameters
    ------------
    x : any
        The input value to normalise.

    Returns
    ------------
    list
        A list containing the input object(s) or an empty list if input is None.

    Examples
    ------------
        force_list(None)        -> []           # None is returned as an empty list.
        force_list({'a': 1})    -> [{'a': 1}]   # A single item is wrapped in a list.
        force_list([{'a': 1}])  -> [{'a': 1}]   # A list remains a list.
    """

    if x is None:
        if verbose:
            logger.debug("_force_list received None, returning an empty list")
        return []
    if isinstance(x, list):
        if verbose:
            logger.debug(f"_force_list received list of length {len(x)}, returning unchanged list")
        return x
    if verbose:
        logger.debug(f"_force_list received single item of type {type(x)}, returning it in a list")
    return [x]

if __name__ == "__main__": # pragma: no cover
    input = "Hello World"
    output = _force_list(input, verbose=True)
    print(output)
    print(type(output))