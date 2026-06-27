# Target Dataset Manifest

status: `PASS_TARGET_DATASET_MANIFEST_READY`

This is a compact manifest of curated low-command target windows.
It does not include raw trace contents and does not start training.

## Summary

- input_curation_json: `outputs/analysis/closed_loop_teacher_window_curation.json`
- dataset_id: `407af2cbe0ad69e1`
- entries: `259`
- source_files: `16`
- source_mode_pairs: `16`
- raw_traces_present: `True`

## Source Distribution

| source | windows |
|---|---:|
| published_policy_command_straight_x008_seed0/trace_full_obs_footpos.jsonl | 18 |
| published_policy_command_straight_x008_seed1/trace_full_obs_footpos.jsonl | 20 |
| published_policy_command_straight_x008_seed2/trace_full_obs_footpos.jsonl | 17 |
| published_policy_command_straight_x008_seed3/trace_full_obs_footpos.jsonl | 17 |
| published_policy_command_straight_x008_seed4/trace_full_obs_footpos.jsonl | 17 |
| published_policy_command_straight_x008_seed5/trace_full_obs_footpos.jsonl | 19 |
| published_policy_command_straight_x008_seed6/trace_full_obs_footpos.jsonl | 18 |
| published_policy_command_straight_x008_seed7/trace_full_obs_footpos.jsonl | 15 |
| published_policy_command_turning_x0074_yneg0037_yawneg0074_seed0/trace_full_obs_footpos.jsonl | 17 |
| published_policy_command_turning_x0074_yneg0037_yawneg0074_seed1/trace_full_obs_footpos.jsonl | 16 |
| published_policy_command_turning_x0074_yneg0037_yawneg0074_seed2/trace_full_obs_footpos.jsonl | 14 |
| published_policy_command_turning_x0074_yneg0037_yawneg0074_seed3/trace_full_obs_footpos.jsonl | 19 |
| published_policy_command_turning_x0074_yneg0037_yawneg0074_seed4/trace_full_obs_footpos.jsonl | 2 |
| published_policy_command_turning_x0074_yneg0037_yawneg0074_seed5/trace_full_obs_footpos.jsonl | 19 |
| published_policy_command_turning_x0074_yneg0037_yawneg0074_seed6/trace_full_obs_footpos.jsonl | 18 |
| published_policy_command_turning_x0074_yneg0037_yawneg0074_seed7/trace_full_obs_footpos.jsonl | 13 |

## Metric Summary

| metric | min | mean | p50 | p95 | max |
|---|---:|---:|---:|---:|---:|
| mean_vx_m_s | 0.0431 | 0.0710 | 0.0705 | 0.0796 | 0.1008 |
| vy_abs_p95_m_s | 0.1331 | 0.1838 | 0.1878 | 0.1985 | 0.1999 |
| body_pitch_abs_p95_rad | 0.0329 | 0.0532 | 0.0529 | 0.0585 | 0.0840 |
| base_height_min_m | 0.1506 | 0.1616 | 0.1620 | 0.1625 | 0.1632 |
| sent_target_velocity_p95_rad_s | 2.1011 | 2.4968 | 2.4908 | 2.7185 | 3.3980 |
| joint_tracking_p95_rad | 0.0862 | 0.1166 | 0.1166 | 0.1255 | 0.1392 |
| contact_dominance_pct | 36.0000 | 47.5521 | 48.0000 | 60.0000 | 84.0000 |

## Windows

