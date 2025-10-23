# src/utils/_force_list.py
from genbank_seqkit.logger import logger

def _force_list(x, verbose=False):
    """
    Ensure that x is always returned as a list.

    Parameters
    ------------
    x : any
        The input value to normalise.
    verbose: bool, optional
        If True, emits debug logs describing behaviour.

    Returns
    ------------
    list
        - [] if x is None
        - [x] if x is a single non-list item
        - x if x is already a list
    """

    # If input is empty:
    if x is None:
        if verbose:
            logger.debug("_force_list received None, returning an empty list")
        return []

    # If input is a list already:
    if isinstance(x, list):
        if verbose:
            logger.debug(f"_force_list received list of length {len(x)}, returning unchanged list")
        return x

    # If verbose is True, logger will receive readout of every input being handled at DEBUG level
    if verbose:
        logger.debug(f"_force_list received single item of type {type(x)}, returning it in a list")

    # If input is neither empty nor already a list, it will be returned as a list
    return [x]

if __name__ == "__main__": # pragma: no cover
    input = "Hello World"
    output = _force_list(input, verbose=True)
    print(output)
    print(type(output))