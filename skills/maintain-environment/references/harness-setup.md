# Harness setup

`/maintain-environment` chooses the home of a change. A personal choice goes in the workstation repo. `/set-up-machine` reads that repo and applies it to each harness on a machine. Read this file when the change adds a harness.

Add the new harness as one harness setup in `/set-up-machine`. A harness setup is that harness's only home there.

A registration list is a list of harness names kept beside the harness setups. The agent who adds a harness is the one who would write a second list.

Add no second registration list. Leave the harness name off every other list. The harness setup stays the only registration. A second list is a second copy of the names. The copy goes stale.

Read the harness setup contract in `/set-up-machine`, in `scripts/setupmachine/harness_setups/__init__.py`.
