# Winner-v12 CPU-contract dispatch attribution

The manual dispatch request at commit `e4d0e9cfc17aa8bee64a472a9364d4415a03d4bb` returned HTTP 404 because the newly added workflow was not present on the repository's default branch. GitHub created no workflow run.

This was a pre-execution stop: zero simulator ticks, optimizer updates, support cells, locomotion steps, and robot/RDK access. The frozen replacement uses one branch/path push trigger that fires only when its own workflow file is committed. Later evidence-import commits cannot retrigger it unless that frozen workflow changes.
