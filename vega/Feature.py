from .Tactic import Tactic, WithReorder

class Feature:
    def __init__(self, debug=False, tactic=WithReorder()):
        assert isinstance(debug, bool)
        assert isinstance(tactic, Tactic)
        self.debug = debug
        self.tactic = tactic

        if self.debug: print("[*] vega.Feature: {}".format(self))

    def __repr__(self):
        return '{}(debug={}, tactic={})'.format(self.__class__.__name__, self.debug, self.tactic)

class FeatureCapability:
    def __init__(self, feature):
        assert isinstance(feature, Feature)
        self.feature = feature