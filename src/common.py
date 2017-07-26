import numpy as np


def distance(coords1: np.ndarray, coords2: np.ndarray) -> np.ndarray:
    return np.linalg.norm(coords1 - coords2)