| id | source | ticks | vx | vy95 | pitch95 | height | sent_vel95 | track95 | contact_max |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|
| f37609b92540c062 | published_policy_command_straight_x008_seed0/trace_full_obs_footpos.jsonl | 0-24 | 0.0929 | 0.1398 | 0.0566 | 0.1521 | 3.3088 | 0.1392 | 60.0000 |
| efb0142fda8ea513 | published_policy_command_straight_x008_seed0/trace_full_obs_footpos.jsonl | 5-29 | 0.0833 | 0.1742 | 0.0569 | 0.1591 | 2.5879 | 0.1269 | 48.0000 |
| 01e26046657431dd | published_policy_command_straight_x008_seed0/trace_full_obs_footpos.jsonl | 10-34 | 0.0702 | 0.1793 | 0.0569 | 0.1591 | 2.4700 | 0.1255 | 52.0000 |
| bf1753d2ff960d6b | published_policy_command_straight_x008_seed0/trace_full_obs_footpos.jsonl | 15-39 | 0.0739 | 0.1793 | 0.0611 | 0.1591 | 2.5002 | 0.1255 | 60.0000 |
| f92727366f21ba08 | published_policy_command_straight_x008_seed0/trace_full_obs_footpos.jsonl | 55-79 | 0.0713 | 0.1934 | 0.0528 | 0.1619 | 2.3807 | 0.1228 | 52.0000 |
| 22fc98298f4db958 | published_policy_command_straight_x008_seed0/trace_full_obs_footpos.jsonl | 75-99 | 0.0713 | 0.1997 | 0.0558 | 0.1625 | 2.3184 | 0.1208 | 36.0000 |
| eea437c6ddde3ab9 | published_policy_command_straight_x008_seed0/trace_full_obs_footpos.jsonl | 80-104 | 0.0755 | 0.1997 | 0.0558 | 0.1625 | 2.4428 | 0.1154 | 44.0000 |
| 615f08cfe8cc5f1b | published_policy_command_straight_x008_seed0/trace_full_obs_footpos.jsonl | 85-109 | 0.0743 | 0.1812 | 0.0558 | 0.1632 | 2.4038 | 0.1079 | 40.0000 |
| 4bc4a800bdf7dc86 | published_policy_command_straight_x008_seed0/trace_full_obs_footpos.jsonl | 90-114 | 0.0719 | 0.1924 | 0.0558 | 0.1632 | 2.3507 | 0.1114 | 36.0000 |
| a1fc601dd81e5b9e | published_policy_command_straight_x008_seed0/trace_full_obs_footpos.jsonl | 95-119 | 0.0702 | 0.1924 | 0.0558 | 0.1632 | 2.3858 | 0.1154 | 44.0000 |
| 10af3494016a2d22 | published_policy_command_straight_x008_seed0/trace_full_obs_footpos.jsonl | 100-124 | 0.0716 | 0.1691 | 0.0528 | 0.1626 | 2.3619 | 0.1096 | 40.0000 |
| 74724745ec8ce987 | published_policy_command_straight_x008_seed0/trace_full_obs_footpos.jsonl | 105-129 | 0.0705 | 0.1895 | 0.0534 | 0.1621 | 2.1011 | 0.1072 | 40.0000 |
| e7dabf3836aafff2 | published_policy_command_straight_x008_seed0/trace_full_obs_footpos.jsonl | 110-134 | 0.0718 | 0.1895 | 0.0567 | 0.1621 | 2.1831 | 0.1028 | 44.0000 |
| 0cb7dd4c7abbd72e | published_policy_command_straight_x008_seed0/trace_full_obs_footpos.jsonl | 115-139 | 0.0714 | 0.1980 | 0.0567 | 0.1621 | 2.4002 | 0.1122 | 40.0000 |
| a5b62495fea889bc | published_policy_command_straight_x008_seed0/trace_full_obs_footpos.jsonl | 125-149 | 0.0711 | 0.1942 | 0.0567 | 0.1621 | 2.4691 | 0.1097 | 48.0000 |
| 83d140649f25e2c3 | published_policy_command_straight_x008_seed0/trace_full_obs_footpos.jsonl | 145-169 | 0.0704 | 0.1837 | 0.0530 | 0.1618 | 2.5163 | 0.1170 | 44.0000 |
| 0eed75a9566b489e | published_policy_command_straight_x008_seed0/trace_full_obs_footpos.jsonl | 215-239 | 0.0723 | 0.1944 | 0.0507 | 0.1622 | 2.4908 | 0.1221 | 52.0000 |
| 6de06dfdc77a261a | published_policy_command_straight_x008_seed0/trace_full_obs_footpos.jsonl | 220-244 | 0.0711 | 0.1820 | 0.0507 | 0.1622 | 2.4941 | 0.1131 | 48.0000 |
| 23821e629bdbd5ad | published_policy_command_straight_x008_seed1/trace_full_obs_footpos.jsonl | 95-119 | 0.0716 | 0.1899 | 0.0555 | 0.1619 | 2.5100 | 0.1208 | 52.0000 |
| 8d784409a13d3442 | published_policy_command_straight_x008_seed1/trace_full_obs_footpos.jsonl | 100-124 | 0.0753 | 0.1805 | 0.0531 | 0.1619 | 2.4991 | 0.1197 | 44.0000 |
| 2c19e1e712f5f642 | published_policy_command_straight_x008_seed1/trace_full_obs_footpos.jsonl | 105-129 | 0.0766 | 0.1888 | 0.0529 | 0.1619 | 2.1702 | 0.1182 | 44.0000 |
| 939a7f5647762038 | published_policy_command_straight_x008_seed1/trace_full_obs_footpos.jsonl | 110-134 | 0.0767 | 0.1888 | 0.0529 | 0.1619 | 2.2148 | 0.1137 | 48.0000 |
| 71b8c9ea6dc72687 | published_policy_command_straight_x008_seed1/trace_full_obs_footpos.jsonl | 115-139 | 0.0729 | 0.1891 | 0.0529 | 0.1625 | 2.5154 | 0.1213 | 40.0000 |
| 8f3e2c85e3e59718 | published_policy_command_straight_x008_seed1/trace_full_obs_footpos.jsonl | 120-144 | 0.0698 | 0.1891 | 0.0529 | 0.1625 | 2.5154 | 0.1205 | 48.0000 |
| 2399c044147b26a2 | published_policy_command_straight_x008_seed1/trace_full_obs_footpos.jsonl | 125-149 | 0.0718 | 0.1862 | 0.0526 | 0.1625 | 2.5154 | 0.1113 | 48.0000 |
| 13bfddf22b85d6f1 | published_policy_command_straight_x008_seed1/trace_full_obs_footpos.jsonl | 135-159 | 0.0728 | 0.1906 | 0.0513 | 0.1622 | 2.3077 | 0.1223 | 52.0000 |
| 1a7a44c103ef6c8a | published_policy_command_straight_x008_seed1/trace_full_obs_footpos.jsonl | 140-164 | 0.0728 | 0.1791 | 0.0513 | 0.1622 | 2.5031 | 0.1170 | 44.0000 |
| 5148e0b384c1d978 | published_policy_command_straight_x008_seed1/trace_full_obs_footpos.jsonl | 170-194 | 0.0704 | 0.1966 | 0.0527 | 0.1621 | 2.4713 | 0.1178 | 44.0000 |
| c905ecb0e687258d | published_policy_command_straight_x008_seed1/trace_full_obs_footpos.jsonl | 180-204 | 0.0707 | 0.1647 | 0.0530 | 0.1623 | 2.5397 | 0.1158 | 48.0000 |
| 857ac468857d986b | published_policy_command_straight_x008_seed1/trace_full_obs_footpos.jsonl | 185-209 | 0.0710 | 0.1950 | 0.0538 | 0.1622 | 2.1827 | 0.1130 | 40.0000 |
| 4bd45625edcbac8b | published_policy_command_straight_x008_seed1/trace_full_obs_footpos.jsonl | 190-214 | 0.0708 | 0.1950 | 0.0538 | 0.1622 | 2.3419 | 0.1158 | 48.0000 |
| 87802874d6fba95b | published_policy_command_straight_x008_seed1/trace_full_obs_footpos.jsonl | 195-219 | 0.0705 | 0.1851 | 0.0538 | 0.1620 | 2.5418 | 0.1176 | 40.0000 |
| 4efe0ec69600b4f4 | published_policy_command_straight_x008_seed1/trace_full_obs_footpos.jsonl | 200-224 | 0.0725 | 0.1851 | 0.0538 | 0.1620 | 2.5418 | 0.1140 | 44.0000 |
| a067ad734ee2accb | published_policy_command_straight_x008_seed1/trace_full_obs_footpos.jsonl | 205-229 | 0.0739 | 0.1851 | 0.0538 | 0.1620 | 2.5418 | 0.1162 | 48.0000 |
| d5292669cc847420 | published_policy_command_straight_x008_seed1/trace_full_obs_footpos.jsonl | 210-234 | 0.0729 | 0.1853 | 0.0508 | 0.1620 | 2.5624 | 0.1280 | 44.0000 |
| 7ddfbac3908c51ea | published_policy_command_straight_x008_seed1/trace_full_obs_footpos.jsonl | 215-239 | 0.0779 | 0.1853 | 0.0489 | 0.1620 | 2.5624 | 0.1267 | 52.0000 |
| 89afd8643b6fb92e | published_policy_command_straight_x008_seed1/trace_full_obs_footpos.jsonl | 220-244 | 0.0792 | 0.1728 | 0.0489 | 0.1625 | 2.5462 | 0.1201 | 48.0000 |
| 192f6a837778e423 | published_policy_command_straight_x008_seed1/trace_full_obs_footpos.jsonl | 225-249 | 0.0757 | 0.1950 | 0.0489 | 0.1625 | 2.4868 | 0.1262 | 44.0000 |
| cdbf9aa30a8d6dfa | published_policy_command_straight_x008_seed2/trace_full_obs_footpos.jsonl | 5-29 | 0.0944 | 0.1618 | 0.0329 | 0.1598 | 2.6524 | 0.1192 | 52.0000 |
| 640a4a7438aebb21 | published_policy_command_straight_x008_seed2/trace_full_obs_footpos.jsonl | 10-34 | 0.0809 | 0.1618 | 0.0369 | 0.1598 | 2.5406 | 0.1220 | 60.0000 |
| 80565b791cfadd24 | published_policy_command_straight_x008_seed2/trace_full_obs_footpos.jsonl | 15-39 | 0.0787 | 0.1608 | 0.0524 | 0.1598 | 2.5406 | 0.1304 | 64.0000 |
| df6f466361dfae1a | published_policy_command_straight_x008_seed2/trace_full_obs_footpos.jsonl | 20-44 | 0.0722 | 0.1907 | 0.0524 | 0.1598 | 2.4086 | 0.1252 | 48.0000 |
| 9456c60649711b45 | published_policy_command_straight_x008_seed2/trace_full_obs_footpos.jsonl | 25-49 | 0.0726 | 0.1907 | 0.0535 | 0.1598 | 2.5387 | 0.1247 | 56.0000 |
| 9cae163a529de146 | published_policy_command_straight_x008_seed2/trace_full_obs_footpos.jsonl | 30-54 | 0.0720 | 0.1867 | 0.0535 | 0.1620 | 2.5601 | 0.1220 | 52.0000 |
| 11f378cdaf016498 | published_policy_command_straight_x008_seed2/trace_full_obs_footpos.jsonl | 45-69 | 0.0746 | 0.1606 | 0.0532 | 0.1623 | 2.3263 | 0.1188 | 48.0000 |
| bbbed64f5186f3a8 | published_policy_command_straight_x008_seed2/trace_full_obs_footpos.jsonl | 50-74 | 0.0713 | 0.1935 | 0.0541 | 0.1623 | 2.2537 | 0.1118 | 40.0000 |
| 4821116a12707ff9 | published_policy_command_straight_x008_seed2/trace_full_obs_footpos.jsonl | 55-79 | 0.0723 | 0.1935 | 0.0541 | 0.1623 | 2.3118 | 0.1149 | 48.0000 |
| 2298ced25f24f2ec | published_policy_command_straight_x008_seed2/trace_full_obs_footpos.jsonl | 60-84 | 0.0709 | 0.1852 | 0.0541 | 0.1619 | 2.5155 | 0.1189 | 40.0000 |
| 9d66d814521597c2 | published_policy_command_straight_x008_seed2/trace_full_obs_footpos.jsonl | 135-159 | 0.0714 | 0.1888 | 0.0534 | 0.1621 | 2.4056 | 0.1244 | 52.0000 |
| d5df1f1c474901c4 | published_policy_command_straight_x008_seed2/trace_full_obs_footpos.jsonl | 140-164 | 0.0706 | 0.1801 | 0.0534 | 0.1621 | 2.5681 | 0.1204 | 44.0000 |
| b7aa1550498f5a67 | published_policy_command_straight_x008_seed2/trace_full_obs_footpos.jsonl | 170-194 | 0.0709 | 0.1877 | 0.0509 | 0.1621 | 2.3547 | 0.1144 | 40.0000 |
| 17886120cd1fb6d4 | published_policy_command_straight_x008_seed2/trace_full_obs_footpos.jsonl | 175-199 | 0.0713 | 0.1877 | 0.0512 | 0.1621 | 2.4145 | 0.1185 | 48.0000 |
| 1e28fa01db8bab0a | published_policy_command_straight_x008_seed2/trace_full_obs_footpos.jsonl | 180-204 | 0.0734 | 0.1622 | 0.0512 | 0.1621 | 2.5292 | 0.1116 | 48.0000 |
| b1e10084cb25b5cc | published_policy_command_straight_x008_seed2/trace_full_obs_footpos.jsonl | 190-214 | 0.0732 | 0.1880 | 0.0536 | 0.1621 | 2.3125 | 0.1232 | 52.0000 |
| 35f9bf6d35a7b51c | published_policy_command_straight_x008_seed2/trace_full_obs_footpos.jsonl | 195-219 | 0.0709 | 0.1982 | 0.0536 | 0.1623 | 2.4938 | 0.1263 | 44.0000 |
| c25c95fa14d1b084 | published_policy_command_straight_x008_seed3/trace_full_obs_footpos.jsonl | 80-104 | 0.0700 | 0.1930 | 0.0528 | 0.1617 | 2.4385 | 0.1186 | 48.0000 |
| 36850df413335621 | published_policy_command_straight_x008_seed3/trace_full_obs_footpos.jsonl | 85-109 | 0.0695 | 0.1714 | 0.0528 | 0.1624 | 2.4605 | 0.1067 | 44.0000 |
| 61d3dbdd436ffa9d | published_policy_command_straight_x008_seed3/trace_full_obs_footpos.jsonl | 90-114 | 0.0700 | 0.1902 | 0.0528 | 0.1624 | 2.4237 | 0.1164 | 40.0000 |
| 326a1f0a185f4aff | published_policy_command_straight_x008_seed3/trace_full_obs_footpos.jsonl | 100-124 | 0.0703 | 0.1723 | 0.0495 | 0.1624 | 2.4342 | 0.1176 | 44.0000 |
| 80225f34b93facc8 | published_policy_command_straight_x008_seed3/trace_full_obs_footpos.jsonl | 105-129 | 0.0723 | 0.1898 | 0.0491 | 0.1624 | 2.2395 | 0.1168 | 44.0000 |
| 26ca1912e2d0cdf2 | published_policy_command_straight_x008_seed3/trace_full_obs_footpos.jsonl | 110-134 | 0.0740 | 0.1898 | 0.0496 | 0.1624 | 2.4323 | 0.1146 | 48.0000 |
| da3507fc1ea733e3 | published_policy_command_straight_x008_seed3/trace_full_obs_footpos.jsonl | 125-149 | 0.0726 | 0.1965 | 0.0517 | 0.1622 | 2.4586 | 0.1127 | 48.0000 |
| 631de4e388f78e2e | published_policy_command_straight_x008_seed3/trace_full_obs_footpos.jsonl | 140-164 | 0.0694 | 0.1760 | 0.0525 | 0.1616 | 2.4671 | 0.1101 | 40.0000 |
| 2afb404c91e69f97 | published_policy_command_straight_x008_seed3/trace_full_obs_footpos.jsonl | 145-169 | 0.0711 | 0.1822 | 0.0525 | 0.1616 | 2.3867 | 0.1127 | 40.0000 |
| d066bb0055814254 | published_policy_command_straight_x008_seed3/trace_full_obs_footpos.jsonl | 150-174 | 0.0714 | 0.1822 | 0.0530 | 0.1616 | 2.4896 | 0.1210 | 48.0000 |
| d41648c3e9171bbc | published_policy_command_straight_x008_seed3/trace_full_obs_footpos.jsonl | 155-179 | 0.0709 | 0.1822 | 0.0528 | 0.1616 | 2.4984 | 0.1219 | 44.0000 |
| 543101d18b449cf3 | published_policy_command_straight_x008_seed3/trace_full_obs_footpos.jsonl | 160-184 | 0.0706 | 0.1822 | 0.0529 | 0.1616 | 2.4793 | 0.1210 | 52.0000 |
| 6618d5b2b3cf4ce6 | published_policy_command_straight_x008_seed3/trace_full_obs_footpos.jsonl | 165-189 | 0.0715 | 0.1822 | 0.0529 | 0.1622 | 2.5488 | 0.1157 | 52.0000 |
| ee0fd226c929a896 | published_policy_command_straight_x008_seed3/trace_full_obs_footpos.jsonl | 205-229 | 0.0698 | 0.1927 | 0.0531 | 0.1618 | 2.3433 | 0.1206 | 52.0000 |
| 814a5885c302b88b | published_policy_command_straight_x008_seed3/trace_full_obs_footpos.jsonl | 210-234 | 0.0699 | 0.1884 | 0.0517 | 0.1623 | 2.2786 | 0.1206 | 40.0000 |
| 8cd149ca209fd74f | published_policy_command_straight_x008_seed3/trace_full_obs_footpos.jsonl | 215-239 | 0.0723 | 0.1884 | 0.0526 | 0.1623 | 2.3979 | 0.1155 | 48.0000 |
| 5fecb7bec63da4d4 | published_policy_command_straight_x008_seed3/trace_full_obs_footpos.jsonl | 220-244 | 0.0718 | 0.1643 | 0.0532 | 0.1619 | 2.4207 | 0.1092 | 44.0000 |
| 80b1cb37ce60b8b3 | published_policy_command_straight_x008_seed4/trace_full_obs_footpos.jsonl | 0-24 | 0.0855 | 0.1628 | 0.0797 | 0.1506 | 3.1965 | 0.1295 | 72.0000 |
| 32109ad0b58411e6 | published_policy_command_straight_x008_seed4/trace_full_obs_footpos.jsonl | 5-29 | 0.0578 | 0.1628 | 0.0840 | 0.1603 | 2.1630 | 0.0862 | 80.0000 |
| 7d88958ffcc4691e | published_policy_command_straight_x008_seed4/trace_full_obs_footpos.jsonl | 145-169 | 0.0431 | 0.1608 | 0.0702 | 0.1574 | 2.3208 | 0.1082 | 64.0000 |
| 3174a81c2adc032a | published_policy_command_straight_x008_seed4/trace_full_obs_footpos.jsonl | 150-174 | 0.0522 | 0.1608 | 0.0695 | 0.1574 | 2.5666 | 0.1181 | 64.0000 |
| 2b53d58c716db3eb | published_policy_command_straight_x008_seed4/trace_full_obs_footpos.jsonl | 165-189 | 0.0616 | 0.1721 | 0.0692 | 0.1601 | 2.4413 | 0.1183 | 52.0000 |
| b1faf02ebdbd96c9 | published_policy_command_straight_x008_seed4/trace_full_obs_footpos.jsonl | 170-194 | 0.0612 | 0.1831 | 0.0692 | 0.1601 | 2.4413 | 0.1237 | 44.0000 |
| 86b6ea037d873424 | published_policy_command_straight_x008_seed4/trace_full_obs_footpos.jsonl | 175-199 | 0.0621 | 0.1831 | 0.0642 | 0.1601 | 2.4714 | 0.1250 | 52.0000 |
| c9af451f73e3a658 | published_policy_command_straight_x008_seed4/trace_full_obs_footpos.jsonl | 180-204 | 0.0659 | 0.1737 | 0.0619 | 0.1617 | 2.3943 | 0.1183 | 48.0000 |
| e3ee3fbc4ce84103 | published_policy_command_straight_x008_seed4/trace_full_obs_footpos.jsonl | 185-209 | 0.0654 | 0.1831 | 0.0565 | 0.1617 | 2.1992 | 0.1137 | 40.0000 |
| 14f8afd2c0c33eb5 | published_policy_command_straight_x008_seed4/trace_full_obs_footpos.jsonl | 190-214 | 0.0687 | 0.1831 | 0.0551 | 0.1617 | 2.2774 | 0.1174 | 48.0000 |
| e95e06ce990784ee | published_policy_command_straight_x008_seed4/trace_full_obs_footpos.jsonl | 195-219 | 0.0685 | 0.1824 | 0.0551 | 0.1618 | 2.5043 | 0.1195 | 40.0000 |
| 97edcff84ced6216 | published_policy_command_straight_x008_seed4/trace_full_obs_footpos.jsonl | 200-224 | 0.0700 | 0.1824 | 0.0550 | 0.1618 | 2.4766 | 0.1151 | 44.0000 |
| 228dfce068664e67 | published_policy_command_straight_x008_seed4/trace_full_obs_footpos.jsonl | 205-229 | 0.0728 | 0.1824 | 0.0553 | 0.1618 | 2.4672 | 0.1124 | 48.0000 |
| 700ebce97c2545f3 | published_policy_command_straight_x008_seed4/trace_full_obs_footpos.jsonl | 210-234 | 0.0729 | 0.1815 | 0.0558 | 0.1618 | 2.4672 | 0.1206 | 40.0000 |
| 0b38cb6a7b032926 | published_policy_command_straight_x008_seed4/trace_full_obs_footpos.jsonl | 215-239 | 0.0769 | 0.1815 | 0.0558 | 0.1618 | 2.4944 | 0.1172 | 48.0000 |
| ca78427b3bb9266e | published_policy_command_straight_x008_seed4/trace_full_obs_footpos.jsonl | 220-244 | 0.0759 | 0.1657 | 0.0558 | 0.1622 | 2.5887 | 0.1106 | 44.0000 |
| 06d9cdc9474066f8 | published_policy_command_straight_x008_seed4/trace_full_obs_footpos.jsonl | 225-249 | 0.0711 | 0.1937 | 0.0558 | 0.1622 | 2.4944 | 0.1147 | 40.0000 |
| fffc9ade1b269cdb | published_policy_command_straight_x008_seed5/trace_full_obs_footpos.jsonl | 20-44 | 0.0770 | 0.1650 | 0.0524 | 0.1601 | 2.8251 | 0.1218 | 44.0000 |
| aad3e4e16219109f | published_policy_command_straight_x008_seed5/trace_full_obs_footpos.jsonl | 25-49 | 0.0847 | 0.1650 | 0.0578 | 0.1601 | 2.5501 | 0.1228 | 56.0000 |
| acc304b92e694295 | published_policy_command_straight_x008_seed5/trace_full_obs_footpos.jsonl | 30-54 | 0.0796 | 0.1626 | 0.0585 | 0.1607 | 2.5775 | 0.1178 | 52.0000 |
| 6835278bfeee9831 | published_policy_command_straight_x008_seed5/trace_full_obs_footpos.jsonl | 35-59 | 0.0723 | 0.1887 | 0.0585 | 0.1607 | 2.5451 | 0.1250 | 44.0000 |
| 1d368eeafa1f263d | published_policy_command_straight_x008_seed5/trace_full_obs_footpos.jsonl | 40-64 | 0.0708 | 0.1887 | 0.0585 | 0.1607 | 2.6560 | 0.1250 | 52.0000 |
| bca62ab24710c163 | published_policy_command_straight_x008_seed5/trace_full_obs_footpos.jsonl | 45-69 | 0.0709 | 0.1701 | 0.0585 | 0.1616 | 2.5760 | 0.1202 | 48.0000 |
| 85bfdb03bc50588e | published_policy_command_straight_x008_seed5/trace_full_obs_footpos.jsonl | 55-79 | 0.0706 | 0.1887 | 0.0555 | 0.1616 | 2.5006 | 0.1202 | 48.0000 |
| 9a057c60c5e10988 | published_policy_command_straight_x008_seed5/trace_full_obs_footpos.jsonl | 60-84 | 0.0713 | 0.1825 | 0.0555 | 0.1626 | 2.5750 | 0.1214 | 40.0000 |
| 7bcd6d2bb64e9113 | published_policy_command_straight_x008_seed5/trace_full_obs_footpos.jsonl | 70-94 | 0.0707 | 0.1825 | 0.0539 | 0.1626 | 2.5006 | 0.1192 | 48.0000 |
| ac1cd32f00190612 | published_policy_command_straight_x008_seed5/trace_full_obs_footpos.jsonl | 75-99 | 0.0715 | 0.1916 | 0.0488 | 0.1616 | 2.4062 | 0.1237 | 44.0000 |
| d3f5146476e5607b | published_policy_command_straight_x008_seed5/trace_full_obs_footpos.jsonl | 80-104 | 0.0733 | 0.1916 | 0.0534 | 0.1616 | 2.3763 | 0.1213 | 52.0000 |
| 19c3fe897af7e44a | published_policy_command_straight_x008_seed5/trace_full_obs_footpos.jsonl | 85-109 | 0.0710 | 0.1829 | 0.0538 | 0.1616 | 2.4228 | 0.1140 | 48.0000 |
| f62bbf91c2b2d16c | published_policy_command_straight_x008_seed5/trace_full_obs_footpos.jsonl | 95-119 | 0.0699 | 0.1923 | 0.0541 | 0.1616 | 2.4148 | 0.1224 | 52.0000 |
| 937db0df0d04c00a | published_policy_command_straight_x008_seed5/trace_full_obs_footpos.jsonl | 100-124 | 0.0702 | 0.1773 | 0.0541 | 0.1620 | 2.3523 | 0.1183 | 44.0000 |
| cf4faab713ad0496 | published_policy_command_straight_x008_seed5/trace_full_obs_footpos.jsonl | 110-134 | 0.0706 | 0.1893 | 0.0541 | 0.1620 | 2.3947 | 0.1166 | 52.0000 |
| a080906d8a6f771b | published_policy_command_straight_x008_seed5/trace_full_obs_footpos.jsonl | 115-139 | 0.0708 | 0.1883 | 0.0541 | 0.1621 | 2.4422 | 0.1229 | 44.0000 |
| 6521b2747897e6d0 | published_policy_command_straight_x008_seed5/trace_full_obs_footpos.jsonl | 135-159 | 0.0724 | 0.1881 | 0.0547 | 0.1621 | 2.4305 | 0.1250 | 52.0000 |
| c8d9b2ed1ba0bb1b | published_policy_command_straight_x008_seed5/trace_full_obs_footpos.jsonl | 140-164 | 0.0720 | 0.1759 | 0.0547 | 0.1622 | 2.5585 | 0.1190 | 44.0000 |
| c305867b4669a91d | published_policy_command_straight_x008_seed5/trace_full_obs_footpos.jsonl | 220-244 | 0.0702 | 0.1739 | 0.0537 | 0.1622 | 2.5297 | 0.1116 | 48.0000 |
| e5bd71a36d8ca02c | published_policy_command_straight_x008_seed6/trace_full_obs_footpos.jsonl | 15-39 | 0.0751 | 0.1923 | 0.0552 | 0.1593 | 2.4647 | 0.1298 | 60.0000 |
| 1d7f5dc38c51afd0 | published_policy_command_straight_x008_seed6/trace_full_obs_footpos.jsonl | 70-94 | 0.0742 | 0.1824 | 0.0546 | 0.1621 | 2.5038 | 0.1149 | 48.0000 |
| 689ab351676fc906 | published_policy_command_straight_x008_seed6/trace_full_obs_footpos.jsonl | 80-104 | 0.0789 | 0.1816 | 0.0515 | 0.1621 | 2.5732 | 0.1173 | 48.0000 |
| 7e8f26994d3c9fe1 | published_policy_command_straight_x008_seed6/trace_full_obs_footpos.jsonl | 85-109 | 0.0785 | 0.1677 | 0.0515 | 0.1625 | 2.6465 | 0.1108 | 44.0000 |
| f4fbc2efacf6319c | published_policy_command_straight_x008_seed6/trace_full_obs_footpos.jsonl | 90-114 | 0.0762 | 0.1987 | 0.0515 | 0.1625 | 2.5620 | 0.1167 | 40.0000 |
| d609de931b679001 | published_policy_command_straight_x008_seed6/trace_full_obs_footpos.jsonl | 95-119 | 0.0767 | 0.1987 | 0.0506 | 0.1625 | 2.6021 | 0.1209 | 48.0000 |
| 6867e7b1421b22cb | published_policy_command_straight_x008_seed6/trace_full_obs_footpos.jsonl | 100-124 | 0.0790 | 0.1674 | 0.0489 | 0.1625 | 2.5898 | 0.1156 | 44.0000 |
| 52b6cc26a0f87249 | published_policy_command_straight_x008_seed6/trace_full_obs_footpos.jsonl | 105-129 | 0.0793 | 0.1984 | 0.0503 | 0.1625 | 2.4453 | 0.1156 | 44.0000 |
| 259c2e148b5383d8 | published_policy_command_straight_x008_seed6/trace_full_obs_footpos.jsonl | 110-134 | 0.0817 | 0.1984 | 0.0510 | 0.1626 | 2.4810 | 0.1143 | 48.0000 |
| 07db2ffe78c5b47e | published_policy_command_straight_x008_seed6/trace_full_obs_footpos.jsonl | 115-139 | 0.0801 | 0.1985 | 0.0510 | 0.1628 | 2.5109 | 0.1193 | 36.0000 |
| c840a96acbec33f2 | published_policy_command_straight_x008_seed6/trace_full_obs_footpos.jsonl | 120-144 | 0.0765 | 0.1985 | 0.0510 | 0.1628 | 2.4380 | 0.1193 | 44.0000 |
| e83d8f48d83c9639 | published_policy_command_straight_x008_seed6/trace_full_obs_footpos.jsonl | 125-149 | 0.0760 | 0.1962 | 0.0544 | 0.1628 | 2.3829 | 0.1080 | 44.0000 |
| 288eeb280b4f7bea | published_policy_command_straight_x008_seed6/trace_full_obs_footpos.jsonl | 185-209 | 0.0771 | 0.1931 | 0.0428 | 0.1622 | 2.4528 | 0.1190 | 44.0000 |
| a15918569f099740 | published_policy_command_straight_x008_seed6/trace_full_obs_footpos.jsonl | 190-214 | 0.0818 | 0.1931 | 0.0439 | 0.1622 | 2.4517 | 0.1250 | 52.0000 |
| 367c9df18d1eafda | published_policy_command_straight_x008_seed6/trace_full_obs_footpos.jsonl | 195-219 | 0.0794 | 0.1970 | 0.0439 | 0.1622 | 2.5907 | 0.1268 | 44.0000 |
| 24b53f7d67686f67 | published_policy_command_straight_x008_seed6/trace_full_obs_footpos.jsonl | 200-224 | 0.0794 | 0.1970 | 0.0439 | 0.1622 | 2.5658 | 0.1233 | 48.0000 |
| 6a9eff170eaeb1b4 | published_policy_command_straight_x008_seed6/trace_full_obs_footpos.jsonl | 205-229 | 0.0795 | 0.1970 | 0.0503 | 0.1622 | 2.4834 | 0.1224 | 52.0000 |
| d0298e24207b55b1 | published_policy_command_straight_x008_seed6/trace_full_obs_footpos.jsonl | 220-244 | 0.0743 | 0.1688 | 0.0533 | 0.1626 | 2.4639 | 0.1106 | 44.0000 |
| 42b9647a765a2e07 | published_policy_command_straight_x008_seed7/trace_full_obs_footpos.jsonl | 45-69 | 0.0749 | 0.1607 | 0.0544 | 0.1622 | 2.5639 | 0.1126 | 48.0000 |
| 8dba054a548416d5 | published_policy_command_straight_x008_seed7/trace_full_obs_footpos.jsonl | 55-79 | 0.0761 | 0.1802 | 0.0533 | 0.1621 | 2.4394 | 0.1220 | 52.0000 |
| fcd89f28631c0678 | published_policy_command_straight_x008_seed7/trace_full_obs_footpos.jsonl | 70-94 | 0.0756 | 0.1846 | 0.0533 | 0.1621 | 2.4580 | 0.1185 | 52.0000 |
| 3ee3e1d834a2477c | published_policy_command_straight_x008_seed7/trace_full_obs_footpos.jsonl | 75-99 | 0.0763 | 0.1839 | 0.0503 | 0.1624 | 2.3136 | 0.1231 | 44.0000 |
| e404f7f2242aba31 | published_policy_command_straight_x008_seed7/trace_full_obs_footpos.jsonl | 80-104 | 0.0788 | 0.1839 | 0.0509 | 0.1624 | 2.4327 | 0.1208 | 52.0000 |
| 7215aed311e767bf | published_policy_command_straight_x008_seed7/trace_full_obs_footpos.jsonl | 85-109 | 0.0785 | 0.1718 | 0.0509 | 0.1624 | 2.4628 | 0.1136 | 48.0000 |
| cabef150c3eee5bf | published_policy_command_straight_x008_seed7/trace_full_obs_footpos.jsonl | 90-114 | 0.0766 | 0.1904 | 0.0509 | 0.1624 | 2.4276 | 0.1190 | 44.0000 |
| 56c14909f00a1912 | published_policy_command_straight_x008_seed7/trace_full_obs_footpos.jsonl | 95-119 | 0.0766 | 0.1904 | 0.0509 | 0.1624 | 2.4276 | 0.1233 | 52.0000 |
| 864797237027522a | published_policy_command_straight_x008_seed7/trace_full_obs_footpos.jsonl | 100-124 | 0.0777 | 0.1641 | 0.0502 | 0.1624 | 2.4372 | 0.1170 | 44.0000 |
| 78465bac606ca2ae | published_policy_command_straight_x008_seed7/trace_full_obs_footpos.jsonl | 105-129 | 0.0791 | 0.1882 | 0.0503 | 0.1624 | 2.3456 | 0.1156 | 44.0000 |
| 2ea64ff5b6a792a9 | published_policy_command_straight_x008_seed7/trace_full_obs_footpos.jsonl | 110-134 | 0.0798 | 0.1882 | 0.0503 | 0.1624 | 2.4582 | 0.1134 | 48.0000 |
| 39ebd0764bef0813 | published_policy_command_straight_x008_seed7/trace_full_obs_footpos.jsonl | 165-189 | 0.0750 | 0.1873 | 0.0552 | 0.1623 | 2.4428 | 0.1151 | 52.0000 |
| 2ca265012746d6ef | published_policy_command_straight_x008_seed7/trace_full_obs_footpos.jsonl | 180-204 | 0.0762 | 0.1649 | 0.0547 | 0.1629 | 2.5574 | 0.1166 | 48.0000 |
| 5cc2bf69f903cd9f | published_policy_command_straight_x008_seed7/trace_full_obs_footpos.jsonl | 220-244 | 0.0751 | 0.1698 | 0.0491 | 0.1625 | 2.6562 | 0.1079 | 44.0000 |
| 97e1e4b73f91f397 | published_policy_command_straight_x008_seed7/trace_full_obs_footpos.jsonl | 225-249 | 0.0771 | 0.1912 | 0.0491 | 0.1625 | 2.3983 | 0.1113 | 40.0000 |
| 3b4abb63356ee2bf | published_policy_command_turning_x0074_yneg0037_yawneg0074_seed0/trace_full_obs_footpos.jsonl | 5-29 | 0.0692 | 0.1810 | 0.0424 | 0.1598 | 2.5812 | 0.1213 | 52.0000 |
| 7ed9a5f2399ebc8c | published_policy_command_turning_x0074_yneg0037_yawneg0074_seed0/trace_full_obs_footpos.jsonl | 15-39 | 0.0669 | 0.1822 | 0.0530 | 0.1598 | 2.4240 | 0.1192 | 60.0000 |
| 021fffd1bf492e05 | published_policy_command_turning_x0074_yneg0037_yawneg0074_seed0/trace_full_obs_footpos.jsonl | 20-44 | 0.0657 | 0.1878 | 0.0530 | 0.1598 | 2.4240 | 0.1133 | 44.0000 |
| 6c3cf4dcd3a3caeb | published_policy_command_turning_x0074_yneg0037_yawneg0074_seed0/trace_full_obs_footpos.jsonl | 25-49 | 0.0666 | 0.1878 | 0.0530 | 0.1598 | 2.5210 | 0.1105 | 52.0000 |
| d42903a0289e5df7 | published_policy_command_turning_x0074_yneg0037_yawneg0074_seed0/trace_full_obs_footpos.jsonl | 45-69 | 0.0659 | 0.1990 | 0.0554 | 0.1614 | 2.6433 | 0.1124 | 48.0000 |
| cdf0742213cec32e | published_policy_command_turning_x0074_yneg0037_yawneg0074_seed0/trace_full_obs_footpos.jsonl | 60-84 | 0.0700 | 0.1817 | 0.0496 | 0.1622 | 2.7356 | 0.1180 | 40.0000 |
| 1cccf693ab0fa4c6 | published_policy_command_turning_x0074_yneg0037_yawneg0074_seed0/trace_full_obs_footpos.jsonl | 65-89 | 0.0676 | 0.1817 | 0.0496 | 0.1622 | 2.5959 | 0.1139 | 44.0000 |
| f221d596e678fe12 | published_policy_command_turning_x0074_yneg0037_yawneg0074_seed0/trace_full_obs_footpos.jsonl | 70-94 | 0.0676 | 0.1817 | 0.0496 | 0.1622 | 2.5028 | 0.1167 | 48.0000 |
| 1ad3c389bf1b76a6 | published_policy_command_turning_x0074_yneg0037_yawneg0074_seed0/trace_full_obs_footpos.jsonl | 180-204 | 0.0660 | 0.1905 | 0.0496 | 0.1617 | 2.5575 | 0.1148 | 48.0000 |
| 11d8279e76eb184f | published_policy_command_turning_x0074_yneg0037_yawneg0074_seed0/trace_full_obs_footpos.jsonl | 190-214 | 0.0668 | 0.1986 | 0.0484 | 0.1617 | 2.5606 | 0.1181 | 52.0000 |
| 79ee7d9941806fe9 | published_policy_command_turning_x0074_yneg0037_yawneg0074_seed0/trace_full_obs_footpos.jsonl | 195-219 | 0.0668 | 0.1896 | 0.0484 | 0.1622 | 2.7519 | 0.1206 | 44.0000 |
| 4eaec00ba2c8b103 | published_policy_command_turning_x0074_yneg0037_yawneg0074_seed0/trace_full_obs_footpos.jsonl | 200-224 | 0.0654 | 0.1896 | 0.0472 | 0.1622 | 2.6940 | 0.1135 | 48.0000 |
| cbaa55534261fff5 | published_policy_command_turning_x0074_yneg0037_yawneg0074_seed0/trace_full_obs_footpos.jsonl | 205-229 | 0.0680 | 0.1896 | 0.0472 | 0.1622 | 2.6876 | 0.1170 | 52.0000 |
| a8f22990a26c74ae | published_policy_command_turning_x0074_yneg0037_yawneg0074_seed0/trace_full_obs_footpos.jsonl | 210-234 | 0.0696 | 0.1918 | 0.0467 | 0.1622 | 2.4990 | 0.1195 | 44.0000 |
| 8016f9bb259c02ca | published_policy_command_turning_x0074_yneg0037_yawneg0074_seed0/trace_full_obs_footpos.jsonl | 215-239 | 0.0728 | 0.1918 | 0.0492 | 0.1622 | 2.5042 | 0.1128 | 52.0000 |
| cee663ed770b2a8f | published_policy_command_turning_x0074_yneg0037_yawneg0074_seed0/trace_full_obs_footpos.jsonl | 220-244 | 0.0703 | 0.1604 | 0.0532 | 0.1621 | 2.5409 | 0.1114 | 48.0000 |
| 3c8c1f04345ad94c | published_policy_command_turning_x0074_yneg0037_yawneg0074_seed0/trace_full_obs_footpos.jsonl | 225-249 | 0.0689 | 0.1893 | 0.0532 | 0.1621 | 2.4153 | 0.1126 | 40.0000 |
| 8f36ca89d7d61432 | published_policy_command_turning_x0074_yneg0037_yawneg0074_seed1/trace_full_obs_footpos.jsonl | 125-149 | 0.0619 | 0.1852 | 0.0554 | 0.1600 | 2.4938 | 0.1121 | 52.0000 |
| 3e47c2ad779f8e92 | published_policy_command_turning_x0074_yneg0037_yawneg0074_seed1/trace_full_obs_footpos.jsonl | 135-159 | 0.0643 | 0.1855 | 0.0531 | 0.1600 | 2.4196 | 0.1167 | 52.0000 |
| 356c51cf8278338f | published_policy_command_turning_x0074_yneg0037_yawneg0074_seed1/trace_full_obs_footpos.jsonl | 140-164 | 0.0636 | 0.1796 | 0.0544 | 0.1616 | 2.5075 | 0.1118 | 44.0000 |
| 7a2fe9face1a395b | published_policy_command_turning_x0074_yneg0037_yawneg0074_seed1/trace_full_obs_footpos.jsonl | 145-169 | 0.0645 | 0.1993 | 0.0544 | 0.1616 | 2.3811 | 0.1134 | 44.0000 |
| cd4bad2cd833b154 | published_policy_command_turning_x0074_yneg0037_yawneg0074_seed1/trace_full_obs_footpos.jsonl | 150-174 | 0.0659 | 0.1993 | 0.0551 | 0.1616 | 2.4196 | 0.1172 | 52.0000 |
| 2b8c247c21cd8b13 | published_policy_command_turning_x0074_yneg0037_yawneg0074_seed1/trace_full_obs_footpos.jsonl | 165-189 | 0.0642 | 0.1932 | 0.0541 | 0.1620 | 2.6051 | 0.1128 | 52.0000 |
| b7e174807ee79a45 | published_policy_command_turning_x0074_yneg0037_yawneg0074_seed1/trace_full_obs_footpos.jsonl | 180-204 | 0.0662 | 0.1851 | 0.0512 | 0.1616 | 2.7260 | 0.1204 | 48.0000 |
| bf982c29963de4c0 | published_policy_command_turning_x0074_yneg0037_yawneg0074_seed1/trace_full_obs_footpos.jsonl | 185-209 | 0.0699 | 0.1899 | 0.0508 | 0.1616 | 2.3815 | 0.1143 | 44.0000 |
| 6ae28248d81c580c | published_policy_command_turning_x0074_yneg0037_yawneg0074_seed1/trace_full_obs_footpos.jsonl | 190-214 | 0.0714 | 0.1899 | 0.0514 | 0.1616 | 2.3626 | 0.1148 | 52.0000 |
| 8f06acbef59b1500 | published_policy_command_turning_x0074_yneg0037_yawneg0074_seed1/trace_full_obs_footpos.jsonl | 195-219 | 0.0706 | 0.1894 | 0.0514 | 0.1618 | 2.5487 | 0.1174 | 44.0000 |
| 6cb6a55db30d01ce | published_policy_command_turning_x0074_yneg0037_yawneg0074_seed1/trace_full_obs_footpos.jsonl | 200-224 | 0.0705 | 0.1894 | 0.0514 | 0.1618 | 2.4664 | 0.1147 | 48.0000 |
| fc3c119e20f50153 | published_policy_command_turning_x0074_yneg0037_yawneg0074_seed1/trace_full_obs_footpos.jsonl | 205-229 | 0.0716 | 0.1894 | 0.0514 | 0.1618 | 2.4267 | 0.1150 | 52.0000 |
| 4fa4e76b924187cd | published_policy_command_turning_x0074_yneg0037_yawneg0074_seed1/trace_full_obs_footpos.jsonl | 210-234 | 0.0685 | 0.1921 | 0.0514 | 0.1618 | 2.4459 | 0.1189 | 44.0000 |
| 045c469459b5ec3f | published_policy_command_turning_x0074_yneg0037_yawneg0074_seed1/trace_full_obs_footpos.jsonl | 215-239 | 0.0716 | 0.1921 | 0.0533 | 0.1618 | 2.5625 | 0.1169 | 52.0000 |
| d5b83ca68fea227a | published_policy_command_turning_x0074_yneg0037_yawneg0074_seed1/trace_full_obs_footpos.jsonl | 220-244 | 0.0698 | 0.1600 | 0.0569 | 0.1619 | 2.4459 | 0.1118 | 48.0000 |
| 701fd0f90b7d2163 | published_policy_command_turning_x0074_yneg0037_yawneg0074_seed1/trace_full_obs_footpos.jsonl | 225-249 | 0.0669 | 0.1849 | 0.0569 | 0.1619 | 2.3825 | 0.1132 | 40.0000 |
| 00a31f2e8b651ea9 | published_policy_command_turning_x0074_yneg0037_yawneg0074_seed2/trace_full_obs_footpos.jsonl | 0-24 | 0.1008 | 0.1331 | 0.0415 | 0.1510 | 2.7390 | 0.1181 | 52.0000 |
| 41461f3470545401 | published_policy_command_turning_x0074_yneg0037_yawneg0074_seed2/trace_full_obs_footpos.jsonl | 5-29 | 0.0809 | 0.1434 | 0.0532 | 0.1562 | 2.5848 | 0.1088 | 60.0000 |
| 4e25a751126182a6 | published_policy_command_turning_x0074_yneg0037_yawneg0074_seed2/trace_full_obs_footpos.jsonl | 85-109 | 0.0661 | 0.1580 | 0.0528 | 0.1618 | 2.7301 | 0.1141 | 48.0000 |
| 7188f3513c238f92 | published_policy_command_turning_x0074_yneg0037_yawneg0074_seed2/trace_full_obs_footpos.jsonl | 90-114 | 0.0663 | 0.1927 | 0.0528 | 0.1618 | 2.5381 | 0.1182 | 44.0000 |
| 7b15fedc9479ac23 | published_policy_command_turning_x0074_yneg0037_yawneg0074_seed2/trace_full_obs_footpos.jsonl | 95-119 | 0.0663 | 0.1927 | 0.0528 | 0.1618 | 2.6366 | 0.1202 | 52.0000 |
| b553df947d98ca42 | published_policy_command_turning_x0074_yneg0037_yawneg0074_seed2/trace_full_obs_footpos.jsonl | 100-124 | 0.0665 | 0.1890 | 0.0528 | 0.1618 | 2.7007 | 0.1182 | 44.0000 |
| ec496039bb66bbde | published_policy_command_turning_x0074_yneg0037_yawneg0074_seed2/trace_full_obs_footpos.jsonl | 105-129 | 0.0668 | 0.1917 | 0.0523 | 0.1618 | 2.3416 | 0.1159 | 48.0000 |
| 80ec09c7d95deb90 | published_policy_command_turning_x0074_yneg0037_yawneg0074_seed2/trace_full_obs_footpos.jsonl | 110-134 | 0.0670 | 0.1917 | 0.0550 | 0.1619 | 2.3842 | 0.1119 | 52.0000 |
| 9acd9a8c0cc463bd | published_policy_command_turning_x0074_yneg0037_yawneg0074_seed2/trace_full_obs_footpos.jsonl | 115-139 | 0.0666 | 0.1887 | 0.0550 | 0.1618 | 2.4574 | 0.1162 | 40.0000 |
| ef06af47206feff2 | published_policy_command_turning_x0074_yneg0037_yawneg0074_seed2/trace_full_obs_footpos.jsonl | 165-189 | 0.0660 | 0.1798 | 0.0515 | 0.1619 | 2.4868 | 0.1111 | 52.0000 |
| a486316d7505c9a5 | published_policy_command_turning_x0074_yneg0037_yawneg0074_seed2/trace_full_obs_footpos.jsonl | 170-194 | 0.0668 | 0.1886 | 0.0515 | 0.1620 | 2.4781 | 0.1120 | 40.0000 |
| d96ab56069a73385 | published_policy_command_turning_x0074_yneg0037_yawneg0074_seed2/trace_full_obs_footpos.jsonl | 180-204 | 0.0672 | 0.1867 | 0.0515 | 0.1620 | 2.4781 | 0.1121 | 44.0000 |
| 48486a76d0613616 | published_policy_command_turning_x0074_yneg0037_yawneg0074_seed2/trace_full_obs_footpos.jsonl | 210-234 | 0.0647 | 0.1952 | 0.0520 | 0.1614 | 2.5063 | 0.1159 | 44.0000 |
| e2e4c805a741f98e | published_policy_command_turning_x0074_yneg0037_yawneg0074_seed2/trace_full_obs_footpos.jsonl | 215-239 | 0.0662 | 0.1952 | 0.0520 | 0.1614 | 2.5327 | 0.1154 | 52.0000 |
| ea5efbf4a6d4d633 | published_policy_command_turning_x0074_yneg0037_yawneg0074_seed3/trace_full_obs_footpos.jsonl | 85-109 | 0.0691 | 0.1566 | 0.0511 | 0.1618 | 2.6075 | 0.1160 | 48.0000 |
| d1dafaa08132bfd5 | published_policy_command_turning_x0074_yneg0037_yawneg0074_seed3/trace_full_obs_footpos.jsonl | 90-114 | 0.0682 | 0.1877 | 0.0511 | 0.1618 | 2.5062 | 0.1186 | 44.0000 |
| c867bc23f7f64c5d | published_policy_command_turning_x0074_yneg0037_yawneg0074_seed3/trace_full_obs_footpos.jsonl | 95-119 | 0.0676 | 0.1877 | 0.0511 | 0.1618 | 2.5989 | 0.1196 | 52.0000 |
| bacbbe9178d58f44 | published_policy_command_turning_x0074_yneg0037_yawneg0074_seed3/trace_full_obs_footpos.jsonl | 100-124 | 0.0691 | 0.1860 | 0.0511 | 0.1618 | 2.5479 | 0.1194 | 44.0000 |
| 2160b36115d735aa | published_policy_command_turning_x0074_yneg0037_yawneg0074_seed3/trace_full_obs_footpos.jsonl | 105-129 | 0.0683 | 0.1885 | 0.0510 | 0.1618 | 2.3553 | 0.1163 | 48.0000 |
| c5e0a6aedcc0999e | published_policy_command_turning_x0074_yneg0037_yawneg0074_seed3/trace_full_obs_footpos.jsonl | 110-134 | 0.0692 | 0.1885 | 0.0517 | 0.1619 | 2.4028 | 0.1092 | 52.0000 |
| 955183901e3b5d8e | published_policy_command_turning_x0074_yneg0037_yawneg0074_seed3/trace_full_obs_footpos.jsonl | 115-139 | 0.0692 | 0.1876 | 0.0517 | 0.1620 | 2.4511 | 0.1155 | 40.0000 |
| 4798ce3f56c5c4c7 | published_policy_command_turning_x0074_yneg0037_yawneg0074_seed3/trace_full_obs_footpos.jsonl | 120-144 | 0.0679 | 0.1876 | 0.0517 | 0.1620 | 2.4891 | 0.1127 | 48.0000 |
| dc58548c291a1447 | published_policy_command_turning_x0074_yneg0037_yawneg0074_seed3/trace_full_obs_footpos.jsonl | 125-149 | 0.0674 | 0.1876 | 0.0517 | 0.1620 | 2.4783 | 0.1071 | 48.0000 |
| 8d4b300844541e1e | published_policy_command_turning_x0074_yneg0037_yawneg0074_seed3/trace_full_obs_footpos.jsonl | 135-159 | 0.0684 | 0.1874 | 0.0509 | 0.1620 | 2.3417 | 0.1161 | 48.0000 |
| 2699a56f50a5c950 | published_policy_command_turning_x0074_yneg0037_yawneg0074_seed3/trace_full_obs_footpos.jsonl | 140-164 | 0.0670 | 0.1714 | 0.0538 | 0.1615 | 2.5885 | 0.1120 | 44.0000 |
| b95af764eab4cca8 | published_policy_command_turning_x0074_yneg0037_yawneg0074_seed3/trace_full_obs_footpos.jsonl | 180-204 | 0.0679 | 0.1878 | 0.0509 | 0.1615 | 2.5824 | 0.1166 | 48.0000 |
| 16def8f55ee8d659 | published_policy_command_turning_x0074_yneg0037_yawneg0074_seed3/trace_full_obs_footpos.jsonl | 185-209 | 0.0673 | 0.1956 | 0.0509 | 0.1615 | 2.3758 | 0.1144 | 44.0000 |
| ac3b3871e6bcb1ca | published_policy_command_turning_x0074_yneg0037_yawneg0074_seed3/trace_full_obs_footpos.jsonl | 190-214 | 0.0683 | 0.1956 | 0.0531 | 0.1615 | 2.3587 | 0.1160 | 52.0000 |
| 76bbb132e7a60444 | published_policy_command_turning_x0074_yneg0037_yawneg0074_seed3/trace_full_obs_footpos.jsonl | 195-219 | 0.0673 | 0.1887 | 0.0531 | 0.1619 | 2.6038 | 0.1182 | 40.0000 |
| 842698a4cd0f2c38 | published_policy_command_turning_x0074_yneg0037_yawneg0074_seed3/trace_full_obs_footpos.jsonl | 200-224 | 0.0676 | 0.1887 | 0.0531 | 0.1619 | 2.4257 | 0.1114 | 44.0000 |
| 8ed31141c563512f | published_policy_command_turning_x0074_yneg0037_yawneg0074_seed3/trace_full_obs_footpos.jsonl | 205-229 | 0.0684 | 0.1887 | 0.0531 | 0.1619 | 2.4528 | 0.1143 | 48.0000 |
| 31a711be62990146 | published_policy_command_turning_x0074_yneg0037_yawneg0074_seed3/trace_full_obs_footpos.jsonl | 215-239 | 0.0682 | 0.1887 | 0.0518 | 0.1619 | 2.5245 | 0.1159 | 48.0000 |
| cf45a9a60fda1296 | published_policy_command_turning_x0074_yneg0037_yawneg0074_seed3/trace_full_obs_footpos.jsonl | 220-244 | 0.0680 | 0.1598 | 0.0524 | 0.1619 | 2.4443 | 0.1119 | 48.0000 |
| 1a2aff565d53199c | published_policy_command_turning_x0074_yneg0037_yawneg0074_seed4/trace_full_obs_footpos.jsonl | 0-24 | 0.0831 | 0.1516 | 0.0802 | 0.1506 | 3.3980 | 0.1271 | 76.0000 |
| 83ce79ca7d4ea96a | published_policy_command_turning_x0074_yneg0037_yawneg0074_seed4/trace_full_obs_footpos.jsonl | 5-29 | 0.0561 | 0.1516 | 0.0800 | 0.1617 | 2.4211 | 0.0921 | 84.0000 |
| 1872bb12a15be923 | published_policy_command_turning_x0074_yneg0037_yawneg0074_seed5/trace_full_obs_footpos.jsonl | 20-44 | 0.0686 | 0.1659 | 0.0450 | 0.1589 | 3.0257 | 0.1262 | 40.0000 |
| 9a85024a907f6284 | published_policy_command_turning_x0074_yneg0037_yawneg0074_seed5/trace_full_obs_footpos.jsonl | 25-49 | 0.0744 | 0.1659 | 0.0478 | 0.1589 | 2.8157 | 0.1209 | 56.0000 |
| 56c87dee7ada7ba5 | published_policy_command_turning_x0074_yneg0037_yawneg0074_seed5/trace_full_obs_footpos.jsonl | 30-54 | 0.0699 | 0.1526 | 0.0543 | 0.1608 | 2.7049 | 0.1195 | 52.0000 |
| 1c591a8dde1e676a | published_policy_command_turning_x0074_yneg0037_yawneg0074_seed5/trace_full_obs_footpos.jsonl | 55-79 | 0.0664 | 0.1971 | 0.0485 | 0.1606 | 2.5542 | 0.1160 | 52.0000 |
| b1ec67b942c92a54 | published_policy_command_turning_x0074_yneg0037_yawneg0074_seed5/trace_full_obs_footpos.jsonl | 60-84 | 0.0667 | 0.1945 | 0.0485 | 0.1618 | 2.7177 | 0.1192 | 44.0000 |
| 698e2e8ef451384b | published_policy_command_turning_x0074_yneg0037_yawneg0074_seed5/trace_full_obs_footpos.jsonl | 70-94 | 0.0668 | 0.1945 | 0.0482 | 0.1618 | 2.7084 | 0.1183 | 52.0000 |
| ae5afe7acf9298f4 | published_policy_command_turning_x0074_yneg0037_yawneg0074_seed5/trace_full_obs_footpos.jsonl | 80-104 | 0.0683 | 0.1936 | 0.0484 | 0.1618 | 2.4914 | 0.1145 | 52.0000 |
| 6833fb4d7aecf7b1 | published_policy_command_turning_x0074_yneg0037_yawneg0074_seed5/trace_full_obs_footpos.jsonl | 85-109 | 0.0663 | 0.1594 | 0.0534 | 0.1619 | 2.5021 | 0.1109 | 48.0000 |
| 1a98e177d40cd0db | published_policy_command_turning_x0074_yneg0037_yawneg0074_seed5/trace_full_obs_footpos.jsonl | 90-114 | 0.0660 | 0.1881 | 0.0534 | 0.1619 | 2.3432 | 0.1126 | 40.0000 |
| bfee9ee409e19da2 | published_policy_command_turning_x0074_yneg0037_yawneg0074_seed5/trace_full_obs_footpos.jsonl | 105-129 | 0.0659 | 0.1884 | 0.0530 | 0.1619 | 2.2850 | 0.1117 | 44.0000 |
| 43c8acfd76d94e1e | published_policy_command_turning_x0074_yneg0037_yawneg0074_seed5/trace_full_obs_footpos.jsonl | 110-134 | 0.0666 | 0.1884 | 0.0521 | 0.1620 | 2.2850 | 0.1049 | 48.0000 |
| ea0a0799d9692ede | published_policy_command_turning_x0074_yneg0037_yawneg0074_seed5/trace_full_obs_footpos.jsonl | 115-139 | 0.0668 | 0.1999 | 0.0521 | 0.1611 | 2.3773 | 0.1145 | 44.0000 |
| 296861383a4d9192 | published_policy_command_turning_x0074_yneg0037_yawneg0074_seed5/trace_full_obs_footpos.jsonl | 175-199 | 0.0664 | 0.1904 | 0.0470 | 0.1620 | 2.7023 | 0.1182 | 52.0000 |
| 944b90900a69a25b | published_policy_command_turning_x0074_yneg0037_yawneg0074_seed5/trace_full_obs_footpos.jsonl | 180-204 | 0.0683 | 0.1865 | 0.0495 | 0.1620 | 2.6104 | 0.1143 | 48.0000 |
| a17c8a24af241132 | published_policy_command_turning_x0074_yneg0037_yawneg0074_seed5/trace_full_obs_footpos.jsonl | 185-209 | 0.0706 | 0.1887 | 0.0504 | 0.1620 | 2.3524 | 0.1137 | 44.0000 |
| c2b13c20ad1fb393 | published_policy_command_turning_x0074_yneg0037_yawneg0074_seed5/trace_full_obs_footpos.jsonl | 190-214 | 0.0720 | 0.1887 | 0.0571 | 0.1620 | 2.3657 | 0.1176 | 52.0000 |
| 669aa233dff03406 | published_policy_command_turning_x0074_yneg0037_yawneg0074_seed5/trace_full_obs_footpos.jsonl | 195-219 | 0.0698 | 0.1917 | 0.0571 | 0.1614 | 2.4581 | 0.1203 | 44.0000 |
| 3cee10f3b17c3f99 | published_policy_command_turning_x0074_yneg0037_yawneg0074_seed5/trace_full_obs_footpos.jsonl | 200-224 | 0.0660 | 0.1917 | 0.0571 | 0.1614 | 2.4693 | 0.1178 | 48.0000 |
| d77a2c6e4e06c8cc | published_policy_command_turning_x0074_yneg0037_yawneg0074_seed5/trace_full_obs_footpos.jsonl | 205-229 | 0.0668 | 0.1917 | 0.0571 | 0.1614 | 2.4693 | 0.1189 | 52.0000 |
| 71f223c7d94758d7 | published_policy_command_turning_x0074_yneg0037_yawneg0074_seed6/trace_full_obs_footpos.jsonl | 15-39 | 0.0668 | 0.1694 | 0.0570 | 0.1580 | 2.6426 | 0.1239 | 64.0000 |
| 8ef6a65bcad7f797 | published_policy_command_turning_x0074_yneg0037_yawneg0074_seed6/trace_full_obs_footpos.jsonl | 25-49 | 0.0699 | 0.1744 | 0.0570 | 0.1580 | 2.5772 | 0.1188 | 60.0000 |
| 5f578cb578671b82 | published_policy_command_turning_x0074_yneg0037_yawneg0074_seed6/trace_full_obs_footpos.jsonl | 30-54 | 0.0695 | 0.1497 | 0.0579 | 0.1607 | 2.4756 | 0.1138 | 56.0000 |
| b8eb4cdfb75905e2 | published_policy_command_turning_x0074_yneg0037_yawneg0074_seed6/trace_full_obs_footpos.jsonl | 60-84 | 0.0699 | 0.1989 | 0.0520 | 0.1623 | 2.7254 | 0.1189 | 40.0000 |
| b1f1f965d06731fa | published_policy_command_turning_x0074_yneg0037_yawneg0074_seed6/trace_full_obs_footpos.jsonl | 65-89 | 0.0679 | 0.1989 | 0.0520 | 0.1623 | 2.6333 | 0.1125 | 44.0000 |
| 51d4af454e83d42b | published_policy_command_turning_x0074_yneg0037_yawneg0074_seed6/trace_full_obs_footpos.jsonl | 70-94 | 0.0685 | 0.1989 | 0.0521 | 0.1623 | 2.6813 | 0.1156 | 48.0000 |
| d9e5724efb038fdf | published_policy_command_turning_x0074_yneg0037_yawneg0074_seed6/trace_full_obs_footpos.jsonl | 75-99 | 0.0671 | 0.1849 | 0.0521 | 0.1623 | 2.6034 | 0.1191 | 40.0000 |
| f1cd7b546f6e78fa | published_policy_command_turning_x0074_yneg0037_yawneg0074_seed6/trace_full_obs_footpos.jsonl | 100-124 | 0.0678 | 0.1820 | 0.0491 | 0.1620 | 2.5854 | 0.1171 | 44.0000 |
| 7bf54327b89231d6 | published_policy_command_turning_x0074_yneg0037_yawneg0074_seed6/trace_full_obs_footpos.jsonl | 105-129 | 0.0722 | 0.1882 | 0.0496 | 0.1620 | 2.3637 | 0.1131 | 48.0000 |
| 3284876ba9e57e52 | published_policy_command_turning_x0074_yneg0037_yawneg0074_seed6/trace_full_obs_footpos.jsonl | 110-134 | 0.0728 | 0.1882 | 0.0555 | 0.1620 | 2.4539 | 0.1119 | 52.0000 |
| 1761f99e17e4c6d1 | published_policy_command_turning_x0074_yneg0037_yawneg0074_seed6/trace_full_obs_footpos.jsonl | 115-139 | 0.0714 | 0.1878 | 0.0555 | 0.1623 | 2.5185 | 0.1172 | 40.0000 |
| f172f04ea24a7b38 | published_policy_command_turning_x0074_yneg0037_yawneg0074_seed6/trace_full_obs_footpos.jsonl | 155-179 | 0.0685 | 0.1899 | 0.0475 | 0.1619 | 2.5232 | 0.1162 | 40.0000 |
| 8aea80e99f6f7b36 | published_policy_command_turning_x0074_yneg0037_yawneg0074_seed6/trace_full_obs_footpos.jsonl | 160-184 | 0.0734 | 0.1899 | 0.0494 | 0.1619 | 2.4946 | 0.1134 | 48.0000 |
| 1a1eb44f868921da | published_policy_command_turning_x0074_yneg0037_yawneg0074_seed6/trace_full_obs_footpos.jsonl | 165-189 | 0.0715 | 0.1707 | 0.0550 | 0.1623 | 2.4946 | 0.1121 | 48.0000 |
| a27be49a7cf9d4ee | published_policy_command_turning_x0074_yneg0037_yawneg0074_seed6/trace_full_obs_footpos.jsonl | 170-194 | 0.0692 | 0.1807 | 0.0550 | 0.1620 | 2.4926 | 0.1135 | 40.0000 |
| 6ffc3cb9fd53f8d7 | published_policy_command_turning_x0074_yneg0037_yawneg0074_seed6/trace_full_obs_footpos.jsonl | 180-204 | 0.0684 | 0.1775 | 0.0550 | 0.1620 | 2.5910 | 0.1140 | 44.0000 |
| c2cb256b5ddd7eaf | published_policy_command_turning_x0074_yneg0037_yawneg0074_seed6/trace_full_obs_footpos.jsonl | 190-214 | 0.0674 | 0.1940 | 0.0529 | 0.1620 | 2.3725 | 0.1146 | 48.0000 |
| 09e08bf7b66429a7 | published_policy_command_turning_x0074_yneg0037_yawneg0074_seed6/trace_full_obs_footpos.jsonl | 195-219 | 0.0679 | 0.1939 | 0.0529 | 0.1620 | 2.5570 | 0.1149 | 40.0000 |
| cd7b6b24e5cde638 | published_policy_command_turning_x0074_yneg0037_yawneg0074_seed7/trace_full_obs_footpos.jsonl | 35-59 | 0.0661 | 0.1861 | 0.0541 | 0.1620 | 2.3223 | 0.1121 | 40.0000 |
| 158af48ab56eb484 | published_policy_command_turning_x0074_yneg0037_yawneg0074_seed7/trace_full_obs_footpos.jsonl | 45-69 | 0.0649 | 0.1860 | 0.0541 | 0.1620 | 2.4920 | 0.1119 | 44.0000 |
| 0e4fad59f9885de7 | published_policy_command_turning_x0074_yneg0037_yawneg0074_seed7/trace_full_obs_footpos.jsonl | 140-164 | 0.0682 | 0.1779 | 0.0513 | 0.1621 | 2.7307 | 0.1138 | 44.0000 |
| 2edc949d8a795196 | published_policy_command_turning_x0074_yneg0037_yawneg0074_seed7/trace_full_obs_footpos.jsonl | 145-169 | 0.0667 | 0.1865 | 0.0513 | 0.1621 | 2.6209 | 0.1138 | 40.0000 |
| aa998a3444c34271 | published_policy_command_turning_x0074_yneg0037_yawneg0074_seed7/trace_full_obs_footpos.jsonl | 150-174 | 0.0658 | 0.1865 | 0.0513 | 0.1621 | 2.6438 | 0.1171 | 48.0000 |
| fb8ba1c1993fb1bf | published_policy_command_turning_x0074_yneg0037_yawneg0074_seed7/trace_full_obs_footpos.jsonl | 155-179 | 0.0657 | 0.1950 | 0.0513 | 0.1621 | 2.6278 | 0.1171 | 40.0000 |
| 514b59c8eb98e2ef | published_policy_command_turning_x0074_yneg0037_yawneg0074_seed7/trace_full_obs_footpos.jsonl | 160-184 | 0.0665 | 0.1950 | 0.0501 | 0.1621 | 2.5717 | 0.1129 | 48.0000 |
| 02f6e74643b6a0e8 | published_policy_command_turning_x0074_yneg0037_yawneg0074_seed7/trace_full_obs_footpos.jsonl | 165-189 | 0.0668 | 0.1914 | 0.0532 | 0.1625 | 2.4132 | 0.1099 | 48.0000 |
| 8845413504b7aa55 | published_policy_command_turning_x0074_yneg0037_yawneg0074_seed7/trace_full_obs_footpos.jsonl | 170-194 | 0.0671 | 0.1943 | 0.0532 | 0.1621 | 2.4995 | 0.1136 | 40.0000 |
| c64cc18795dcc2d0 | published_policy_command_turning_x0074_yneg0037_yawneg0074_seed7/trace_full_obs_footpos.jsonl | 175-199 | 0.0660 | 0.1943 | 0.0532 | 0.1621 | 2.6102 | 0.1137 | 48.0000 |
| 16813c484ad65311 | published_policy_command_turning_x0074_yneg0037_yawneg0074_seed7/trace_full_obs_footpos.jsonl | 180-204 | 0.0678 | 0.1782 | 0.0532 | 0.1621 | 2.6102 | 0.1128 | 44.0000 |
| 1c9847a9ddd2369d | published_policy_command_turning_x0074_yneg0037_yawneg0074_seed7/trace_full_obs_footpos.jsonl | 220-244 | 0.0657 | 0.1604 | 0.0524 | 0.1620 | 2.5490 | 0.1097 | 48.0000 |
| c2ee8a7691c23793 | published_policy_command_turning_x0074_yneg0037_yawneg0074_seed7/trace_full_obs_footpos.jsonl | 225-249 | 0.0671 | 0.1861 | 0.0524 | 0.1620 | 2.4114 | 0.1118 | 40.0000 |

## Gate

- This manifest is only seed material for a future supervised/imitation experiment.
- Do not train until the manifest and source skew are reviewed.
- Do not commit raw JSONL traces unless explicitly approved.
