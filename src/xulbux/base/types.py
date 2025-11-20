from typing import TYPE_CHECKING, Annotated, TypeAlias, TypedDict, Optional, Union, Any
import regex as _rx
import re as _re

# PREVENT CIRCULAR IMPORTS
if TYPE_CHECKING:
    from ..color import rgba, hsla, hexa

#
################################################## COLOR ##################################################

Int_0_100 = Annotated[int, "An integer in range [0, 100]."]
Int_0_255 = Annotated[int, "An integer in range [0, 255]."]
Int_0_360 = Annotated[int, "An integer in range [0, 360]."]
Float_0_1 = Annotated[float, "A float in range [0.0, 1.0]."]

AnyRgba: TypeAlias = Any
AnyHsla: TypeAlias = Any
AnyHexa: TypeAlias = Any

Rgba: TypeAlias = Union[
    tuple[Int_0_255, Int_0_255, Int_0_255],
    tuple[Int_0_255, Int_0_255, Int_0_255, Float_0_1],
    list[Int_0_255],
    list[Union[Int_0_255, Float_0_1]],
    dict[str, Union[int, float]],
    "rgba",
    str,
]
Hsla: TypeAlias = Union[
    tuple[Int_0_360, Int_0_100, Int_0_100],
    tuple[Int_0_360, Int_0_100, Int_0_100, Float_0_1],
    list[Union[Int_0_360, Int_0_100]],
    list[Union[Int_0_360, Int_0_100, Float_0_1]],
    dict[str, Union[int, float]],
    "hsla",
    str,
]
Hexa: TypeAlias = Union[str, int, "hexa"]

#
################################################## CONSOLE ##################################################


class ArgConfigWithDefault(TypedDict):
    """TypedDict for flagged argument configuration with default value."""
    flags: set[str]
    default: str


class ArgResultRegular(TypedDict):
    """TypedDict for regular flagged argument results."""
    exists: bool
    value: Optional[str]


class ArgResultPositional(TypedDict):
    """TypedDict for positional `"before"`/`"after"` argument results."""
    exists: bool
    values: list[str]


################################################## DATA ##################################################

DataStructure: TypeAlias = Union[list, tuple, set, frozenset, dict]
IndexIterable: TypeAlias = Union[list, tuple, set, frozenset]

#
################################################## REGEX ##################################################

Pattern: TypeAlias = _re.Pattern[str] | _rx.Pattern[str]
Match: TypeAlias = _re.Match[str] | _rx.Match[str]

#
################################################## SYSTEM ##################################################


class MissingLibsMsgs(TypedDict):
    """TypedDict for the `missing_libs_msgs` parameter in `System.check_libs()`."""
    found_missing: str
    should_install: str
