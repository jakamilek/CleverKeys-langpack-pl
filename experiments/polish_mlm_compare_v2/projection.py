"""Expose the ORIGINAL DistilBERT head to the unchanged v1 scoring/parity code."""
from types import SimpleNamespace


class DistilProjection:
    def __init__(self, original):
        self.original = original
        self.bert = original.distilbert
        self.cls = SimpleNamespace(predictions=self.head)

    def head(self, hidden):
        model = self.original
        return model.vocab_projector(model.vocab_layer_norm(model.activation(model.vocab_transform(hidden))))

    def __call__(self, *args, **kwargs):
        return self.original(*args, **kwargs)


def scoring_model(original, architecture):
    if architecture == 'bert':
        return original
    if architecture == 'distilbert':
        return DistilProjection(original)
    raise ValueError('unsupported original architecture')
