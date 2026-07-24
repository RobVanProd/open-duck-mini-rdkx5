# Winner-v123 episode-peak failure attribution

Status: `PASS_WINNER_V123_EPISODE_PEAK_FAILURE_ATTRIBUTION`

Decision: `CLOSE_V122_EPISODE_PEAK_OBJECTIVE`

V123 preserved walking and tracking but expanded the nominal torque-exceedance population from 15 events in V121 to 184 events. All 12 moving cells fail torque; only the four x=0 holds pass. The events are distributed through the gait cycle and across both knees and ankles, so the exact episode-global peak objective is closed without retry, scalar search, or checkpoint selection.

A static `torque_limit/kp = 0.14302893 rad` sent-target margin is not selected: 35/184 events occur without crossing that sent-target error, while the measured bridge leaves applied and sent targets separated under load. No successor training or behavior screen is authorized by this attribution.
