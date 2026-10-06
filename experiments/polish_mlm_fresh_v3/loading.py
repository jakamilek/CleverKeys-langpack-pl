"""Strict original-checkpoint load contract shared by inference and collection."""
from contract import MODELS


HERBERT_UNUSED_KEYS = frozenset({
    'bert.pooler.dense.bias', 'bert.pooler.dense.weight',
    'cls.sso.sso_relationship.bias', 'cls.sso.sso_relationship.weight',
})


def expected_unused_keys(name):
    if name not in MODELS:
        raise ValueError('unknown pinned model: ' + name)
    # The exact pinned HerBERT checkpoint also contains pooler/SSO weights.
    # AutoModelForMaskedLM uses its original trained MLM head and encoder.
    # These four unused keys were already checked explicitly in frozen v1.
    return HERBERT_UNUSED_KEYS if name == 'herbert' else frozenset()


def validate_loading_info(name, info):
    expected = expected_unused_keys(name)
    for field in ['missing_keys', 'mismatched_keys', 'error_msgs', 'unexpected_keys']:
        if not isinstance(info.get(field), list):
            raise ValueError('missing/invalid loading evidence: ' + field)
    if any(info[field] for field in ['missing_keys', 'mismatched_keys', 'error_msgs']):
        raise ValueError('incomplete original pretrained MLM: ' + repr(info))
    actual = info['unexpected_keys']
    if (any(not isinstance(key, str) for key in actual)
            or len(actual) != len(expected) or set(actual) != expected):
        raise ValueError('unexplained original pretrained weights: ' + repr(info))
