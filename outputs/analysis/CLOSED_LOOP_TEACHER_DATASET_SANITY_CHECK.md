# Target Dataset Sanity Check

status: `PASS_TARGET_DATASET_SANITY_CHECK`

This check recomputes compact window metrics from local source traces.
It does not copy raw traces and does not start training.

## Summary

- manifest: `outputs/analysis/closed_loop_teacher_dataset_manifest.json`
- dataset_id: `407af2cbe0ad69e1`
- entries_checked: `259`
- entries_with_errors: `0`
- bc_ready_entries: `259`
- bc_readiness_status: `PASS_TARGET_DATASET_BC_READY`
- source_files: `16`
- max_source_fraction: `0.0772`

## Warnings

- none

## Entry Results

| id | source | ticks | errors | vx | vy95 | pitch95 | height | sent_vel95 | track95 |
|---|---|---|---|---:|---:|---:|---:|---:|---:|
| f37609b92540c062 | published_policy_command_straight_x008_seed0/trace_full_obs_footpos.jsonl | 0-24 | `none` | 0.0929 | 0.1398 | 0.0566 | 0.1521 | 3.3088 | 0.1392 |
| efb0142fda8ea513 | published_policy_command_straight_x008_seed0/trace_full_obs_footpos.jsonl | 5-29 | `none` | 0.0833 | 0.1742 | 0.0569 | 0.1591 | 2.5879 | 0.1269 |
| 01e26046657431dd | published_policy_command_straight_x008_seed0/trace_full_obs_footpos.jsonl | 10-34 | `none` | 0.0702 | 0.1793 | 0.0569 | 0.1591 | 2.4700 | 0.1255 |
| bf1753d2ff960d6b | published_policy_command_straight_x008_seed0/trace_full_obs_footpos.jsonl | 15-39 | `none` | 0.0739 | 0.1793 | 0.0611 | 0.1591 | 2.5002 | 0.1255 |
| f92727366f21ba08 | published_policy_command_straight_x008_seed0/trace_full_obs_footpos.jsonl | 55-79 | `none` | 0.0713 | 0.1934 | 0.0528 | 0.1619 | 2.3807 | 0.1228 |
| 22fc98298f4db958 | published_policy_command_straight_x008_seed0/trace_full_obs_footpos.jsonl | 75-99 | `none` | 0.0713 | 0.1997 | 0.0558 | 0.1625 | 2.3184 | 0.1208 |
| eea437c6ddde3ab9 | published_policy_command_straight_x008_seed0/trace_full_obs_footpos.jsonl | 80-104 | `none` | 0.0755 | 0.1997 | 0.0558 | 0.1625 | 2.4428 | 0.1154 |
| 615f08cfe8cc5f1b | published_policy_command_straight_x008_seed0/trace_full_obs_footpos.jsonl | 85-109 | `none` | 0.0743 | 0.1812 | 0.0558 | 0.1632 | 2.4038 | 0.1079 |
| 4bc4a800bdf7dc86 | published_policy_command_straight_x008_seed0/trace_full_obs_footpos.jsonl | 90-114 | `none` | 0.0719 | 0.1924 | 0.0558 | 0.1632 | 2.3507 | 0.1114 |
| a1fc601dd81e5b9e | published_policy_command_straight_x008_seed0/trace_full_obs_footpos.jsonl | 95-119 | `none` | 0.0702 | 0.1924 | 0.0558 | 0.1632 | 2.3858 | 0.1154 |
| 10af3494016a2d22 | published_policy_command_straight_x008_seed0/trace_full_obs_footpos.jsonl | 100-124 | `none` | 0.0716 | 0.1691 | 0.0528 | 0.1626 | 2.3619 | 0.1096 |
| 74724745ec8ce987 | published_policy_command_straight_x008_seed0/trace_full_obs_footpos.jsonl | 105-129 | `none` | 0.0705 | 0.1895 | 0.0534 | 0.1621 | 2.1011 | 0.1072 |
| e7dabf3836aafff2 | published_policy_command_straight_x008_seed0/trace_full_obs_footpos.jsonl | 110-134 | `none` | 0.0718 | 0.1895 | 0.0567 | 0.1621 | 2.1831 | 0.1028 |
| 0cb7dd4c7abbd72e | published_policy_command_straight_x008_seed0/trace_full_obs_footpos.jsonl | 115-139 | `none` | 0.0714 | 0.1980 | 0.0567 | 0.1621 | 2.4002 | 0.1122 |
| a5b62495fea889bc | published_policy_command_straight_x008_seed0/trace_full_obs_footpos.jsonl | 125-149 | `none` | 0.0711 | 0.1942 | 0.0567 | 0.1621 | 2.4691 | 0.1097 |
| 83d140649f25e2c3 | published_policy_command_straight_x008_seed0/trace_full_obs_footpos.jsonl | 145-169 | `none` | 0.0704 | 0.1837 | 0.0530 | 0.1618 | 2.5163 | 0.1170 |
| 0eed75a9566b489e | published_policy_command_straight_x008_seed0/trace_full_obs_footpos.jsonl | 215-239 | `none` | 0.0723 | 0.1944 | 0.0507 | 0.1622 | 2.4908 | 0.1221 |
| 6de06dfdc77a261a | published_policy_command_straight_x008_seed0/trace_full_obs_footpos.jsonl | 220-244 | `none` | 0.0711 | 0.1820 | 0.0507 | 0.1622 | 2.4941 | 0.1131 |
| 23821e629bdbd5ad | published_policy_command_straight_x008_seed1/trace_full_obs_footpos.jsonl | 95-119 | `none` | 0.0716 | 0.1899 | 0.0555 | 0.1619 | 2.5100 | 0.1208 |
| 8d784409a13d3442 | published_policy_command_straight_x008_seed1/trace_full_obs_footpos.jsonl | 100-124 | `none` | 0.0753 | 0.1805 | 0.0531 | 0.1619 | 2.4991 | 0.1197 |
| 2c19e1e712f5f642 | published_policy_command_straight_x008_seed1/trace_full_obs_footpos.jsonl | 105-129 | `none` | 0.0766 | 0.1888 | 0.0529 | 0.1619 | 2.1702 | 0.1182 |
| 939a7f5647762038 | published_policy_command_straight_x008_seed1/trace_full_obs_footpos.jsonl | 110-134 | `none` | 0.0767 | 0.1888 | 0.0529 | 0.1619 | 2.2148 | 0.1137 |
| 71b8c9ea6dc72687 | published_policy_command_straight_x008_seed1/trace_full_obs_footpos.jsonl | 115-139 | `none` | 0.0729 | 0.1891 | 0.0529 | 0.1625 | 2.5154 | 0.1213 |
| 8f3e2c85e3e59718 | published_policy_command_straight_x008_seed1/trace_full_obs_footpos.jsonl | 120-144 | `none` | 0.0698 | 0.1891 | 0.0529 | 0.1625 | 2.5154 | 0.1205 |
| 2399c044147b26a2 | published_policy_command_straight_x008_seed1/trace_full_obs_footpos.jsonl | 125-149 | `none` | 0.0718 | 0.1862 | 0.0526 | 0.1625 | 2.5154 | 0.1113 |
| 13bfddf22b85d6f1 | published_policy_command_straight_x008_seed1/trace_full_obs_footpos.jsonl | 135-159 | `none` | 0.0728 | 0.1906 | 0.0513 | 0.1622 | 2.3077 | 0.1223 |
| 1a7a44c103ef6c8a | published_policy_command_straight_x008_seed1/trace_full_obs_footpos.jsonl | 140-164 | `none` | 0.0728 | 0.1791 | 0.0513 | 0.1622 | 2.5031 | 0.1170 |
| 5148e0b384c1d978 | published_policy_command_straight_x008_seed1/trace_full_obs_footpos.jsonl | 170-194 | `none` | 0.0704 | 0.1966 | 0.0527 | 0.1621 | 2.4713 | 0.1178 |
| c905ecb0e687258d | published_policy_command_straight_x008_seed1/trace_full_obs_footpos.jsonl | 180-204 | `none` | 0.0707 | 0.1647 | 0.0530 | 0.1623 | 2.5397 | 0.1158 |
| 857ac468857d986b | published_policy_command_straight_x008_seed1/trace_full_obs_footpos.jsonl | 185-209 | `none` | 0.0710 | 0.1950 | 0.0538 | 0.1622 | 2.1827 | 0.1130 |
| 4bd45625edcbac8b | published_policy_command_straight_x008_seed1/trace_full_obs_footpos.jsonl | 190-214 | `none` | 0.0708 | 0.1950 | 0.0538 | 0.1622 | 2.3419 | 0.1158 |
| 87802874d6fba95b | published_policy_command_straight_x008_seed1/trace_full_obs_footpos.jsonl | 195-219 | `none` | 0.0705 | 0.1851 | 0.0538 | 0.1620 | 2.5418 | 0.1176 |
| 4efe0ec69600b4f4 | published_policy_command_straight_x008_seed1/trace_full_obs_footpos.jsonl | 200-224 | `none` | 0.0725 | 0.1851 | 0.0538 | 0.1620 | 2.5418 | 0.1140 |
| a067ad734ee2accb | published_policy_command_straight_x008_seed1/trace_full_obs_footpos.jsonl | 205-229 | `none` | 0.0739 | 0.1851 | 0.0538 | 0.1620 | 2.5418 | 0.1162 |
| d5292669cc847420 | published_policy_command_straight_x008_seed1/trace_full_obs_footpos.jsonl | 210-234 | `none` | 0.0729 | 0.1853 | 0.0508 | 0.1620 | 2.5624 | 0.1280 |
| 7ddfbac3908c51ea | published_policy_command_straight_x008_seed1/trace_full_obs_footpos.jsonl | 215-239 | `none` | 0.0779 | 0.1853 | 0.0489 | 0.1620 | 2.5624 | 0.1267 |
| 89afd8643b6fb92e | published_policy_command_straight_x008_seed1/trace_full_obs_footpos.jsonl | 220-244 | `none` | 0.0792 | 0.1728 | 0.0489 | 0.1625 | 2.5462 | 0.1201 |
| 192f6a837778e423 | published_policy_command_straight_x008_seed1/trace_full_obs_footpos.jsonl | 225-249 | `none` | 0.0757 | 0.1950 | 0.0489 | 0.1625 | 2.4868 | 0.1262 |
| cdbf9aa30a8d6dfa | published_policy_command_straight_x008_seed2/trace_full_obs_footpos.jsonl | 5-29 | `none` | 0.0944 | 0.1618 | 0.0329 | 0.1598 | 2.6524 | 0.1192 |
| 640a4a7438aebb21 | published_policy_command_straight_x008_seed2/trace_full_obs_footpos.jsonl | 10-34 | `none` | 0.0809 | 0.1618 | 0.0369 | 0.1598 | 2.5406 | 0.1220 |
| 80565b791cfadd24 | published_policy_command_straight_x008_seed2/trace_full_obs_footpos.jsonl | 15-39 | `none` | 0.0787 | 0.1608 | 0.0524 | 0.1598 | 2.5406 | 0.1304 |
| df6f466361dfae1a | published_policy_command_straight_x008_seed2/trace_full_obs_footpos.jsonl | 20-44 | `none` | 0.0722 | 0.1907 | 0.0524 | 0.1598 | 2.4086 | 0.1252 |
| 9456c60649711b45 | published_policy_command_straight_x008_seed2/trace_full_obs_footpos.jsonl | 25-49 | `none` | 0.0726 | 0.1907 | 0.0535 | 0.1598 | 2.5387 | 0.1247 |
| 9cae163a529de146 | published_policy_command_straight_x008_seed2/trace_full_obs_footpos.jsonl | 30-54 | `none` | 0.0720 | 0.1867 | 0.0535 | 0.1620 | 2.5601 | 0.1220 |
| 11f378cdaf016498 | published_policy_command_straight_x008_seed2/trace_full_obs_footpos.jsonl | 45-69 | `none` | 0.0746 | 0.1606 | 0.0532 | 0.1623 | 2.3263 | 0.1188 |
| bbbed64f5186f3a8 | published_policy_command_straight_x008_seed2/trace_full_obs_footpos.jsonl | 50-74 | `none` | 0.0713 | 0.1935 | 0.0541 | 0.1623 | 2.2537 | 0.1118 |
| 4821116a12707ff9 | published_policy_command_straight_x008_seed2/trace_full_obs_footpos.jsonl | 55-79 | `none` | 0.0723 | 0.1935 | 0.0541 | 0.1623 | 2.3118 | 0.1149 |
| 2298ced25f24f2ec | published_policy_command_straight_x008_seed2/trace_full_obs_footpos.jsonl | 60-84 | `none` | 0.0709 | 0.1852 | 0.0541 | 0.1619 | 2.5155 | 0.1189 |
| 9d66d814521597c2 | published_policy_command_straight_x008_seed2/trace_full_obs_footpos.jsonl | 135-159 | `none` | 0.0714 | 0.1888 | 0.0534 | 0.1621 | 2.4056 | 0.1244 |
| d5df1f1c474901c4 | published_policy_command_straight_x008_seed2/trace_full_obs_footpos.jsonl | 140-164 | `none` | 0.0706 | 0.1801 | 0.0534 | 0.1621 | 2.5681 | 0.1204 |
| b7aa1550498f5a67 | published_policy_command_straight_x008_seed2/trace_full_obs_footpos.jsonl | 170-194 | `none` | 0.0709 | 0.1877 | 0.0509 | 0.1621 | 2.3547 | 0.1144 |
| 17886120cd1fb6d4 | published_policy_command_straight_x008_seed2/trace_full_obs_footpos.jsonl | 175-199 | `none` | 0.0713 | 0.1877 | 0.0512 | 0.1621 | 2.4145 | 0.1185 |
| 1e28fa01db8bab0a | published_policy_command_straight_x008_seed2/trace_full_obs_footpos.jsonl | 180-204 | `none` | 0.0734 | 0.1622 | 0.0512 | 0.1621 | 2.5292 | 0.1116 |
| b1e10084cb25b5cc | published_policy_command_straight_x008_seed2/trace_full_obs_footpos.jsonl | 190-214 | `none` | 0.0732 | 0.1880 | 0.0536 | 0.1621 | 2.3125 | 0.1232 |
| 35f9bf6d35a7b51c | published_policy_command_straight_x008_seed2/trace_full_obs_footpos.jsonl | 195-219 | `none` | 0.0709 | 0.1982 | 0.0536 | 0.1623 | 2.4938 | 0.1263 |
| c25c95fa14d1b084 | published_policy_command_straight_x008_seed3/trace_full_obs_footpos.jsonl | 80-104 | `none` | 0.0700 | 0.1930 | 0.0528 | 0.1617 | 2.4385 | 0.1186 |
| 36850df413335621 | published_policy_command_straight_x008_seed3/trace_full_obs_footpos.jsonl | 85-109 | `none` | 0.0695 | 0.1714 | 0.0528 | 0.1624 | 2.4605 | 0.1067 |
| 61d3dbdd436ffa9d | published_policy_command_straight_x008_seed3/trace_full_obs_footpos.jsonl | 90-114 | `none` | 0.0700 | 0.1902 | 0.0528 | 0.1624 | 2.4237 | 0.1164 |
| 326a1f0a185f4aff | published_policy_command_straight_x008_seed3/trace_full_obs_footpos.jsonl | 100-124 | `none` | 0.0703 | 0.1723 | 0.0495 | 0.1624 | 2.4342 | 0.1176 |
| 80225f34b93facc8 | published_policy_command_straight_x008_seed3/trace_full_obs_footpos.jsonl | 105-129 | `none` | 0.0723 | 0.1898 | 0.0491 | 0.1624 | 2.2395 | 0.1168 |
| 26ca1912e2d0cdf2 | published_policy_command_straight_x008_seed3/trace_full_obs_footpos.jsonl | 110-134 | `none` | 0.0740 | 0.1898 | 0.0496 | 0.1624 | 2.4323 | 0.1146 |
| da3507fc1ea733e3 | published_policy_command_straight_x008_seed3/trace_full_obs_footpos.jsonl | 125-149 | `none` | 0.0726 | 0.1965 | 0.0517 | 0.1622 | 2.4586 | 0.1127 |
| 631de4e388f78e2e | published_policy_command_straight_x008_seed3/trace_full_obs_footpos.jsonl | 140-164 | `none` | 0.0694 | 0.1760 | 0.0525 | 0.1616 | 2.4671 | 0.1101 |
| 2afb404c91e69f97 | published_policy_command_straight_x008_seed3/trace_full_obs_footpos.jsonl | 145-169 | `none` | 0.0711 | 0.1822 | 0.0525 | 0.1616 | 2.3867 | 0.1127 |
| d066bb0055814254 | published_policy_command_straight_x008_seed3/trace_full_obs_footpos.jsonl | 150-174 | `none` | 0.0714 | 0.1822 | 0.0530 | 0.1616 | 2.4896 | 0.1210 |
| d41648c3e9171bbc | published_policy_command_straight_x008_seed3/trace_full_obs_footpos.jsonl | 155-179 | `none` | 0.0709 | 0.1822 | 0.0528 | 0.1616 | 2.4984 | 0.1219 |
| 543101d18b449cf3 | published_policy_command_straight_x008_seed3/trace_full_obs_footpos.jsonl | 160-184 | `none` | 0.0706 | 0.1822 | 0.0529 | 0.1616 | 2.4793 | 0.1210 |
| 6618d5b2b3cf4ce6 | published_policy_command_straight_x008_seed3/trace_full_obs_footpos.jsonl | 165-189 | `none` | 0.0715 | 0.1822 | 0.0529 | 0.1622 | 2.5488 | 0.1157 |
| ee0fd226c929a896 | published_policy_command_straight_x008_seed3/trace_full_obs_footpos.jsonl | 205-229 | `none` | 0.0698 | 0.1927 | 0.0531 | 0.1618 | 2.3433 | 0.1206 |
| 814a5885c302b88b | published_policy_command_straight_x008_seed3/trace_full_obs_footpos.jsonl | 210-234 | `none` | 0.0699 | 0.1884 | 0.0517 | 0.1623 | 2.2786 | 0.1206 |
| 8cd149ca209fd74f | published_policy_command_straight_x008_seed3/trace_full_obs_footpos.jsonl | 215-239 | `none` | 0.0723 | 0.1884 | 0.0526 | 0.1623 | 2.3979 | 0.1155 |
| 5fecb7bec63da4d4 | published_policy_command_straight_x008_seed3/trace_full_obs_footpos.jsonl | 220-244 | `none` | 0.0718 | 0.1643 | 0.0532 | 0.1619 | 2.4207 | 0.1092 |
| 80b1cb37ce60b8b3 | published_policy_command_straight_x008_seed4/trace_full_obs_footpos.jsonl | 0-24 | `none` | 0.0855 | 0.1628 | 0.0797 | 0.1506 | 3.1965 | 0.1295 |
| 32109ad0b58411e6 | published_policy_command_straight_x008_seed4/trace_full_obs_footpos.jsonl | 5-29 | `none` | 0.0578 | 0.1628 | 0.0840 | 0.1603 | 2.1630 | 0.0862 |
| 7d88958ffcc4691e | published_policy_command_straight_x008_seed4/trace_full_obs_footpos.jsonl | 145-169 | `none` | 0.0431 | 0.1608 | 0.0702 | 0.1574 | 2.3208 | 0.1082 |
| 3174a81c2adc032a | published_policy_command_straight_x008_seed4/trace_full_obs_footpos.jsonl | 150-174 | `none` | 0.0522 | 0.1608 | 0.0695 | 0.1574 | 2.5666 | 0.1181 |
| 2b53d58c716db3eb | published_policy_command_straight_x008_seed4/trace_full_obs_footpos.jsonl | 165-189 | `none` | 0.0616 | 0.1721 | 0.0692 | 0.1601 | 2.4413 | 0.1183 |
| b1faf02ebdbd96c9 | published_policy_command_straight_x008_seed4/trace_full_obs_footpos.jsonl | 170-194 | `none` | 0.0612 | 0.1831 | 0.0692 | 0.1601 | 2.4413 | 0.1237 |
| 86b6ea037d873424 | published_policy_command_straight_x008_seed4/trace_full_obs_footpos.jsonl | 175-199 | `none` | 0.0621 | 0.1831 | 0.0642 | 0.1601 | 2.4714 | 0.1250 |
| c9af451f73e3a658 | published_policy_command_straight_x008_seed4/trace_full_obs_footpos.jsonl | 180-204 | `none` | 0.0659 | 0.1737 | 0.0619 | 0.1617 | 2.3943 | 0.1183 |
| e3ee3fbc4ce84103 | published_policy_command_straight_x008_seed4/trace_full_obs_footpos.jsonl | 185-209 | `none` | 0.0654 | 0.1831 | 0.0565 | 0.1617 | 2.1992 | 0.1137 |
| 14f8afd2c0c33eb5 | published_policy_command_straight_x008_seed4/trace_full_obs_footpos.jsonl | 190-214 | `none` | 0.0687 | 0.1831 | 0.0551 | 0.1617 | 2.2774 | 0.1174 |
| e95e06ce990784ee | published_policy_command_straight_x008_seed4/trace_full_obs_footpos.jsonl | 195-219 | `none` | 0.0685 | 0.1824 | 0.0551 | 0.1618 | 2.5043 | 0.1195 |
| 97edcff84ced6216 | published_policy_command_straight_x008_seed4/trace_full_obs_footpos.jsonl | 200-224 | `none` | 0.0700 | 0.1824 | 0.0550 | 0.1618 | 2.4766 | 0.1151 |
| 228dfce068664e67 | published_policy_command_straight_x008_seed4/trace_full_obs_footpos.jsonl | 205-229 | `none` | 0.0728 | 0.1824 | 0.0553 | 0.1618 | 2.4672 | 0.1124 |
| 700ebce97c2545f3 | published_policy_command_straight_x008_seed4/trace_full_obs_footpos.jsonl | 210-234 | `none` | 0.0729 | 0.1815 | 0.0558 | 0.1618 | 2.4672 | 0.1206 |
| 0b38cb6a7b032926 | published_policy_command_straight_x008_seed4/trace_full_obs_footpos.jsonl | 215-239 | `none` | 0.0769 | 0.1815 | 0.0558 | 0.1618 | 2.4944 | 0.1172 |
| ca78427b3bb9266e | published_policy_command_straight_x008_seed4/trace_full_obs_footpos.jsonl | 220-244 | `none` | 0.0759 | 0.1657 | 0.0558 | 0.1622 | 2.5887 | 0.1106 |
| 06d9cdc9474066f8 | published_policy_command_straight_x008_seed4/trace_full_obs_footpos.jsonl | 225-249 | `none` | 0.0711 | 0.1937 | 0.0558 | 0.1622 | 2.4944 | 0.1147 |
| fffc9ade1b269cdb | published_policy_command_straight_x008_seed5/trace_full_obs_footpos.jsonl | 20-44 | `none` | 0.0770 | 0.1650 | 0.0524 | 0.1601 | 2.8251 | 0.1218 |
| aad3e4e16219109f | published_policy_command_straight_x008_seed5/trace_full_obs_footpos.jsonl | 25-49 | `none` | 0.0847 | 0.1650 | 0.0578 | 0.1601 | 2.5501 | 0.1228 |
| acc304b92e694295 | published_policy_command_straight_x008_seed5/trace_full_obs_footpos.jsonl | 30-54 | `none` | 0.0796 | 0.1626 | 0.0585 | 0.1607 | 2.5775 | 0.1178 |
| 6835278bfeee9831 | published_policy_command_straight_x008_seed5/trace_full_obs_footpos.jsonl | 35-59 | `none` | 0.0723 | 0.1887 | 0.0585 | 0.1607 | 2.5451 | 0.1250 |
| 1d368eeafa1f263d | published_policy_command_straight_x008_seed5/trace_full_obs_footpos.jsonl | 40-64 | `none` | 0.0708 | 0.1887 | 0.0585 | 0.1607 | 2.6560 | 0.1250 |
| bca62ab24710c163 | published_policy_command_straight_x008_seed5/trace_full_obs_footpos.jsonl | 45-69 | `none` | 0.0709 | 0.1701 | 0.0585 | 0.1616 | 2.5760 | 0.1202 |
| 85bfdb03bc50588e | published_policy_command_straight_x008_seed5/trace_full_obs_footpos.jsonl | 55-79 | `none` | 0.0706 | 0.1887 | 0.0555 | 0.1616 | 2.5006 | 0.1202 |
| 9a057c60c5e10988 | published_policy_command_straight_x008_seed5/trace_full_obs_footpos.jsonl | 60-84 | `none` | 0.0713 | 0.1825 | 0.0555 | 0.1626 | 2.5750 | 0.1214 |
| 7bcd6d2bb64e9113 | published_policy_command_straight_x008_seed5/trace_full_obs_footpos.jsonl | 70-94 | `none` | 0.0707 | 0.1825 | 0.0539 | 0.1626 | 2.5006 | 0.1192 |
| ac1cd32f00190612 | published_policy_command_straight_x008_seed5/trace_full_obs_footpos.jsonl | 75-99 | `none` | 0.0715 | 0.1916 | 0.0488 | 0.1616 | 2.4062 | 0.1237 |
| d3f5146476e5607b | published_policy_command_straight_x008_seed5/trace_full_obs_footpos.jsonl | 80-104 | `none` | 0.0733 | 0.1916 | 0.0534 | 0.1616 | 2.3763 | 0.1213 |
| 19c3fe897af7e44a | published_policy_command_straight_x008_seed5/trace_full_obs_footpos.jsonl | 85-109 | `none` | 0.0710 | 0.1829 | 0.0538 | 0.1616 | 2.4228 | 0.1140 |
| f62bbf91c2b2d16c | published_policy_command_straight_x008_seed5/trace_full_obs_footpos.jsonl | 95-119 | `none` | 0.0699 | 0.1923 | 0.0541 | 0.1616 | 2.4148 | 0.1224 |
| 937db0df0d04c00a | published_policy_command_straight_x008_seed5/trace_full_obs_footpos.jsonl | 100-124 | `none` | 0.0702 | 0.1773 | 0.0541 | 0.1620 | 2.3523 | 0.1183 |
| cf4faab713ad0496 | published_policy_command_straight_x008_seed5/trace_full_obs_footpos.jsonl | 110-134 | `none` | 0.0706 | 0.1893 | 0.0541 | 0.1620 | 2.3947 | 0.1166 |
| a080906d8a6f771b | published_policy_command_straight_x008_seed5/trace_full_obs_footpos.jsonl | 115-139 | `none` | 0.0708 | 0.1883 | 0.0541 | 0.1621 | 2.4422 | 0.1229 |
| 6521b2747897e6d0 | published_policy_command_straight_x008_seed5/trace_full_obs_footpos.jsonl | 135-159 | `none` | 0.0724 | 0.1881 | 0.0547 | 0.1621 | 2.4305 | 0.1250 |
| c8d9b2ed1ba0bb1b | published_policy_command_straight_x008_seed5/trace_full_obs_footpos.jsonl | 140-164 | `none` | 0.0720 | 0.1759 | 0.0547 | 0.1622 | 2.5585 | 0.1190 |
| c305867b4669a91d | published_policy_command_straight_x008_seed5/trace_full_obs_footpos.jsonl | 220-244 | `none` | 0.0702 | 0.1739 | 0.0537 | 0.1622 | 2.5297 | 0.1116 |
| e5bd71a36d8ca02c | published_policy_command_straight_x008_seed6/trace_full_obs_footpos.jsonl | 15-39 | `none` | 0.0751 | 0.1923 | 0.0552 | 0.1593 | 2.4647 | 0.1298 |
| 1d7f5dc38c51afd0 | published_policy_command_straight_x008_seed6/trace_full_obs_footpos.jsonl | 70-94 | `none` | 0.0742 | 0.1824 | 0.0546 | 0.1621 | 2.5038 | 0.1149 |
| 689ab351676fc906 | published_policy_command_straight_x008_seed6/trace_full_obs_footpos.jsonl | 80-104 | `none` | 0.0789 | 0.1816 | 0.0515 | 0.1621 | 2.5732 | 0.1173 |
| 7e8f26994d3c9fe1 | published_policy_command_straight_x008_seed6/trace_full_obs_footpos.jsonl | 85-109 | `none` | 0.0785 | 0.1677 | 0.0515 | 0.1625 | 2.6465 | 0.1108 |
| f4fbc2efacf6319c | published_policy_command_straight_x008_seed6/trace_full_obs_footpos.jsonl | 90-114 | `none` | 0.0762 | 0.1987 | 0.0515 | 0.1625 | 2.5620 | 0.1167 |
| d609de931b679001 | published_policy_command_straight_x008_seed6/trace_full_obs_footpos.jsonl | 95-119 | `none` | 0.0767 | 0.1987 | 0.0506 | 0.1625 | 2.6021 | 0.1209 |
| 6867e7b1421b22cb | published_policy_command_straight_x008_seed6/trace_full_obs_footpos.jsonl | 100-124 | `none` | 0.0790 | 0.1674 | 0.0489 | 0.1625 | 2.5898 | 0.1156 |
| 52b6cc26a0f87249 | published_policy_command_straight_x008_seed6/trace_full_obs_footpos.jsonl | 105-129 | `none` | 0.0793 | 0.1984 | 0.0503 | 0.1625 | 2.4453 | 0.1156 |
| 259c2e148b5383d8 | published_policy_command_straight_x008_seed6/trace_full_obs_footpos.jsonl | 110-134 | `none` | 0.0817 | 0.1984 | 0.0510 | 0.1626 | 2.4810 | 0.1143 |
| 07db2ffe78c5b47e | published_policy_command_straight_x008_seed6/trace_full_obs_footpos.jsonl | 115-139 | `none` | 0.0801 | 0.1985 | 0.0510 | 0.1628 | 2.5109 | 0.1193 |
| c840a96acbec33f2 | published_policy_command_straight_x008_seed6/trace_full_obs_footpos.jsonl | 120-144 | `none` | 0.0765 | 0.1985 | 0.0510 | 0.1628 | 2.4380 | 0.1193 |
| e83d8f48d83c9639 | published_policy_command_straight_x008_seed6/trace_full_obs_footpos.jsonl | 125-149 | `none` | 0.0760 | 0.1962 | 0.0544 | 0.1628 | 2.3829 | 0.1080 |
| 288eeb280b4f7bea | published_policy_command_straight_x008_seed6/trace_full_obs_footpos.jsonl | 185-209 | `none` | 0.0771 | 0.1931 | 0.0428 | 0.1622 | 2.4528 | 0.1190 |
| a15918569f099740 | published_policy_command_straight_x008_seed6/trace_full_obs_footpos.jsonl | 190-214 | `none` | 0.0818 | 0.1931 | 0.0439 | 0.1622 | 2.4517 | 0.1250 |
| 367c9df18d1eafda | published_policy_command_straight_x008_seed6/trace_full_obs_footpos.jsonl | 195-219 | `none` | 0.0794 | 0.1970 | 0.0439 | 0.1622 | 2.5907 | 0.1268 |
| 24b53f7d67686f67 | published_policy_command_straight_x008_seed6/trace_full_obs_footpos.jsonl | 200-224 | `none` | 0.0794 | 0.1970 | 0.0439 | 0.1622 | 2.5658 | 0.1233 |
| 6a9eff170eaeb1b4 | published_policy_command_straight_x008_seed6/trace_full_obs_footpos.jsonl | 205-229 | `none` | 0.0795 | 0.1970 | 0.0503 | 0.1622 | 2.4834 | 0.1224 |
| d0298e24207b55b1 | published_policy_command_straight_x008_seed6/trace_full_obs_footpos.jsonl | 220-244 | `none` | 0.0743 | 0.1688 | 0.0533 | 0.1626 | 2.4639 | 0.1106 |
| 42b9647a765a2e07 | published_policy_command_straight_x008_seed7/trace_full_obs_footpos.jsonl | 45-69 | `none` | 0.0749 | 0.1607 | 0.0544 | 0.1622 | 2.5639 | 0.1126 |
| 8dba054a548416d5 | published_policy_command_straight_x008_seed7/trace_full_obs_footpos.jsonl | 55-79 | `none` | 0.0761 | 0.1802 | 0.0533 | 0.1621 | 2.4394 | 0.1220 |
| fcd89f28631c0678 | published_policy_command_straight_x008_seed7/trace_full_obs_footpos.jsonl | 70-94 | `none` | 0.0756 | 0.1846 | 0.0533 | 0.1621 | 2.4580 | 0.1185 |
| 3ee3e1d834a2477c | published_policy_command_straight_x008_seed7/trace_full_obs_footpos.jsonl | 75-99 | `none` | 0.0763 | 0.1839 | 0.0503 | 0.1624 | 2.3136 | 0.1231 |
| e404f7f2242aba31 | published_policy_command_straight_x008_seed7/trace_full_obs_footpos.jsonl | 80-104 | `none` | 0.0788 | 0.1839 | 0.0509 | 0.1624 | 2.4327 | 0.1208 |
| 7215aed311e767bf | published_policy_command_straight_x008_seed7/trace_full_obs_footpos.jsonl | 85-109 | `none` | 0.0785 | 0.1718 | 0.0509 | 0.1624 | 2.4628 | 0.1136 |
| cabef150c3eee5bf | published_policy_command_straight_x008_seed7/trace_full_obs_footpos.jsonl | 90-114 | `none` | 0.0766 | 0.1904 | 0.0509 | 0.1624 | 2.4276 | 0.1190 |
| 56c14909f00a1912 | published_policy_command_straight_x008_seed7/trace_full_obs_footpos.jsonl | 95-119 | `none` | 0.0766 | 0.1904 | 0.0509 | 0.1624 | 2.4276 | 0.1233 |
| 864797237027522a | published_policy_command_straight_x008_seed7/trace_full_obs_footpos.jsonl | 100-124 | `none` | 0.0777 | 0.1641 | 0.0502 | 0.1624 | 2.4372 | 0.1170 |
| 78465bac606ca2ae | published_policy_command_straight_x008_seed7/trace_full_obs_footpos.jsonl | 105-129 | `none` | 0.0791 | 0.1882 | 0.0503 | 0.1624 | 2.3456 | 0.1156 |
| 2ea64ff5b6a792a9 | published_policy_command_straight_x008_seed7/trace_full_obs_footpos.jsonl | 110-134 | `none` | 0.0798 | 0.1882 | 0.0503 | 0.1624 | 2.4582 | 0.1134 |
| 39ebd0764bef0813 | published_policy_command_straight_x008_seed7/trace_full_obs_footpos.jsonl | 165-189 | `none` | 0.0750 | 0.1873 | 0.0552 | 0.1623 | 2.4428 | 0.1151 |
| 2ca265012746d6ef | published_policy_command_straight_x008_seed7/trace_full_obs_footpos.jsonl | 180-204 | `none` | 0.0762 | 0.1649 | 0.0547 | 0.1629 | 2.5574 | 0.1166 |
| 5cc2bf69f903cd9f | published_policy_command_straight_x008_seed7/trace_full_obs_footpos.jsonl | 220-244 | `none` | 0.0751 | 0.1698 | 0.0491 | 0.1625 | 2.6562 | 0.1079 |
| 97e1e4b73f91f397 | published_policy_command_straight_x008_seed7/trace_full_obs_footpos.jsonl | 225-249 | `none` | 0.0771 | 0.1912 | 0.0491 | 0.1625 | 2.3983 | 0.1113 |
| 3b4abb63356ee2bf | published_policy_command_turning_x0074_yneg0037_yawneg0074_seed0/trace_full_obs_footpos.jsonl | 5-29 | `none` | 0.0692 | 0.1810 | 0.0424 | 0.1598 | 2.5812 | 0.1213 |
| 7ed9a5f2399ebc8c | published_policy_command_turning_x0074_yneg0037_yawneg0074_seed0/trace_full_obs_footpos.jsonl | 15-39 | `none` | 0.0669 | 0.1822 | 0.0530 | 0.1598 | 2.4240 | 0.1192 |
| 021fffd1bf492e05 | published_policy_command_turning_x0074_yneg0037_yawneg0074_seed0/trace_full_obs_footpos.jsonl | 20-44 | `none` | 0.0657 | 0.1878 | 0.0530 | 0.1598 | 2.4240 | 0.1133 |
| 6c3cf4dcd3a3caeb | published_policy_command_turning_x0074_yneg0037_yawneg0074_seed0/trace_full_obs_footpos.jsonl | 25-49 | `none` | 0.0666 | 0.1878 | 0.0530 | 0.1598 | 2.5210 | 0.1105 |
| d42903a0289e5df7 | published_policy_command_turning_x0074_yneg0037_yawneg0074_seed0/trace_full_obs_footpos.jsonl | 45-69 | `none` | 0.0659 | 0.1990 | 0.0554 | 0.1614 | 2.6433 | 0.1124 |
| cdf0742213cec32e | published_policy_command_turning_x0074_yneg0037_yawneg0074_seed0/trace_full_obs_footpos.jsonl | 60-84 | `none` | 0.0700 | 0.1817 | 0.0496 | 0.1622 | 2.7356 | 0.1180 |
| 1cccf693ab0fa4c6 | published_policy_command_turning_x0074_yneg0037_yawneg0074_seed0/trace_full_obs_footpos.jsonl | 65-89 | `none` | 0.0676 | 0.1817 | 0.0496 | 0.1622 | 2.5959 | 0.1139 |
| f221d596e678fe12 | published_policy_command_turning_x0074_yneg0037_yawneg0074_seed0/trace_full_obs_footpos.jsonl | 70-94 | `none` | 0.0676 | 0.1817 | 0.0496 | 0.1622 | 2.5028 | 0.1167 |
| 1ad3c389bf1b76a6 | published_policy_command_turning_x0074_yneg0037_yawneg0074_seed0/trace_full_obs_footpos.jsonl | 180-204 | `none` | 0.0660 | 0.1905 | 0.0496 | 0.1617 | 2.5575 | 0.1148 |
| 11d8279e76eb184f | published_policy_command_turning_x0074_yneg0037_yawneg0074_seed0/trace_full_obs_footpos.jsonl | 190-214 | `none` | 0.0668 | 0.1986 | 0.0484 | 0.1617 | 2.5606 | 0.1181 |
| 79ee7d9941806fe9 | published_policy_command_turning_x0074_yneg0037_yawneg0074_seed0/trace_full_obs_footpos.jsonl | 195-219 | `none` | 0.0668 | 0.1896 | 0.0484 | 0.1622 | 2.7519 | 0.1206 |
| 4eaec00ba2c8b103 | published_policy_command_turning_x0074_yneg0037_yawneg0074_seed0/trace_full_obs_footpos.jsonl | 200-224 | `none` | 0.0654 | 0.1896 | 0.0472 | 0.1622 | 2.6940 | 0.1135 |
| cbaa55534261fff5 | published_policy_command_turning_x0074_yneg0037_yawneg0074_seed0/trace_full_obs_footpos.jsonl | 205-229 | `none` | 0.0680 | 0.1896 | 0.0472 | 0.1622 | 2.6876 | 0.1170 |
| a8f22990a26c74ae | published_policy_command_turning_x0074_yneg0037_yawneg0074_seed0/trace_full_obs_footpos.jsonl | 210-234 | `none` | 0.0696 | 0.1918 | 0.0467 | 0.1622 | 2.4990 | 0.1195 |
| 8016f9bb259c02ca | published_policy_command_turning_x0074_yneg0037_yawneg0074_seed0/trace_full_obs_footpos.jsonl | 215-239 | `none` | 0.0728 | 0.1918 | 0.0492 | 0.1622 | 2.5042 | 0.1128 |
| cee663ed770b2a8f | published_policy_command_turning_x0074_yneg0037_yawneg0074_seed0/trace_full_obs_footpos.jsonl | 220-244 | `none` | 0.0703 | 0.1604 | 0.0532 | 0.1621 | 2.5409 | 0.1114 |
| 3c8c1f04345ad94c | published_policy_command_turning_x0074_yneg0037_yawneg0074_seed0/trace_full_obs_footpos.jsonl | 225-249 | `none` | 0.0689 | 0.1893 | 0.0532 | 0.1621 | 2.4153 | 0.1126 |
| 8f36ca89d7d61432 | published_policy_command_turning_x0074_yneg0037_yawneg0074_seed1/trace_full_obs_footpos.jsonl | 125-149 | `none` | 0.0619 | 0.1852 | 0.0554 | 0.1600 | 2.4938 | 0.1121 |
| 3e47c2ad779f8e92 | published_policy_command_turning_x0074_yneg0037_yawneg0074_seed1/trace_full_obs_footpos.jsonl | 135-159 | `none` | 0.0643 | 0.1855 | 0.0531 | 0.1600 | 2.4196 | 0.1167 |
| 356c51cf8278338f | published_policy_command_turning_x0074_yneg0037_yawneg0074_seed1/trace_full_obs_footpos.jsonl | 140-164 | `none` | 0.0636 | 0.1796 | 0.0544 | 0.1616 | 2.5075 | 0.1118 |
| 7a2fe9face1a395b | published_policy_command_turning_x0074_yneg0037_yawneg0074_seed1/trace_full_obs_footpos.jsonl | 145-169 | `none` | 0.0645 | 0.1993 | 0.0544 | 0.1616 | 2.3811 | 0.1134 |
| cd4bad2cd833b154 | published_policy_command_turning_x0074_yneg0037_yawneg0074_seed1/trace_full_obs_footpos.jsonl | 150-174 | `none` | 0.0659 | 0.1993 | 0.0551 | 0.1616 | 2.4196 | 0.1172 |
| 2b8c247c21cd8b13 | published_policy_command_turning_x0074_yneg0037_yawneg0074_seed1/trace_full_obs_footpos.jsonl | 165-189 | `none` | 0.0642 | 0.1932 | 0.0541 | 0.1620 | 2.6051 | 0.1128 |
| b7e174807ee79a45 | published_policy_command_turning_x0074_yneg0037_yawneg0074_seed1/trace_full_obs_footpos.jsonl | 180-204 | `none` | 0.0662 | 0.1851 | 0.0512 | 0.1616 | 2.7260 | 0.1204 |
| bf982c29963de4c0 | published_policy_command_turning_x0074_yneg0037_yawneg0074_seed1/trace_full_obs_footpos.jsonl | 185-209 | `none` | 0.0699 | 0.1899 | 0.0508 | 0.1616 | 2.3815 | 0.1143 |
| 6ae28248d81c580c | published_policy_command_turning_x0074_yneg0037_yawneg0074_seed1/trace_full_obs_footpos.jsonl | 190-214 | `none` | 0.0714 | 0.1899 | 0.0514 | 0.1616 | 2.3626 | 0.1148 |
| 8f06acbef59b1500 | published_policy_command_turning_x0074_yneg0037_yawneg0074_seed1/trace_full_obs_footpos.jsonl | 195-219 | `none` | 0.0706 | 0.1894 | 0.0514 | 0.1618 | 2.5487 | 0.1174 |
| 6cb6a55db30d01ce | published_policy_command_turning_x0074_yneg0037_yawneg0074_seed1/trace_full_obs_footpos.jsonl | 200-224 | `none` | 0.0705 | 0.1894 | 0.0514 | 0.1618 | 2.4664 | 0.1147 |
| fc3c119e20f50153 | published_policy_command_turning_x0074_yneg0037_yawneg0074_seed1/trace_full_obs_footpos.jsonl | 205-229 | `none` | 0.0716 | 0.1894 | 0.0514 | 0.1618 | 2.4267 | 0.1150 |
| 4fa4e76b924187cd | published_policy_command_turning_x0074_yneg0037_yawneg0074_seed1/trace_full_obs_footpos.jsonl | 210-234 | `none` | 0.0685 | 0.1921 | 0.0514 | 0.1618 | 2.4459 | 0.1189 |
| 045c469459b5ec3f | published_policy_command_turning_x0074_yneg0037_yawneg0074_seed1/trace_full_obs_footpos.jsonl | 215-239 | `none` | 0.0716 | 0.1921 | 0.0533 | 0.1618 | 2.5625 | 0.1169 |
| d5b83ca68fea227a | published_policy_command_turning_x0074_yneg0037_yawneg0074_seed1/trace_full_obs_footpos.jsonl | 220-244 | `none` | 0.0698 | 0.1600 | 0.0569 | 0.1619 | 2.4459 | 0.1118 |
| 701fd0f90b7d2163 | published_policy_command_turning_x0074_yneg0037_yawneg0074_seed1/trace_full_obs_footpos.jsonl | 225-249 | `none` | 0.0669 | 0.1849 | 0.0569 | 0.1619 | 2.3825 | 0.1132 |
| 00a31f2e8b651ea9 | published_policy_command_turning_x0074_yneg0037_yawneg0074_seed2/trace_full_obs_footpos.jsonl | 0-24 | `none` | 0.1008 | 0.1331 | 0.0415 | 0.1510 | 2.7390 | 0.1181 |
| 41461f3470545401 | published_policy_command_turning_x0074_yneg0037_yawneg0074_seed2/trace_full_obs_footpos.jsonl | 5-29 | `none` | 0.0809 | 0.1434 | 0.0532 | 0.1562 | 2.5848 | 0.1088 |
| 4e25a751126182a6 | published_policy_command_turning_x0074_yneg0037_yawneg0074_seed2/trace_full_obs_footpos.jsonl | 85-109 | `none` | 0.0661 | 0.1580 | 0.0528 | 0.1618 | 2.7301 | 0.1141 |
| 7188f3513c238f92 | published_policy_command_turning_x0074_yneg0037_yawneg0074_seed2/trace_full_obs_footpos.jsonl | 90-114 | `none` | 0.0663 | 0.1927 | 0.0528 | 0.1618 | 2.5381 | 0.1182 |
| 7b15fedc9479ac23 | published_policy_command_turning_x0074_yneg0037_yawneg0074_seed2/trace_full_obs_footpos.jsonl | 95-119 | `none` | 0.0663 | 0.1927 | 0.0528 | 0.1618 | 2.6366 | 0.1202 |
| b553df947d98ca42 | published_policy_command_turning_x0074_yneg0037_yawneg0074_seed2/trace_full_obs_footpos.jsonl | 100-124 | `none` | 0.0665 | 0.1890 | 0.0528 | 0.1618 | 2.7007 | 0.1182 |
| ec496039bb66bbde | published_policy_command_turning_x0074_yneg0037_yawneg0074_seed2/trace_full_obs_footpos.jsonl | 105-129 | `none` | 0.0668 | 0.1917 | 0.0523 | 0.1618 | 2.3416 | 0.1159 |
| 80ec09c7d95deb90 | published_policy_command_turning_x0074_yneg0037_yawneg0074_seed2/trace_full_obs_footpos.jsonl | 110-134 | `none` | 0.0670 | 0.1917 | 0.0550 | 0.1619 | 2.3842 | 0.1119 |
| 9acd9a8c0cc463bd | published_policy_command_turning_x0074_yneg0037_yawneg0074_seed2/trace_full_obs_footpos.jsonl | 115-139 | `none` | 0.0666 | 0.1887 | 0.0550 | 0.1618 | 2.4574 | 0.1162 |
| ef06af47206feff2 | published_policy_command_turning_x0074_yneg0037_yawneg0074_seed2/trace_full_obs_footpos.jsonl | 165-189 | `none` | 0.0660 | 0.1798 | 0.0515 | 0.1619 | 2.4868 | 0.1111 |
| a486316d7505c9a5 | published_policy_command_turning_x0074_yneg0037_yawneg0074_seed2/trace_full_obs_footpos.jsonl | 170-194 | `none` | 0.0668 | 0.1886 | 0.0515 | 0.1620 | 2.4781 | 0.1120 |
| d96ab56069a73385 | published_policy_command_turning_x0074_yneg0037_yawneg0074_seed2/trace_full_obs_footpos.jsonl | 180-204 | `none` | 0.0672 | 0.1867 | 0.0515 | 0.1620 | 2.4781 | 0.1121 |
| 48486a76d0613616 | published_policy_command_turning_x0074_yneg0037_yawneg0074_seed2/trace_full_obs_footpos.jsonl | 210-234 | `none` | 0.0647 | 0.1952 | 0.0520 | 0.1614 | 2.5063 | 0.1159 |
| e2e4c805a741f98e | published_policy_command_turning_x0074_yneg0037_yawneg0074_seed2/trace_full_obs_footpos.jsonl | 215-239 | `none` | 0.0662 | 0.1952 | 0.0520 | 0.1614 | 2.5327 | 0.1154 |
| ea5efbf4a6d4d633 | published_policy_command_turning_x0074_yneg0037_yawneg0074_seed3/trace_full_obs_footpos.jsonl | 85-109 | `none` | 0.0691 | 0.1566 | 0.0511 | 0.1618 | 2.6075 | 0.1160 |
| d1dafaa08132bfd5 | published_policy_command_turning_x0074_yneg0037_yawneg0074_seed3/trace_full_obs_footpos.jsonl | 90-114 | `none` | 0.0682 | 0.1877 | 0.0511 | 0.1618 | 2.5062 | 0.1186 |
| c867bc23f7f64c5d | published_policy_command_turning_x0074_yneg0037_yawneg0074_seed3/trace_full_obs_footpos.jsonl | 95-119 | `none` | 0.0676 | 0.1877 | 0.0511 | 0.1618 | 2.5989 | 0.1196 |
| bacbbe9178d58f44 | published_policy_command_turning_x0074_yneg0037_yawneg0074_seed3/trace_full_obs_footpos.jsonl | 100-124 | `none` | 0.0691 | 0.1860 | 0.0511 | 0.1618 | 2.5479 | 0.1194 |
| 2160b36115d735aa | published_policy_command_turning_x0074_yneg0037_yawneg0074_seed3/trace_full_obs_footpos.jsonl | 105-129 | `none` | 0.0683 | 0.1885 | 0.0510 | 0.1618 | 2.3553 | 0.1163 |
| c5e0a6aedcc0999e | published_policy_command_turning_x0074_yneg0037_yawneg0074_seed3/trace_full_obs_footpos.jsonl | 110-134 | `none` | 0.0692 | 0.1885 | 0.0517 | 0.1619 | 2.4028 | 0.1092 |
| 955183901e3b5d8e | published_policy_command_turning_x0074_yneg0037_yawneg0074_seed3/trace_full_obs_footpos.jsonl | 115-139 | `none` | 0.0692 | 0.1876 | 0.0517 | 0.1620 | 2.4511 | 0.1155 |
| 4798ce3f56c5c4c7 | published_policy_command_turning_x0074_yneg0037_yawneg0074_seed3/trace_full_obs_footpos.jsonl | 120-144 | `none` | 0.0679 | 0.1876 | 0.0517 | 0.1620 | 2.4891 | 0.1127 |
| dc58548c291a1447 | published_policy_command_turning_x0074_yneg0037_yawneg0074_seed3/trace_full_obs_footpos.jsonl | 125-149 | `none` | 0.0674 | 0.1876 | 0.0517 | 0.1620 | 2.4783 | 0.1071 |
| 8d4b300844541e1e | published_policy_command_turning_x0074_yneg0037_yawneg0074_seed3/trace_full_obs_footpos.jsonl | 135-159 | `none` | 0.0684 | 0.1874 | 0.0509 | 0.1620 | 2.3417 | 0.1161 |
| 2699a56f50a5c950 | published_policy_command_turning_x0074_yneg0037_yawneg0074_seed3/trace_full_obs_footpos.jsonl | 140-164 | `none` | 0.0670 | 0.1714 | 0.0538 | 0.1615 | 2.5885 | 0.1120 |
| b95af764eab4cca8 | published_policy_command_turning_x0074_yneg0037_yawneg0074_seed3/trace_full_obs_footpos.jsonl | 180-204 | `none` | 0.0679 | 0.1878 | 0.0509 | 0.1615 | 2.5824 | 0.1166 |
| 16def8f55ee8d659 | published_policy_command_turning_x0074_yneg0037_yawneg0074_seed3/trace_full_obs_footpos.jsonl | 185-209 | `none` | 0.0673 | 0.1956 | 0.0509 | 0.1615 | 2.3758 | 0.1144 |
| ac3b3871e6bcb1ca | published_policy_command_turning_x0074_yneg0037_yawneg0074_seed3/trace_full_obs_footpos.jsonl | 190-214 | `none` | 0.0683 | 0.1956 | 0.0531 | 0.1615 | 2.3587 | 0.1160 |
| 76bbb132e7a60444 | published_policy_command_turning_x0074_yneg0037_yawneg0074_seed3/trace_full_obs_footpos.jsonl | 195-219 | `none` | 0.0673 | 0.1887 | 0.0531 | 0.1619 | 2.6038 | 0.1182 |
| 842698a4cd0f2c38 | published_policy_command_turning_x0074_yneg0037_yawneg0074_seed3/trace_full_obs_footpos.jsonl | 200-224 | `none` | 0.0676 | 0.1887 | 0.0531 | 0.1619 | 2.4257 | 0.1114 |
| 8ed31141c563512f | published_policy_command_turning_x0074_yneg0037_yawneg0074_seed3/trace_full_obs_footpos.jsonl | 205-229 | `none` | 0.0684 | 0.1887 | 0.0531 | 0.1619 | 2.4528 | 0.1143 |
| 31a711be62990146 | published_policy_command_turning_x0074_yneg0037_yawneg0074_seed3/trace_full_obs_footpos.jsonl | 215-239 | `none` | 0.0682 | 0.1887 | 0.0518 | 0.1619 | 2.5245 | 0.1159 |
| cf45a9a60fda1296 | published_policy_command_turning_x0074_yneg0037_yawneg0074_seed3/trace_full_obs_footpos.jsonl | 220-244 | `none` | 0.0680 | 0.1598 | 0.0524 | 0.1619 | 2.4443 | 0.1119 |
| 1a2aff565d53199c | published_policy_command_turning_x0074_yneg0037_yawneg0074_seed4/trace_full_obs_footpos.jsonl | 0-24 | `none` | 0.0831 | 0.1516 | 0.0802 | 0.1506 | 3.3980 | 0.1271 |
| 83ce79ca7d4ea96a | published_policy_command_turning_x0074_yneg0037_yawneg0074_seed4/trace_full_obs_footpos.jsonl | 5-29 | `none` | 0.0561 | 0.1516 | 0.0800 | 0.1617 | 2.4211 | 0.0921 |
| 1872bb12a15be923 | published_policy_command_turning_x0074_yneg0037_yawneg0074_seed5/trace_full_obs_footpos.jsonl | 20-44 | `none` | 0.0686 | 0.1659 | 0.0450 | 0.1589 | 3.0257 | 0.1262 |
| 9a85024a907f6284 | published_policy_command_turning_x0074_yneg0037_yawneg0074_seed5/trace_full_obs_footpos.jsonl | 25-49 | `none` | 0.0744 | 0.1659 | 0.0478 | 0.1589 | 2.8157 | 0.1209 |
| 56c87dee7ada7ba5 | published_policy_command_turning_x0074_yneg0037_yawneg0074_seed5/trace_full_obs_footpos.jsonl | 30-54 | `none` | 0.0699 | 0.1526 | 0.0543 | 0.1608 | 2.7049 | 0.1195 |
| 1c591a8dde1e676a | published_policy_command_turning_x0074_yneg0037_yawneg0074_seed5/trace_full_obs_footpos.jsonl | 55-79 | `none` | 0.0664 | 0.1971 | 0.0485 | 0.1606 | 2.5542 | 0.1160 |
| b1ec67b942c92a54 | published_policy_command_turning_x0074_yneg0037_yawneg0074_seed5/trace_full_obs_footpos.jsonl | 60-84 | `none` | 0.0667 | 0.1945 | 0.0485 | 0.1618 | 2.7177 | 0.1192 |
| 698e2e8ef451384b | published_policy_command_turning_x0074_yneg0037_yawneg0074_seed5/trace_full_obs_footpos.jsonl | 70-94 | `none` | 0.0668 | 0.1945 | 0.0482 | 0.1618 | 2.7084 | 0.1183 |
| ae5afe7acf9298f4 | published_policy_command_turning_x0074_yneg0037_yawneg0074_seed5/trace_full_obs_footpos.jsonl | 80-104 | `none` | 0.0683 | 0.1936 | 0.0484 | 0.1618 | 2.4914 | 0.1145 |
| 6833fb4d7aecf7b1 | published_policy_command_turning_x0074_yneg0037_yawneg0074_seed5/trace_full_obs_footpos.jsonl | 85-109 | `none` | 0.0663 | 0.1594 | 0.0534 | 0.1619 | 2.5021 | 0.1109 |
| 1a98e177d40cd0db | published_policy_command_turning_x0074_yneg0037_yawneg0074_seed5/trace_full_obs_footpos.jsonl | 90-114 | `none` | 0.0660 | 0.1881 | 0.0534 | 0.1619 | 2.3432 | 0.1126 |
| bfee9ee409e19da2 | published_policy_command_turning_x0074_yneg0037_yawneg0074_seed5/trace_full_obs_footpos.jsonl | 105-129 | `none` | 0.0659 | 0.1884 | 0.0530 | 0.1619 | 2.2850 | 0.1117 |
| 43c8acfd76d94e1e | published_policy_command_turning_x0074_yneg0037_yawneg0074_seed5/trace_full_obs_footpos.jsonl | 110-134 | `none` | 0.0666 | 0.1884 | 0.0521 | 0.1620 | 2.2850 | 0.1049 |
| ea0a0799d9692ede | published_policy_command_turning_x0074_yneg0037_yawneg0074_seed5/trace_full_obs_footpos.jsonl | 115-139 | `none` | 0.0668 | 0.1999 | 0.0521 | 0.1611 | 2.3773 | 0.1145 |
| 296861383a4d9192 | published_policy_command_turning_x0074_yneg0037_yawneg0074_seed5/trace_full_obs_footpos.jsonl | 175-199 | `none` | 0.0664 | 0.1904 | 0.0470 | 0.1620 | 2.7023 | 0.1182 |
| 944b90900a69a25b | published_policy_command_turning_x0074_yneg0037_yawneg0074_seed5/trace_full_obs_footpos.jsonl | 180-204 | `none` | 0.0683 | 0.1865 | 0.0495 | 0.1620 | 2.6104 | 0.1143 |
| a17c8a24af241132 | published_policy_command_turning_x0074_yneg0037_yawneg0074_seed5/trace_full_obs_footpos.jsonl | 185-209 | `none` | 0.0706 | 0.1887 | 0.0504 | 0.1620 | 2.3524 | 0.1137 |
| c2b13c20ad1fb393 | published_policy_command_turning_x0074_yneg0037_yawneg0074_seed5/trace_full_obs_footpos.jsonl | 190-214 | `none` | 0.0720 | 0.1887 | 0.0571 | 0.1620 | 2.3657 | 0.1176 |
| 669aa233dff03406 | published_policy_command_turning_x0074_yneg0037_yawneg0074_seed5/trace_full_obs_footpos.jsonl | 195-219 | `none` | 0.0698 | 0.1917 | 0.0571 | 0.1614 | 2.4581 | 0.1203 |
| 3cee10f3b17c3f99 | published_policy_command_turning_x0074_yneg0037_yawneg0074_seed5/trace_full_obs_footpos.jsonl | 200-224 | `none` | 0.0660 | 0.1917 | 0.0571 | 0.1614 | 2.4693 | 0.1178 |
| d77a2c6e4e06c8cc | published_policy_command_turning_x0074_yneg0037_yawneg0074_seed5/trace_full_obs_footpos.jsonl | 205-229 | `none` | 0.0668 | 0.1917 | 0.0571 | 0.1614 | 2.4693 | 0.1189 |
| 71f223c7d94758d7 | published_policy_command_turning_x0074_yneg0037_yawneg0074_seed6/trace_full_obs_footpos.jsonl | 15-39 | `none` | 0.0668 | 0.1694 | 0.0570 | 0.1580 | 2.6426 | 0.1239 |
| 8ef6a65bcad7f797 | published_policy_command_turning_x0074_yneg0037_yawneg0074_seed6/trace_full_obs_footpos.jsonl | 25-49 | `none` | 0.0699 | 0.1744 | 0.0570 | 0.1580 | 2.5772 | 0.1188 |
| 5f578cb578671b82 | published_policy_command_turning_x0074_yneg0037_yawneg0074_seed6/trace_full_obs_footpos.jsonl | 30-54 | `none` | 0.0695 | 0.1497 | 0.0579 | 0.1607 | 2.4756 | 0.1138 |
| b8eb4cdfb75905e2 | published_policy_command_turning_x0074_yneg0037_yawneg0074_seed6/trace_full_obs_footpos.jsonl | 60-84 | `none` | 0.0699 | 0.1989 | 0.0520 | 0.1623 | 2.7254 | 0.1189 |
| b1f1f965d06731fa | published_policy_command_turning_x0074_yneg0037_yawneg0074_seed6/trace_full_obs_footpos.jsonl | 65-89 | `none` | 0.0679 | 0.1989 | 0.0520 | 0.1623 | 2.6333 | 0.1125 |
| 51d4af454e83d42b | published_policy_command_turning_x0074_yneg0037_yawneg0074_seed6/trace_full_obs_footpos.jsonl | 70-94 | `none` | 0.0685 | 0.1989 | 0.0521 | 0.1623 | 2.6813 | 0.1156 |
| d9e5724efb038fdf | published_policy_command_turning_x0074_yneg0037_yawneg0074_seed6/trace_full_obs_footpos.jsonl | 75-99 | `none` | 0.0671 | 0.1849 | 0.0521 | 0.1623 | 2.6034 | 0.1191 |
| f1cd7b546f6e78fa | published_policy_command_turning_x0074_yneg0037_yawneg0074_seed6/trace_full_obs_footpos.jsonl | 100-124 | `none` | 0.0678 | 0.1820 | 0.0491 | 0.1620 | 2.5854 | 0.1171 |
| 7bf54327b89231d6 | published_policy_command_turning_x0074_yneg0037_yawneg0074_seed6/trace_full_obs_footpos.jsonl | 105-129 | `none` | 0.0722 | 0.1882 | 0.0496 | 0.1620 | 2.3637 | 0.1131 |
| 3284876ba9e57e52 | published_policy_command_turning_x0074_yneg0037_yawneg0074_seed6/trace_full_obs_footpos.jsonl | 110-134 | `none` | 0.0728 | 0.1882 | 0.0555 | 0.1620 | 2.4539 | 0.1119 |
| 1761f99e17e4c6d1 | published_policy_command_turning_x0074_yneg0037_yawneg0074_seed6/trace_full_obs_footpos.jsonl | 115-139 | `none` | 0.0714 | 0.1878 | 0.0555 | 0.1623 | 2.5185 | 0.1172 |
| f172f04ea24a7b38 | published_policy_command_turning_x0074_yneg0037_yawneg0074_seed6/trace_full_obs_footpos.jsonl | 155-179 | `none` | 0.0685 | 0.1899 | 0.0475 | 0.1619 | 2.5232 | 0.1162 |
| 8aea80e99f6f7b36 | published_policy_command_turning_x0074_yneg0037_yawneg0074_seed6/trace_full_obs_footpos.jsonl | 160-184 | `none` | 0.0734 | 0.1899 | 0.0494 | 0.1619 | 2.4946 | 0.1134 |
| 1a1eb44f868921da | published_policy_command_turning_x0074_yneg0037_yawneg0074_seed6/trace_full_obs_footpos.jsonl | 165-189 | `none` | 0.0715 | 0.1707 | 0.0550 | 0.1623 | 2.4946 | 0.1121 |
| a27be49a7cf9d4ee | published_policy_command_turning_x0074_yneg0037_yawneg0074_seed6/trace_full_obs_footpos.jsonl | 170-194 | `none` | 0.0692 | 0.1807 | 0.0550 | 0.1620 | 2.4926 | 0.1135 |
| 6ffc3cb9fd53f8d7 | published_policy_command_turning_x0074_yneg0037_yawneg0074_seed6/trace_full_obs_footpos.jsonl | 180-204 | `none` | 0.0684 | 0.1775 | 0.0550 | 0.1620 | 2.5910 | 0.1140 |
| c2cb256b5ddd7eaf | published_policy_command_turning_x0074_yneg0037_yawneg0074_seed6/trace_full_obs_footpos.jsonl | 190-214 | `none` | 0.0674 | 0.1940 | 0.0529 | 0.1620 | 2.3725 | 0.1146 |
| 09e08bf7b66429a7 | published_policy_command_turning_x0074_yneg0037_yawneg0074_seed6/trace_full_obs_footpos.jsonl | 195-219 | `none` | 0.0679 | 0.1939 | 0.0529 | 0.1620 | 2.5570 | 0.1149 |
| cd7b6b24e5cde638 | published_policy_command_turning_x0074_yneg0037_yawneg0074_seed7/trace_full_obs_footpos.jsonl | 35-59 | `none` | 0.0661 | 0.1861 | 0.0541 | 0.1620 | 2.3223 | 0.1121 |
| 158af48ab56eb484 | published_policy_command_turning_x0074_yneg0037_yawneg0074_seed7/trace_full_obs_footpos.jsonl | 45-69 | `none` | 0.0649 | 0.1860 | 0.0541 | 0.1620 | 2.4920 | 0.1119 |
| 0e4fad59f9885de7 | published_policy_command_turning_x0074_yneg0037_yawneg0074_seed7/trace_full_obs_footpos.jsonl | 140-164 | `none` | 0.0682 | 0.1779 | 0.0513 | 0.1621 | 2.7307 | 0.1138 |
| 2edc949d8a795196 | published_policy_command_turning_x0074_yneg0037_yawneg0074_seed7/trace_full_obs_footpos.jsonl | 145-169 | `none` | 0.0667 | 0.1865 | 0.0513 | 0.1621 | 2.6209 | 0.1138 |
| aa998a3444c34271 | published_policy_command_turning_x0074_yneg0037_yawneg0074_seed7/trace_full_obs_footpos.jsonl | 150-174 | `none` | 0.0658 | 0.1865 | 0.0513 | 0.1621 | 2.6438 | 0.1171 |
| fb8ba1c1993fb1bf | published_policy_command_turning_x0074_yneg0037_yawneg0074_seed7/trace_full_obs_footpos.jsonl | 155-179 | `none` | 0.0657 | 0.1950 | 0.0513 | 0.1621 | 2.6278 | 0.1171 |
| 514b59c8eb98e2ef | published_policy_command_turning_x0074_yneg0037_yawneg0074_seed7/trace_full_obs_footpos.jsonl | 160-184 | `none` | 0.0665 | 0.1950 | 0.0501 | 0.1621 | 2.5717 | 0.1129 |
| 02f6e74643b6a0e8 | published_policy_command_turning_x0074_yneg0037_yawneg0074_seed7/trace_full_obs_footpos.jsonl | 165-189 | `none` | 0.0668 | 0.1914 | 0.0532 | 0.1625 | 2.4132 | 0.1099 |
| 8845413504b7aa55 | published_policy_command_turning_x0074_yneg0037_yawneg0074_seed7/trace_full_obs_footpos.jsonl | 170-194 | `none` | 0.0671 | 0.1943 | 0.0532 | 0.1621 | 2.4995 | 0.1136 |
| c64cc18795dcc2d0 | published_policy_command_turning_x0074_yneg0037_yawneg0074_seed7/trace_full_obs_footpos.jsonl | 175-199 | `none` | 0.0660 | 0.1943 | 0.0532 | 0.1621 | 2.6102 | 0.1137 |
| 16813c484ad65311 | published_policy_command_turning_x0074_yneg0037_yawneg0074_seed7/trace_full_obs_footpos.jsonl | 180-204 | `none` | 0.0678 | 0.1782 | 0.0532 | 0.1621 | 2.6102 | 0.1128 |
| 1c9847a9ddd2369d | published_policy_command_turning_x0074_yneg0037_yawneg0074_seed7/trace_full_obs_footpos.jsonl | 220-244 | `none` | 0.0657 | 0.1604 | 0.0524 | 0.1620 | 2.5490 | 0.1097 |
| c2ee8a7691c23793 | published_policy_command_turning_x0074_yneg0037_yawneg0074_seed7/trace_full_obs_footpos.jsonl | 225-249 | `none` | 0.0671 | 0.1861 | 0.0524 | 0.1620 | 2.4114 | 0.1118 |

## Gate

- A pass or warning-pass here only proves the compact manifest matches local trace evidence.
- `bc_readiness_status` must pass before behavior cloning or supervised action training.
- Review source skew before any supervised/imitation smoke run.
