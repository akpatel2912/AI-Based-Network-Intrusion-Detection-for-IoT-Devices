
import sys
from .config import settings

sys.path.insert(0, str(settings.ml_src_dir))
from predict import Predictor  # noqa: E402  (lives in ml/src)

_predictor = None


def get_predictor() -> Predictor:
    global _predictor
    if _predictor is None:
        _predictor = Predictor(settings.model_file)
    return _predictor
