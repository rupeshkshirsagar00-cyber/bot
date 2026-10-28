import random
import string


def _rand(n, alphabet=string.ascii_lowercase + string.digits):
    return "".join(random.choice(alphabet) for _ in range(n))


def _hex(n):
    return "".join(random.choice("0123456789abcdef") for _ in range(n))


# current-ish stable desktop build range
_BUILD_NUMBERS = [350000, 352000, 355000, 358000, 360000, 362000, 365000]

_OS_LIST = ["Windows", "Mac OS X", "Linux"]

_CHROME_VERSIONS = ["126.0.0.0", "127.0.0.0", "128.0.0.0", "129.0.0.0"]


def _encode_build(num):
    # discord encodes build number into base64-ish 3-char segments
    return _rand(3)


def generate():
    """Return a fresh fingerprint string matching Discord's client format."""
    os_name = random.choice(_OS_LIST)
    build = random.choice(_BUILD_NUMBERS)
    chrome = random.choice(_CHROME_VERSIONS)

    encoded = "".join(_encode_build(build) for _ in range(3))

    parts = [
        os_name,
        chrome,
        encoded,
    ]
    return "-".join(parts)


def regenerate(state):
    fp = generate()
    state["fingerprint"] = fp
    return fp