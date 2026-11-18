"""EliPilot: Ford intelligent cruise (iACC) set-speed request in openpilot longitudinal ("Self-drive").

How Ford's own system works, from the user's Ford-mode drives (rlogs 00000004, 00000005, 00000007, 00000008):
- the camera (IPMA) sends IPMA_Data2.IaccVLim_D_Rq = sign + the driver's tolerance, in km/h (IaccVLimUnit_D_Rq 1),
  for signs of 30 and above, and 254 (no request) below 30 (car parks); it is sent at 1 Hz whether cruise is on or not;
- the car (PCM) applies a *changed* request to its cruise set speed within 0.1 s, engaged or in standby; a driver
  change of the set speed (Set, +/-) holds until the request changes again.
With openpilot longitudinal the camera switches to 255 (no request) a few seconds after openpilot takes over speed
(drive 0000000a), so the cluster set speed stops following. EliPilot sends the camera's IPMA_Data2 on to the car:
- while the camera still requests (anything but 255), its request unchanged;
- after it switches to 255, the request the camera would send: sign + the driver's tolerance, which is learned from
  the camera itself (request - sign) whenever it does request, and 254 below 30.
The car's own set speed, which the cluster shows and openpilot uses as its maximum, then follows signs as in Ford mode.
"""

NO_REQUEST = 255       # camera: no iACC request (seen with openpilot longitudinal, and at start-up)
BELOW_MIN = 254        # camera: sign below the minimum set speed (car parks)
MIN_KPH = 30           # Ford's minimum set speed; signs below it get BELOW_MIN
MAX_REQUEST_KPH = 135  # ceiling enforced by the Ford safety mode (opendbc/safety/modes/ford.h)
UNIT_NONE, UNIT_KPH = 0, 1
VALID_SIGN = (5, 250)  # IsaVLim_D_Rq 251-255 are status codes
TOLERANCE_RANGE = (-10, 20)  # sanity bounds for a learned tolerance, km/h


def allowed(iacc: int, unit: int) -> bool:
  """Mirror of the Ford safety mode's IPMA_Data2 check."""
  return iacc in (NO_REQUEST, BELOW_MIN) or (unit == UNIT_KPH and MIN_KPH <= iacc <= MAX_REQUEST_KPH)


def _kph_sign(stock: dict) -> int | None:
  sign, unit = int(stock["IsaVLim_D_Rq"]), int(stock["IsaVLimUnit_D_Rq"])
  return sign if unit == UNIT_KPH and VALID_SIGN[0] <= sign <= VALID_SIGN[1] else None


def learn_tolerance(stock: dict) -> int | None:
  """The driver's tolerance (Ford menu) from a camera request, or None when this frame has no request to learn from."""
  sign = _kph_sign(stock)
  iacc, unit = int(stock["IaccVLim_D_Rq"]), int(stock["IaccVLimUnit_D_Rq"])
  if sign is None or sign < MIN_KPH or unit != UNIT_KPH or not (MIN_KPH <= iacc <= VALID_SIGN[1]):
    return None
  tolerance = iacc - sign
  return tolerance if TOLERANCE_RANGE[0] <= tolerance <= TOLERANCE_RANGE[1] else None


def iacc_request(stock: dict, follow: bool, tolerance_kph: int | None) -> tuple[int, int]:
  """(IaccVLim_D_Rq, IaccVLimUnit_D_Rq) to send for the camera's IPMA_Data2 values `stock`."""
  iacc, unit = int(stock["IaccVLim_D_Rq"]), int(stock["IaccVLimUnit_D_Rq"])
  camera = (iacc, unit) if allowed(iacc, unit) else (NO_REQUEST, UNIT_NONE)
  if not follow or iacc != NO_REQUEST:
    return camera  # setting off, or the camera is still requesting: its own request

  sign = _kph_sign(stock)
  if sign is None:
    return NO_REQUEST, UNIT_NONE
  if sign < MIN_KPH:
    return BELOW_MIN, UNIT_KPH
  if tolerance_kph is None:
    return NO_REQUEST, UNIT_NONE  # never seen the camera request: don't guess
  return min(max(sign + tolerance_kph, MIN_KPH), MAX_REQUEST_KPH), UNIT_KPH
