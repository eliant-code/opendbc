# CLAUDE.md — eliant-code/opendbc (EliPilot)

This is Elias's personal fork of commaai/opendbc, used by EliPilot
(eliant-code/openpilot, branch `elipilot`). Elias does not read or write code:
Claude does the coding. Explain every change in plain language — what it does
in the car, not how the code works.

## Git rules (always)
- Only push to remotes owned by `eliant-code`. Never push to, open pull
  requests against, or file issues on commaai, BluePilot or any repository
  not owned by eliant-code.
- Work branch is `elipilot`. `master` tracks upstream commaai/opendbc;
  don't commit EliPilot changes there.
- Push only when Elias asks. Before pushing, say in one or two plain sentences
  what will change in the car.
- Never force-push or delete a branch without asking Elias first.
- Run the Ford safety tests before pushing (`./test.sh` where the tools exist).
  After pushing, wait for GitHub's checks (full safety suite, coverage, MISRA)
  to pass before updating the submodule pointer in eliant-code/openpilot.

## How changes reach the car
- EliPilot's openpilot repo pins this repo as a submodule. A push here does
  nothing on the car until the submodule pointer in eliant-code/openpilot
  `elipilot` is updated — that second step is what ships it.
- The pointer must be the exact commit that passed GitHub's checks. A wrong
  hash makes the device's update fail.

## Safety
- This code controls steering and speed on a real car (Ford Focus Mk4,
  MY2019, CAN not CAN FD). Never loosen safety limits (panda safety, torque
  or angle limits, allowed TX messages) without explaining the change and
  getting Elias's explicit approval.
