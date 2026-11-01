"""Small audit-tool checks; not game/domain regression expectations."""
import copy
import importlib.util
from pathlib import Path
import unittest

P = Path(__file__).with_name('after_action_correspondence.py')
spec = importlib.util.spec_from_file_location('audit', P)
audit = importlib.util.module_from_spec(spec)
spec.loader.exec_module(audit)


def truth(i, x, alive=True):
    return {'id': i, 'alive': alive, 'positionM': {'x': x, 'y': 0, 'z': 0},
            'velocityMps': {'x': 0, 'y': 0, 'z': 0}}


def track(i, x, covariance=True):
    return {'trackId': i, 'trackNumber': i, 'kf6': [x, 0, 0, 0, 0, 0],
            'Pdiag': [1]*6 if covariance else None}


def sample(step, tracks, truth):
    return {'step': step, 'timeS': step/60, 'tracks': tracks, 'truthAfterAction': truth}


def capture(*samples, returns=()):
    return {'samples': list(samples), 'associationReturns': list(returns)}


class AuditChecks(unittest.TestCase):
    def test_shared_nearest_is_not_physical_duplicate(self):
        s, _, _, collisions, _, _ = audit.analyze(capture(sample(0, [track(10, 1), track(11, 2)], [truth(1, 0)])), {})
        self.assertEqual(len(collisions), 1)
        self.assertIsNone(s['fullPhysicalCorrespondence']['provenDuplicatePhysicalTrackCount'])
        self.assertTrue(s['fullPhysicalCorrespondence']['status'].startswith('UNKNOWN'))

    def test_truth_retirement_does_not_become_proven_switch(self):
        c = capture(sample(0, [track(10, 1)], [truth(1, 0), truth(2, 100)]),
                    sample(60, [track(10, 1)], [truth(1, 0, False), truth(2, 100)]))
        s, _, _, _, changes, _ = audit.analyze(c, {})
        self.assertEqual(s['nearestReferenceChanges'], 1)
        self.assertFalse(changes[0]['sameLiveReferenceSet'])
        self.assertFalse(changes[0]['oldReferenceStillAlive'])
        self.assertIsNone(s['fullPhysicalCorrespondence']['provenIdSwapCount'])

    def test_missing_covariance_is_not_replaced(self):
        s, _, pairs, _, _, _ = audit.analyze(capture(sample(0, [track(10, 1, False)], [truth(1, 0)])), {})
        self.assertEqual(s['invalidOrMissingCovarianceDiagonals'], 1)
        self.assertIsNone(pairs[0]['xMarginalSigmaUnits'])

    def test_per_return_uniqueness_not_across_turns(self):
        r = {'actualSelectedPairs': [{'i': 0, 'id': 10}]}
        s, *_ = audit.analyze(capture(sample(0, [], []), returns=[r, r]), {})
        self.assertEqual(s['logicalWithinReturnOneToOneViolations'], 0)
        bad = {'actualSelectedPairs': [{'i': 0, 'id': 10}, {'i': 1, 'id': 10}]}
        s, *_ = audit.analyze(capture(sample(0, [], []), returns=[bad]), {})
        self.assertEqual(s['logicalWithinReturnOneToOneViolations'], 1)

    def test_no_input_mutation_and_no_inferred_truth(self):
        c = capture(sample(0, [track(10, 1)], [truth(1, 0, None), truth(2, 100, False)]))
        before = copy.deepcopy(c)
        s, rows, pairs, *_ = audit.analyze(c, {})
        self.assertEqual(c, before)
        self.assertEqual(s['unknownTruthAliveFlags'], 1)
        self.assertIsNone(rows[0]['nearestInitialAsmReferenceId'])
        self.assertEqual(pairs, [])

    def test_residual_has_no_calibrated_gate(self):
        t = track(10, 3); t['kf6'][1] = 4
        s, _, pairs, *_ = audit.analyze(capture(sample(0, [t], [truth(1, 0)])), {})
        self.assertEqual(pairs[0]['distance3dM'], 5)
        self.assertEqual(pairs[0]['xMarginalSigmaUnits'], 3)
        self.assertNotIn('accepted', pairs[0])
        self.assertIsNone(s['fullPhysicalCorrespondence']['provenFalseMergeCount'])


if __name__ == '__main__':
    unittest.main()
