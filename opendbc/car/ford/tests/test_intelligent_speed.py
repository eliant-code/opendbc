"""EliPilot iACC set-speed request: matches what Ford's camera sent on the user's drives."""
import unittest

from opendbc.car.ford.intelligent_speed import iacc_request, learn_tolerance, allowed, NO_REQUEST, BELOW_MIN


def stock(sign, sign_unit=1, iacc=255, iacc_unit=0):
  return {"IsaVLim_D_Rq": sign, "IsaVLimUnit_D_Rq": sign_unit, "IaccVLim_D_Rq": iacc, "IaccVLimUnit_D_Rq": iacc_unit}


class TestLearnTolerance(unittest.TestCase):
  def test_from_camera_requests(self):
    # Ford mode drives 00000004/07/08: 40 -> 43, 50 -> 53, 60 -> 63 with the user's +3
    for sign in (40, 50, 60):
      self.assertEqual(learn_tolerance(stock(sign, iacc=sign + 3, iacc_unit=1)), 3)
    self.assertEqual(learn_tolerance(stock(50, iacc=50, iacc_unit=1)), 0)

  def test_nothing_to_learn(self):
    for s in (stock(50), stock(10, iacc=254, iacc_unit=1), stock(254, iacc=255), stock(50, 3, 53, 1),
              stock(50, iacc=53, iacc_unit=2), stock(50, iacc=90, iacc_unit=1), stock(50, iacc=0, iacc_unit=0)):
      self.assertIsNone(learn_tolerance(s), s)


class TestIaccRequest(unittest.TestCase):
  def test_camera_still_requesting_passes_through(self):
    for s in (stock(50, iacc=53, iacc_unit=1), stock(10, iacc=254, iacc_unit=1), stock(40, iacc=43, iacc_unit=1)):
      for follow in (True, False):
        self.assertEqual(iacc_request(s, follow, 5), (s["IaccVLim_D_Rq"], s["IaccVLimUnit_D_Rq"]))

  def test_camera_stopped_fills_in(self):
    # Self-drive drive 0000000a: camera 255, sign 50/40/60/10 -> what the camera would send with +3
    for sign, want in ((50, (53, 1)), (40, (43, 1)), (60, (63, 1)), (30, (33, 1)), (10, (BELOW_MIN, 1)), (29, (BELOW_MIN, 1))):
      self.assertEqual(iacc_request(stock(sign), True, 3), want)
    self.assertEqual(iacc_request(stock(50), True, 0), (50, 1))

  def test_unknown_tolerance_or_no_sign(self):
    self.assertEqual(iacc_request(stock(50), True, None), (NO_REQUEST, 0))
    self.assertEqual(iacc_request(stock(10), True, None), (BELOW_MIN, 1))  # same as the camera, no tolerance needed
    for sign, unit in ((254, 1), (255, 1), (0, 0), (50, 3), (30, 2)):
      self.assertEqual(iacc_request(stock(sign, unit), True, 3), (NO_REQUEST, 0))

  def test_off(self):
    self.assertEqual(iacc_request(stock(50), False, 3), (255, 0))

  def test_bounds(self):
    self.assertEqual(iacc_request(stock(130), True, 20), (135, 1))
    self.assertEqual(iacc_request(stock(30), True, -10), (30, 1))
    self.assertEqual(iacc_request(stock(50, iacc=0, iacc_unit=0), False, None), (NO_REQUEST, 0))

  def test_every_output_passes_safety(self):
    for follow in (True, False):
      for tol in (None, -10, 0, 3, 20):
        for sign in range(256):
          for unit in range(4):
            for iacc in (0, 29, 30, 53, 135, 136, 254, 255):
              for iacc_unit in range(4):
                self.assertTrue(allowed(*iacc_request(stock(sign, unit, iacc, iacc_unit), follow, tol)))


if __name__ == "__main__":
  unittest.main()
