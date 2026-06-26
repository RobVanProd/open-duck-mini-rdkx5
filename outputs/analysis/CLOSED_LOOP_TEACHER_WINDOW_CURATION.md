# Realized Target Window Curation

status: `PASS_CURATED_DATASET_SEED_READY`

This applies stricter dataset-readiness filters to the mined realized
motion windows. It does not export raw traces or start training.

## Criteria

- min_curated_windows: `8`
- min_mean_vx: `0.04`
- max_vy_abs_p95: `0.2`
- max_pitch_abs_p95: `0.35`
- min_base_height: `0.145`
- max_action_saturation_pct: `1.0`
- max_sent_velocity_p95: `3.75`
- max_tracking_p95: `0.14`
- min_done_margin: `50`
- max_contact_dominance_pct: `95.0`
- min_source_files: `1`
- min_source_mode_pairs: `1`

## Counts

- mined_windows: `301`
- pass_curated_seed_windows: `259`
- review_motion_hints: `40`
- rejected_dataset_seeds: `2`
- curated_source_files: `1`
- curated_modes: `1`
- curated_source_mode_pairs: `1`

## Curated Seed Windows

| source | mode | ticks | vx | vy95 | pitch95 | height_min | sent_vel95 | track95 | margin | contact_max |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|
| trace_full_obs_footpos.jsonl | `vanilla` | 0-24 | 0.0929 | 0.1398 | 0.0566 | 0.1521 | 3.3088 | 0.1392 | None | 60.0000 |
| trace_full_obs_footpos.jsonl | `vanilla` | 5-29 | 0.0833 | 0.1742 | 0.0569 | 0.1591 | 2.5879 | 0.1269 | None | 48.0000 |
| trace_full_obs_footpos.jsonl | `vanilla` | 80-104 | 0.0755 | 0.1997 | 0.0558 | 0.1625 | 2.4428 | 0.1154 | None | 44.0000 |
| trace_full_obs_footpos.jsonl | `vanilla` | 85-109 | 0.0743 | 0.1812 | 0.0558 | 0.1632 | 2.4038 | 0.1079 | None | 40.0000 |
| trace_full_obs_footpos.jsonl | `vanilla` | 15-39 | 0.0739 | 0.1793 | 0.0611 | 0.1591 | 2.5002 | 0.1255 | None | 60.0000 |
| trace_full_obs_footpos.jsonl | `vanilla` | 215-239 | 0.0723 | 0.1944 | 0.0507 | 0.1622 | 2.4908 | 0.1221 | None | 52.0000 |
| trace_full_obs_footpos.jsonl | `vanilla` | 90-114 | 0.0719 | 0.1924 | 0.0558 | 0.1632 | 2.3507 | 0.1114 | None | 36.0000 |
| trace_full_obs_footpos.jsonl | `vanilla` | 110-134 | 0.0718 | 0.1895 | 0.0567 | 0.1621 | 2.1831 | 0.1028 | None | 44.0000 |
| trace_full_obs_footpos.jsonl | `vanilla` | 100-124 | 0.0716 | 0.1691 | 0.0528 | 0.1626 | 2.3619 | 0.1096 | None | 40.0000 |
| trace_full_obs_footpos.jsonl | `vanilla` | 115-139 | 0.0714 | 0.1980 | 0.0567 | 0.1621 | 2.4002 | 0.1122 | None | 40.0000 |
| trace_full_obs_footpos.jsonl | `vanilla` | 75-99 | 0.0713 | 0.1997 | 0.0558 | 0.1625 | 2.3184 | 0.1208 | None | 36.0000 |
| trace_full_obs_footpos.jsonl | `vanilla` | 55-79 | 0.0713 | 0.1934 | 0.0528 | 0.1619 | 2.3807 | 0.1228 | None | 52.0000 |
| trace_full_obs_footpos.jsonl | `vanilla` | 220-244 | 0.0711 | 0.1820 | 0.0507 | 0.1622 | 2.4941 | 0.1131 | None | 48.0000 |
| trace_full_obs_footpos.jsonl | `vanilla` | 125-149 | 0.0711 | 0.1942 | 0.0567 | 0.1621 | 2.4691 | 0.1097 | None | 48.0000 |
| trace_full_obs_footpos.jsonl | `vanilla` | 105-129 | 0.0705 | 0.1895 | 0.0534 | 0.1621 | 2.1011 | 0.1072 | None | 40.0000 |
| trace_full_obs_footpos.jsonl | `vanilla` | 145-169 | 0.0704 | 0.1837 | 0.0530 | 0.1618 | 2.5163 | 0.1170 | None | 44.0000 |
| trace_full_obs_footpos.jsonl | `vanilla` | 95-119 | 0.0702 | 0.1924 | 0.0558 | 0.1632 | 2.3858 | 0.1154 | None | 44.0000 |
| trace_full_obs_footpos.jsonl | `vanilla` | 10-34 | 0.0702 | 0.1793 | 0.0569 | 0.1591 | 2.4700 | 0.1255 | None | 52.0000 |
| trace_full_obs_footpos.jsonl | `vanilla` | 220-244 | 0.0792 | 0.1728 | 0.0489 | 0.1625 | 2.5462 | 0.1201 | None | 48.0000 |
| trace_full_obs_footpos.jsonl | `vanilla` | 215-239 | 0.0779 | 0.1853 | 0.0489 | 0.1620 | 2.5624 | 0.1267 | None | 52.0000 |
| trace_full_obs_footpos.jsonl | `vanilla` | 110-134 | 0.0767 | 0.1888 | 0.0529 | 0.1619 | 2.2148 | 0.1137 | None | 48.0000 |
| trace_full_obs_footpos.jsonl | `vanilla` | 105-129 | 0.0766 | 0.1888 | 0.0529 | 0.1619 | 2.1702 | 0.1182 | None | 44.0000 |
| trace_full_obs_footpos.jsonl | `vanilla` | 225-249 | 0.0757 | 0.1950 | 0.0489 | 0.1625 | 2.4868 | 0.1262 | None | 44.0000 |
| trace_full_obs_footpos.jsonl | `vanilla` | 100-124 | 0.0753 | 0.1805 | 0.0531 | 0.1619 | 2.4991 | 0.1197 | None | 44.0000 |
| trace_full_obs_footpos.jsonl | `vanilla` | 205-229 | 0.0739 | 0.1851 | 0.0538 | 0.1620 | 2.5418 | 0.1162 | None | 48.0000 |
| trace_full_obs_footpos.jsonl | `vanilla` | 115-139 | 0.0729 | 0.1891 | 0.0529 | 0.1625 | 2.5154 | 0.1213 | None | 40.0000 |
| trace_full_obs_footpos.jsonl | `vanilla` | 210-234 | 0.0729 | 0.1853 | 0.0508 | 0.1620 | 2.5624 | 0.1280 | None | 44.0000 |
| trace_full_obs_footpos.jsonl | `vanilla` | 135-159 | 0.0728 | 0.1906 | 0.0513 | 0.1622 | 2.3077 | 0.1223 | None | 52.0000 |
| trace_full_obs_footpos.jsonl | `vanilla` | 140-164 | 0.0728 | 0.1791 | 0.0513 | 0.1622 | 2.5031 | 0.1170 | None | 44.0000 |
| trace_full_obs_footpos.jsonl | `vanilla` | 200-224 | 0.0725 | 0.1851 | 0.0538 | 0.1620 | 2.5418 | 0.1140 | None | 44.0000 |
| trace_full_obs_footpos.jsonl | `vanilla` | 125-149 | 0.0718 | 0.1862 | 0.0526 | 0.1625 | 2.5154 | 0.1113 | None | 48.0000 |
| trace_full_obs_footpos.jsonl | `vanilla` | 95-119 | 0.0716 | 0.1899 | 0.0555 | 0.1619 | 2.5100 | 0.1208 | None | 52.0000 |
| trace_full_obs_footpos.jsonl | `vanilla` | 185-209 | 0.0710 | 0.1950 | 0.0538 | 0.1622 | 2.1827 | 0.1130 | None | 40.0000 |
| trace_full_obs_footpos.jsonl | `vanilla` | 190-214 | 0.0708 | 0.1950 | 0.0538 | 0.1622 | 2.3419 | 0.1158 | None | 48.0000 |
| trace_full_obs_footpos.jsonl | `vanilla` | 180-204 | 0.0707 | 0.1647 | 0.0530 | 0.1623 | 2.5397 | 0.1158 | None | 48.0000 |
| trace_full_obs_footpos.jsonl | `vanilla` | 195-219 | 0.0705 | 0.1851 | 0.0538 | 0.1620 | 2.5418 | 0.1176 | None | 40.0000 |
| trace_full_obs_footpos.jsonl | `vanilla` | 170-194 | 0.0704 | 0.1966 | 0.0527 | 0.1621 | 2.4713 | 0.1178 | None | 44.0000 |
| trace_full_obs_footpos.jsonl | `vanilla` | 120-144 | 0.0698 | 0.1891 | 0.0529 | 0.1625 | 2.5154 | 0.1205 | None | 48.0000 |
| trace_full_obs_footpos.jsonl | `vanilla` | 5-29 | 0.0944 | 0.1618 | 0.0329 | 0.1598 | 2.6524 | 0.1192 | None | 52.0000 |
| trace_full_obs_footpos.jsonl | `vanilla` | 10-34 | 0.0809 | 0.1618 | 0.0369 | 0.1598 | 2.5406 | 0.1220 | None | 60.0000 |
| trace_full_obs_footpos.jsonl | `vanilla` | 15-39 | 0.0787 | 0.1608 | 0.0524 | 0.1598 | 2.5406 | 0.1304 | None | 64.0000 |
| trace_full_obs_footpos.jsonl | `vanilla` | 45-69 | 0.0746 | 0.1606 | 0.0532 | 0.1623 | 2.3263 | 0.1188 | None | 48.0000 |
| trace_full_obs_footpos.jsonl | `vanilla` | 180-204 | 0.0734 | 0.1622 | 0.0512 | 0.1621 | 2.5292 | 0.1116 | None | 48.0000 |
| trace_full_obs_footpos.jsonl | `vanilla` | 190-214 | 0.0732 | 0.1880 | 0.0536 | 0.1621 | 2.3125 | 0.1232 | None | 52.0000 |
| trace_full_obs_footpos.jsonl | `vanilla` | 25-49 | 0.0726 | 0.1907 | 0.0535 | 0.1598 | 2.5387 | 0.1247 | None | 56.0000 |
| trace_full_obs_footpos.jsonl | `vanilla` | 55-79 | 0.0723 | 0.1935 | 0.0541 | 0.1623 | 2.3118 | 0.1149 | None | 48.0000 |
| trace_full_obs_footpos.jsonl | `vanilla` | 20-44 | 0.0722 | 0.1907 | 0.0524 | 0.1598 | 2.4086 | 0.1252 | None | 48.0000 |
| trace_full_obs_footpos.jsonl | `vanilla` | 30-54 | 0.0720 | 0.1867 | 0.0535 | 0.1620 | 2.5601 | 0.1220 | None | 52.0000 |
| trace_full_obs_footpos.jsonl | `vanilla` | 135-159 | 0.0714 | 0.1888 | 0.0534 | 0.1621 | 2.4056 | 0.1244 | None | 52.0000 |
| trace_full_obs_footpos.jsonl | `vanilla` | 175-199 | 0.0713 | 0.1877 | 0.0512 | 0.1621 | 2.4145 | 0.1185 | None | 48.0000 |
| trace_full_obs_footpos.jsonl | `vanilla` | 50-74 | 0.0713 | 0.1935 | 0.0541 | 0.1623 | 2.2537 | 0.1118 | None | 40.0000 |
| trace_full_obs_footpos.jsonl | `vanilla` | 170-194 | 0.0709 | 0.1877 | 0.0509 | 0.1621 | 2.3547 | 0.1144 | None | 40.0000 |
| trace_full_obs_footpos.jsonl | `vanilla` | 60-84 | 0.0709 | 0.1852 | 0.0541 | 0.1619 | 2.5155 | 0.1189 | None | 40.0000 |
| trace_full_obs_footpos.jsonl | `vanilla` | 195-219 | 0.0709 | 0.1982 | 0.0536 | 0.1623 | 2.4938 | 0.1263 | None | 44.0000 |
| trace_full_obs_footpos.jsonl | `vanilla` | 140-164 | 0.0706 | 0.1801 | 0.0534 | 0.1621 | 2.5681 | 0.1204 | None | 44.0000 |
| trace_full_obs_footpos.jsonl | `vanilla` | 110-134 | 0.0740 | 0.1898 | 0.0496 | 0.1624 | 2.4323 | 0.1146 | None | 48.0000 |
| trace_full_obs_footpos.jsonl | `vanilla` | 125-149 | 0.0726 | 0.1965 | 0.0517 | 0.1622 | 2.4586 | 0.1127 | None | 48.0000 |
| trace_full_obs_footpos.jsonl | `vanilla` | 215-239 | 0.0723 | 0.1884 | 0.0526 | 0.1623 | 2.3979 | 0.1155 | None | 48.0000 |
| trace_full_obs_footpos.jsonl | `vanilla` | 105-129 | 0.0723 | 0.1898 | 0.0491 | 0.1624 | 2.2395 | 0.1168 | None | 44.0000 |
| trace_full_obs_footpos.jsonl | `vanilla` | 220-244 | 0.0718 | 0.1643 | 0.0532 | 0.1619 | 2.4207 | 0.1092 | None | 44.0000 |
| trace_full_obs_footpos.jsonl | `vanilla` | 165-189 | 0.0715 | 0.1822 | 0.0529 | 0.1622 | 2.5488 | 0.1157 | None | 52.0000 |
| trace_full_obs_footpos.jsonl | `vanilla` | 150-174 | 0.0714 | 0.1822 | 0.0530 | 0.1616 | 2.4896 | 0.1210 | None | 48.0000 |
| trace_full_obs_footpos.jsonl | `vanilla` | 145-169 | 0.0711 | 0.1822 | 0.0525 | 0.1616 | 2.3867 | 0.1127 | None | 40.0000 |
| trace_full_obs_footpos.jsonl | `vanilla` | 155-179 | 0.0709 | 0.1822 | 0.0528 | 0.1616 | 2.4984 | 0.1219 | None | 44.0000 |
| trace_full_obs_footpos.jsonl | `vanilla` | 160-184 | 0.0706 | 0.1822 | 0.0529 | 0.1616 | 2.4793 | 0.1210 | None | 52.0000 |
| trace_full_obs_footpos.jsonl | `vanilla` | 100-124 | 0.0703 | 0.1723 | 0.0495 | 0.1624 | 2.4342 | 0.1176 | None | 44.0000 |
| trace_full_obs_footpos.jsonl | `vanilla` | 80-104 | 0.0700 | 0.1930 | 0.0528 | 0.1617 | 2.4385 | 0.1186 | None | 48.0000 |
| trace_full_obs_footpos.jsonl | `vanilla` | 90-114 | 0.0700 | 0.1902 | 0.0528 | 0.1624 | 2.4237 | 0.1164 | None | 40.0000 |
| trace_full_obs_footpos.jsonl | `vanilla` | 210-234 | 0.0699 | 0.1884 | 0.0517 | 0.1623 | 2.2786 | 0.1206 | None | 40.0000 |
| trace_full_obs_footpos.jsonl | `vanilla` | 205-229 | 0.0698 | 0.1927 | 0.0531 | 0.1618 | 2.3433 | 0.1206 | None | 52.0000 |
| trace_full_obs_footpos.jsonl | `vanilla` | 85-109 | 0.0695 | 0.1714 | 0.0528 | 0.1624 | 2.4605 | 0.1067 | None | 44.0000 |
| trace_full_obs_footpos.jsonl | `vanilla` | 140-164 | 0.0694 | 0.1760 | 0.0525 | 0.1616 | 2.4671 | 0.1101 | None | 40.0000 |
| trace_full_obs_footpos.jsonl | `vanilla` | 0-24 | 0.0855 | 0.1628 | 0.0797 | 0.1506 | 3.1965 | 0.1295 | None | 72.0000 |
| trace_full_obs_footpos.jsonl | `vanilla` | 215-239 | 0.0769 | 0.1815 | 0.0558 | 0.1618 | 2.4944 | 0.1172 | None | 48.0000 |
| trace_full_obs_footpos.jsonl | `vanilla` | 220-244 | 0.0759 | 0.1657 | 0.0558 | 0.1622 | 2.5887 | 0.1106 | None | 44.0000 |
| trace_full_obs_footpos.jsonl | `vanilla` | 210-234 | 0.0729 | 0.1815 | 0.0558 | 0.1618 | 2.4672 | 0.1206 | None | 40.0000 |
| trace_full_obs_footpos.jsonl | `vanilla` | 205-229 | 0.0728 | 0.1824 | 0.0553 | 0.1618 | 2.4672 | 0.1124 | None | 48.0000 |
| trace_full_obs_footpos.jsonl | `vanilla` | 225-249 | 0.0711 | 0.1937 | 0.0558 | 0.1622 | 2.4944 | 0.1147 | None | 40.0000 |
| trace_full_obs_footpos.jsonl | `vanilla` | 200-224 | 0.0700 | 0.1824 | 0.0550 | 0.1618 | 2.4766 | 0.1151 | None | 44.0000 |
| trace_full_obs_footpos.jsonl | `vanilla` | 190-214 | 0.0687 | 0.1831 | 0.0551 | 0.1617 | 2.2774 | 0.1174 | None | 48.0000 |
| trace_full_obs_footpos.jsonl | `vanilla` | 195-219 | 0.0685 | 0.1824 | 0.0551 | 0.1618 | 2.5043 | 0.1195 | None | 40.0000 |
| trace_full_obs_footpos.jsonl | `vanilla` | 180-204 | 0.0659 | 0.1737 | 0.0619 | 0.1617 | 2.3943 | 0.1183 | None | 48.0000 |
| trace_full_obs_footpos.jsonl | `vanilla` | 185-209 | 0.0654 | 0.1831 | 0.0565 | 0.1617 | 2.1992 | 0.1137 | None | 40.0000 |
| trace_full_obs_footpos.jsonl | `vanilla` | 175-199 | 0.0621 | 0.1831 | 0.0642 | 0.1601 | 2.4714 | 0.1250 | None | 52.0000 |
| trace_full_obs_footpos.jsonl | `vanilla` | 165-189 | 0.0616 | 0.1721 | 0.0692 | 0.1601 | 2.4413 | 0.1183 | None | 52.0000 |
| trace_full_obs_footpos.jsonl | `vanilla` | 170-194 | 0.0612 | 0.1831 | 0.0692 | 0.1601 | 2.4413 | 0.1237 | None | 44.0000 |
| trace_full_obs_footpos.jsonl | `vanilla` | 5-29 | 0.0578 | 0.1628 | 0.0840 | 0.1603 | 2.1630 | 0.0862 | None | 80.0000 |
| trace_full_obs_footpos.jsonl | `vanilla` | 150-174 | 0.0522 | 0.1608 | 0.0695 | 0.1574 | 2.5666 | 0.1181 | None | 64.0000 |
| trace_full_obs_footpos.jsonl | `vanilla` | 145-169 | 0.0431 | 0.1608 | 0.0702 | 0.1574 | 2.3208 | 0.1082 | None | 64.0000 |
| trace_full_obs_footpos.jsonl | `vanilla` | 25-49 | 0.0847 | 0.1650 | 0.0578 | 0.1601 | 2.5501 | 0.1228 | None | 56.0000 |
| trace_full_obs_footpos.jsonl | `vanilla` | 30-54 | 0.0796 | 0.1626 | 0.0585 | 0.1607 | 2.5775 | 0.1178 | None | 52.0000 |
| trace_full_obs_footpos.jsonl | `vanilla` | 20-44 | 0.0770 | 0.1650 | 0.0524 | 0.1601 | 2.8251 | 0.1218 | None | 44.0000 |
| trace_full_obs_footpos.jsonl | `vanilla` | 80-104 | 0.0733 | 0.1916 | 0.0534 | 0.1616 | 2.3763 | 0.1213 | None | 52.0000 |
| trace_full_obs_footpos.jsonl | `vanilla` | 135-159 | 0.0724 | 0.1881 | 0.0547 | 0.1621 | 2.4305 | 0.1250 | None | 52.0000 |
| trace_full_obs_footpos.jsonl | `vanilla` | 35-59 | 0.0723 | 0.1887 | 0.0585 | 0.1607 | 2.5451 | 0.1250 | None | 44.0000 |
| trace_full_obs_footpos.jsonl | `vanilla` | 140-164 | 0.0720 | 0.1759 | 0.0547 | 0.1622 | 2.5585 | 0.1190 | None | 44.0000 |
| trace_full_obs_footpos.jsonl | `vanilla` | 75-99 | 0.0715 | 0.1916 | 0.0488 | 0.1616 | 2.4062 | 0.1237 | None | 44.0000 |
| trace_full_obs_footpos.jsonl | `vanilla` | 60-84 | 0.0713 | 0.1825 | 0.0555 | 0.1626 | 2.5750 | 0.1214 | None | 40.0000 |
| trace_full_obs_footpos.jsonl | `vanilla` | 85-109 | 0.0710 | 0.1829 | 0.0538 | 0.1616 | 2.4228 | 0.1140 | None | 48.0000 |
| trace_full_obs_footpos.jsonl | `vanilla` | 45-69 | 0.0709 | 0.1701 | 0.0585 | 0.1616 | 2.5760 | 0.1202 | None | 48.0000 |
| trace_full_obs_footpos.jsonl | `vanilla` | 115-139 | 0.0708 | 0.1883 | 0.0541 | 0.1621 | 2.4422 | 0.1229 | None | 44.0000 |
| trace_full_obs_footpos.jsonl | `vanilla` | 40-64 | 0.0708 | 0.1887 | 0.0585 | 0.1607 | 2.6560 | 0.1250 | None | 52.0000 |
| trace_full_obs_footpos.jsonl | `vanilla` | 70-94 | 0.0707 | 0.1825 | 0.0539 | 0.1626 | 2.5006 | 0.1192 | None | 48.0000 |
| trace_full_obs_footpos.jsonl | `vanilla` | 110-134 | 0.0706 | 0.1893 | 0.0541 | 0.1620 | 2.3947 | 0.1166 | None | 52.0000 |
| trace_full_obs_footpos.jsonl | `vanilla` | 55-79 | 0.0706 | 0.1887 | 0.0555 | 0.1616 | 2.5006 | 0.1202 | None | 48.0000 |
| trace_full_obs_footpos.jsonl | `vanilla` | 100-124 | 0.0702 | 0.1773 | 0.0541 | 0.1620 | 2.3523 | 0.1183 | None | 44.0000 |
| trace_full_obs_footpos.jsonl | `vanilla` | 220-244 | 0.0702 | 0.1739 | 0.0537 | 0.1622 | 2.5297 | 0.1116 | None | 48.0000 |
| trace_full_obs_footpos.jsonl | `vanilla` | 95-119 | 0.0699 | 0.1923 | 0.0541 | 0.1616 | 2.4148 | 0.1224 | None | 52.0000 |
| trace_full_obs_footpos.jsonl | `vanilla` | 190-214 | 0.0818 | 0.1931 | 0.0439 | 0.1622 | 2.4517 | 0.1250 | None | 52.0000 |
| trace_full_obs_footpos.jsonl | `vanilla` | 110-134 | 0.0817 | 0.1984 | 0.0510 | 0.1626 | 2.4810 | 0.1143 | None | 48.0000 |
| trace_full_obs_footpos.jsonl | `vanilla` | 115-139 | 0.0801 | 0.1985 | 0.0510 | 0.1628 | 2.5109 | 0.1193 | None | 36.0000 |
| trace_full_obs_footpos.jsonl | `vanilla` | 205-229 | 0.0795 | 0.1970 | 0.0503 | 0.1622 | 2.4834 | 0.1224 | None | 52.0000 |
| trace_full_obs_footpos.jsonl | `vanilla` | 200-224 | 0.0794 | 0.1970 | 0.0439 | 0.1622 | 2.5658 | 0.1233 | None | 48.0000 |
| trace_full_obs_footpos.jsonl | `vanilla` | 195-219 | 0.0794 | 0.1970 | 0.0439 | 0.1622 | 2.5907 | 0.1268 | None | 44.0000 |
| trace_full_obs_footpos.jsonl | `vanilla` | 105-129 | 0.0793 | 0.1984 | 0.0503 | 0.1625 | 2.4453 | 0.1156 | None | 44.0000 |
| trace_full_obs_footpos.jsonl | `vanilla` | 100-124 | 0.0790 | 0.1674 | 0.0489 | 0.1625 | 2.5898 | 0.1156 | None | 44.0000 |
| trace_full_obs_footpos.jsonl | `vanilla` | 80-104 | 0.0789 | 0.1816 | 0.0515 | 0.1621 | 2.5732 | 0.1173 | None | 48.0000 |
| trace_full_obs_footpos.jsonl | `vanilla` | 85-109 | 0.0785 | 0.1677 | 0.0515 | 0.1625 | 2.6465 | 0.1108 | None | 44.0000 |
| trace_full_obs_footpos.jsonl | `vanilla` | 185-209 | 0.0771 | 0.1931 | 0.0428 | 0.1622 | 2.4528 | 0.1190 | None | 44.0000 |
| trace_full_obs_footpos.jsonl | `vanilla` | 95-119 | 0.0767 | 0.1987 | 0.0506 | 0.1625 | 2.6021 | 0.1209 | None | 48.0000 |
| trace_full_obs_footpos.jsonl | `vanilla` | 120-144 | 0.0765 | 0.1985 | 0.0510 | 0.1628 | 2.4380 | 0.1193 | None | 44.0000 |
| trace_full_obs_footpos.jsonl | `vanilla` | 90-114 | 0.0762 | 0.1987 | 0.0515 | 0.1625 | 2.5620 | 0.1167 | None | 40.0000 |
| trace_full_obs_footpos.jsonl | `vanilla` | 125-149 | 0.0760 | 0.1962 | 0.0544 | 0.1628 | 2.3829 | 0.1080 | None | 44.0000 |
| trace_full_obs_footpos.jsonl | `vanilla` | 15-39 | 0.0751 | 0.1923 | 0.0552 | 0.1593 | 2.4647 | 0.1298 | None | 60.0000 |
| trace_full_obs_footpos.jsonl | `vanilla` | 220-244 | 0.0743 | 0.1688 | 0.0533 | 0.1626 | 2.4639 | 0.1106 | None | 44.0000 |
| trace_full_obs_footpos.jsonl | `vanilla` | 70-94 | 0.0742 | 0.1824 | 0.0546 | 0.1621 | 2.5038 | 0.1149 | None | 48.0000 |
| trace_full_obs_footpos.jsonl | `vanilla` | 110-134 | 0.0798 | 0.1882 | 0.0503 | 0.1624 | 2.4582 | 0.1134 | None | 48.0000 |
| trace_full_obs_footpos.jsonl | `vanilla` | 105-129 | 0.0791 | 0.1882 | 0.0503 | 0.1624 | 2.3456 | 0.1156 | None | 44.0000 |
| trace_full_obs_footpos.jsonl | `vanilla` | 80-104 | 0.0788 | 0.1839 | 0.0509 | 0.1624 | 2.4327 | 0.1208 | None | 52.0000 |
| trace_full_obs_footpos.jsonl | `vanilla` | 85-109 | 0.0785 | 0.1718 | 0.0509 | 0.1624 | 2.4628 | 0.1136 | None | 48.0000 |
| trace_full_obs_footpos.jsonl | `vanilla` | 100-124 | 0.0777 | 0.1641 | 0.0502 | 0.1624 | 2.4372 | 0.1170 | None | 44.0000 |
| trace_full_obs_footpos.jsonl | `vanilla` | 225-249 | 0.0771 | 0.1912 | 0.0491 | 0.1625 | 2.3983 | 0.1113 | None | 40.0000 |
| trace_full_obs_footpos.jsonl | `vanilla` | 90-114 | 0.0766 | 0.1904 | 0.0509 | 0.1624 | 2.4276 | 0.1190 | None | 44.0000 |
| trace_full_obs_footpos.jsonl | `vanilla` | 95-119 | 0.0766 | 0.1904 | 0.0509 | 0.1624 | 2.4276 | 0.1233 | None | 52.0000 |
| trace_full_obs_footpos.jsonl | `vanilla` | 75-99 | 0.0763 | 0.1839 | 0.0503 | 0.1624 | 2.3136 | 0.1231 | None | 44.0000 |
| trace_full_obs_footpos.jsonl | `vanilla` | 180-204 | 0.0762 | 0.1649 | 0.0547 | 0.1629 | 2.5574 | 0.1166 | None | 48.0000 |
| trace_full_obs_footpos.jsonl | `vanilla` | 55-79 | 0.0761 | 0.1802 | 0.0533 | 0.1621 | 2.4394 | 0.1220 | None | 52.0000 |
| trace_full_obs_footpos.jsonl | `vanilla` | 70-94 | 0.0756 | 0.1846 | 0.0533 | 0.1621 | 2.4580 | 0.1185 | None | 52.0000 |
| trace_full_obs_footpos.jsonl | `vanilla` | 220-244 | 0.0751 | 0.1698 | 0.0491 | 0.1625 | 2.6562 | 0.1079 | None | 44.0000 |
| trace_full_obs_footpos.jsonl | `vanilla` | 165-189 | 0.0750 | 0.1873 | 0.0552 | 0.1623 | 2.4428 | 0.1151 | None | 52.0000 |
| trace_full_obs_footpos.jsonl | `vanilla` | 45-69 | 0.0749 | 0.1607 | 0.0544 | 0.1622 | 2.5639 | 0.1126 | None | 48.0000 |
| trace_full_obs_footpos.jsonl | `vanilla` | 215-239 | 0.0728 | 0.1918 | 0.0492 | 0.1622 | 2.5042 | 0.1128 | None | 52.0000 |
| trace_full_obs_footpos.jsonl | `vanilla` | 220-244 | 0.0703 | 0.1604 | 0.0532 | 0.1621 | 2.5409 | 0.1114 | None | 48.0000 |
| trace_full_obs_footpos.jsonl | `vanilla` | 60-84 | 0.0700 | 0.1817 | 0.0496 | 0.1622 | 2.7356 | 0.1180 | None | 40.0000 |
| trace_full_obs_footpos.jsonl | `vanilla` | 210-234 | 0.0696 | 0.1918 | 0.0467 | 0.1622 | 2.4990 | 0.1195 | None | 44.0000 |
| trace_full_obs_footpos.jsonl | `vanilla` | 5-29 | 0.0692 | 0.1810 | 0.0424 | 0.1598 | 2.5812 | 0.1213 | None | 52.0000 |
| trace_full_obs_footpos.jsonl | `vanilla` | 225-249 | 0.0689 | 0.1893 | 0.0532 | 0.1621 | 2.4153 | 0.1126 | None | 40.0000 |
| trace_full_obs_footpos.jsonl | `vanilla` | 205-229 | 0.0680 | 0.1896 | 0.0472 | 0.1622 | 2.6876 | 0.1170 | None | 52.0000 |
| trace_full_obs_footpos.jsonl | `vanilla` | 70-94 | 0.0676 | 0.1817 | 0.0496 | 0.1622 | 2.5028 | 0.1167 | None | 48.0000 |
| trace_full_obs_footpos.jsonl | `vanilla` | 65-89 | 0.0676 | 0.1817 | 0.0496 | 0.1622 | 2.5959 | 0.1139 | None | 44.0000 |
| trace_full_obs_footpos.jsonl | `vanilla` | 15-39 | 0.0669 | 0.1822 | 0.0530 | 0.1598 | 2.4240 | 0.1192 | None | 60.0000 |
| trace_full_obs_footpos.jsonl | `vanilla` | 190-214 | 0.0668 | 0.1986 | 0.0484 | 0.1617 | 2.5606 | 0.1181 | None | 52.0000 |
| trace_full_obs_footpos.jsonl | `vanilla` | 195-219 | 0.0668 | 0.1896 | 0.0484 | 0.1622 | 2.7519 | 0.1206 | None | 44.0000 |
| trace_full_obs_footpos.jsonl | `vanilla` | 25-49 | 0.0666 | 0.1878 | 0.0530 | 0.1598 | 2.5210 | 0.1105 | None | 52.0000 |
| trace_full_obs_footpos.jsonl | `vanilla` | 180-204 | 0.0660 | 0.1905 | 0.0496 | 0.1617 | 2.5575 | 0.1148 | None | 48.0000 |
| trace_full_obs_footpos.jsonl | `vanilla` | 45-69 | 0.0659 | 0.1990 | 0.0554 | 0.1614 | 2.6433 | 0.1124 | None | 48.0000 |
| trace_full_obs_footpos.jsonl | `vanilla` | 20-44 | 0.0657 | 0.1878 | 0.0530 | 0.1598 | 2.4240 | 0.1133 | None | 44.0000 |
| trace_full_obs_footpos.jsonl | `vanilla` | 200-224 | 0.0654 | 0.1896 | 0.0472 | 0.1622 | 2.6940 | 0.1135 | None | 48.0000 |
| trace_full_obs_footpos.jsonl | `vanilla` | 205-229 | 0.0716 | 0.1894 | 0.0514 | 0.1618 | 2.4267 | 0.1150 | None | 52.0000 |
| trace_full_obs_footpos.jsonl | `vanilla` | 215-239 | 0.0716 | 0.1921 | 0.0533 | 0.1618 | 2.5625 | 0.1169 | None | 52.0000 |
| trace_full_obs_footpos.jsonl | `vanilla` | 190-214 | 0.0714 | 0.1899 | 0.0514 | 0.1616 | 2.3626 | 0.1148 | None | 52.0000 |
| trace_full_obs_footpos.jsonl | `vanilla` | 195-219 | 0.0706 | 0.1894 | 0.0514 | 0.1618 | 2.5487 | 0.1174 | None | 44.0000 |
| trace_full_obs_footpos.jsonl | `vanilla` | 200-224 | 0.0705 | 0.1894 | 0.0514 | 0.1618 | 2.4664 | 0.1147 | None | 48.0000 |
| trace_full_obs_footpos.jsonl | `vanilla` | 185-209 | 0.0699 | 0.1899 | 0.0508 | 0.1616 | 2.3815 | 0.1143 | None | 44.0000 |
| trace_full_obs_footpos.jsonl | `vanilla` | 220-244 | 0.0698 | 0.1600 | 0.0569 | 0.1619 | 2.4459 | 0.1118 | None | 48.0000 |
| trace_full_obs_footpos.jsonl | `vanilla` | 210-234 | 0.0685 | 0.1921 | 0.0514 | 0.1618 | 2.4459 | 0.1189 | None | 44.0000 |
| trace_full_obs_footpos.jsonl | `vanilla` | 225-249 | 0.0669 | 0.1849 | 0.0569 | 0.1619 | 2.3825 | 0.1132 | None | 40.0000 |
| trace_full_obs_footpos.jsonl | `vanilla` | 180-204 | 0.0662 | 0.1851 | 0.0512 | 0.1616 | 2.7260 | 0.1204 | None | 48.0000 |
| trace_full_obs_footpos.jsonl | `vanilla` | 150-174 | 0.0659 | 0.1993 | 0.0551 | 0.1616 | 2.4196 | 0.1172 | None | 52.0000 |
| trace_full_obs_footpos.jsonl | `vanilla` | 145-169 | 0.0645 | 0.1993 | 0.0544 | 0.1616 | 2.3811 | 0.1134 | None | 44.0000 |
| trace_full_obs_footpos.jsonl | `vanilla` | 135-159 | 0.0643 | 0.1855 | 0.0531 | 0.1600 | 2.4196 | 0.1167 | None | 52.0000 |
| trace_full_obs_footpos.jsonl | `vanilla` | 165-189 | 0.0642 | 0.1932 | 0.0541 | 0.1620 | 2.6051 | 0.1128 | None | 52.0000 |
| trace_full_obs_footpos.jsonl | `vanilla` | 140-164 | 0.0636 | 0.1796 | 0.0544 | 0.1616 | 2.5075 | 0.1118 | None | 44.0000 |
| trace_full_obs_footpos.jsonl | `vanilla` | 125-149 | 0.0619 | 0.1852 | 0.0554 | 0.1600 | 2.4938 | 0.1121 | None | 52.0000 |
| trace_full_obs_footpos.jsonl | `vanilla` | 0-24 | 0.1008 | 0.1331 | 0.0415 | 0.1510 | 2.7390 | 0.1181 | None | 52.0000 |
| trace_full_obs_footpos.jsonl | `vanilla` | 5-29 | 0.0809 | 0.1434 | 0.0532 | 0.1562 | 2.5848 | 0.1088 | None | 60.0000 |
| trace_full_obs_footpos.jsonl | `vanilla` | 180-204 | 0.0672 | 0.1867 | 0.0515 | 0.1620 | 2.4781 | 0.1121 | None | 44.0000 |
| trace_full_obs_footpos.jsonl | `vanilla` | 110-134 | 0.0670 | 0.1917 | 0.0550 | 0.1619 | 2.3842 | 0.1119 | None | 52.0000 |
| trace_full_obs_footpos.jsonl | `vanilla` | 105-129 | 0.0668 | 0.1917 | 0.0523 | 0.1618 | 2.3416 | 0.1159 | None | 48.0000 |
| trace_full_obs_footpos.jsonl | `vanilla` | 170-194 | 0.0668 | 0.1886 | 0.0515 | 0.1620 | 2.4781 | 0.1120 | None | 40.0000 |
| trace_full_obs_footpos.jsonl | `vanilla` | 115-139 | 0.0666 | 0.1887 | 0.0550 | 0.1618 | 2.4574 | 0.1162 | None | 40.0000 |
| trace_full_obs_footpos.jsonl | `vanilla` | 100-124 | 0.0665 | 0.1890 | 0.0528 | 0.1618 | 2.7007 | 0.1182 | None | 44.0000 |
| trace_full_obs_footpos.jsonl | `vanilla` | 95-119 | 0.0663 | 0.1927 | 0.0528 | 0.1618 | 2.6366 | 0.1202 | None | 52.0000 |
| trace_full_obs_footpos.jsonl | `vanilla` | 90-114 | 0.0663 | 0.1927 | 0.0528 | 0.1618 | 2.5381 | 0.1182 | None | 44.0000 |
| trace_full_obs_footpos.jsonl | `vanilla` | 215-239 | 0.0662 | 0.1952 | 0.0520 | 0.1614 | 2.5327 | 0.1154 | None | 52.0000 |
| trace_full_obs_footpos.jsonl | `vanilla` | 85-109 | 0.0661 | 0.1580 | 0.0528 | 0.1618 | 2.7301 | 0.1141 | None | 48.0000 |
| trace_full_obs_footpos.jsonl | `vanilla` | 165-189 | 0.0660 | 0.1798 | 0.0515 | 0.1619 | 2.4868 | 0.1111 | None | 52.0000 |
| trace_full_obs_footpos.jsonl | `vanilla` | 210-234 | 0.0647 | 0.1952 | 0.0520 | 0.1614 | 2.5063 | 0.1159 | None | 44.0000 |
| trace_full_obs_footpos.jsonl | `vanilla` | 115-139 | 0.0692 | 0.1876 | 0.0517 | 0.1620 | 2.4511 | 0.1155 | None | 40.0000 |
| trace_full_obs_footpos.jsonl | `vanilla` | 110-134 | 0.0692 | 0.1885 | 0.0517 | 0.1619 | 2.4028 | 0.1092 | None | 52.0000 |
| trace_full_obs_footpos.jsonl | `vanilla` | 100-124 | 0.0691 | 0.1860 | 0.0511 | 0.1618 | 2.5479 | 0.1194 | None | 44.0000 |
| trace_full_obs_footpos.jsonl | `vanilla` | 85-109 | 0.0691 | 0.1566 | 0.0511 | 0.1618 | 2.6075 | 0.1160 | None | 48.0000 |
| trace_full_obs_footpos.jsonl | `vanilla` | 205-229 | 0.0684 | 0.1887 | 0.0531 | 0.1619 | 2.4528 | 0.1143 | None | 48.0000 |
| trace_full_obs_footpos.jsonl | `vanilla` | 135-159 | 0.0684 | 0.1874 | 0.0509 | 0.1620 | 2.3417 | 0.1161 | None | 48.0000 |
| trace_full_obs_footpos.jsonl | `vanilla` | 190-214 | 0.0683 | 0.1956 | 0.0531 | 0.1615 | 2.3587 | 0.1160 | None | 52.0000 |
| trace_full_obs_footpos.jsonl | `vanilla` | 105-129 | 0.0683 | 0.1885 | 0.0510 | 0.1618 | 2.3553 | 0.1163 | None | 48.0000 |
| trace_full_obs_footpos.jsonl | `vanilla` | 215-239 | 0.0682 | 0.1887 | 0.0518 | 0.1619 | 2.5245 | 0.1159 | None | 48.0000 |
| trace_full_obs_footpos.jsonl | `vanilla` | 90-114 | 0.0682 | 0.1877 | 0.0511 | 0.1618 | 2.5062 | 0.1186 | None | 44.0000 |
| trace_full_obs_footpos.jsonl | `vanilla` | 220-244 | 0.0680 | 0.1598 | 0.0524 | 0.1619 | 2.4443 | 0.1119 | None | 48.0000 |
| trace_full_obs_footpos.jsonl | `vanilla` | 120-144 | 0.0679 | 0.1876 | 0.0517 | 0.1620 | 2.4891 | 0.1127 | None | 48.0000 |
| trace_full_obs_footpos.jsonl | `vanilla` | 180-204 | 0.0679 | 0.1878 | 0.0509 | 0.1615 | 2.5824 | 0.1166 | None | 48.0000 |
| trace_full_obs_footpos.jsonl | `vanilla` | 95-119 | 0.0676 | 0.1877 | 0.0511 | 0.1618 | 2.5989 | 0.1196 | None | 52.0000 |
| trace_full_obs_footpos.jsonl | `vanilla` | 200-224 | 0.0676 | 0.1887 | 0.0531 | 0.1619 | 2.4257 | 0.1114 | None | 44.0000 |
| trace_full_obs_footpos.jsonl | `vanilla` | 125-149 | 0.0674 | 0.1876 | 0.0517 | 0.1620 | 2.4783 | 0.1071 | None | 48.0000 |
| trace_full_obs_footpos.jsonl | `vanilla` | 195-219 | 0.0673 | 0.1887 | 0.0531 | 0.1619 | 2.6038 | 0.1182 | None | 40.0000 |
| trace_full_obs_footpos.jsonl | `vanilla` | 185-209 | 0.0673 | 0.1956 | 0.0509 | 0.1615 | 2.3758 | 0.1144 | None | 44.0000 |
| trace_full_obs_footpos.jsonl | `vanilla` | 140-164 | 0.0670 | 0.1714 | 0.0538 | 0.1615 | 2.5885 | 0.1120 | None | 44.0000 |
| trace_full_obs_footpos.jsonl | `vanilla` | 0-24 | 0.0831 | 0.1516 | 0.0802 | 0.1506 | 3.3980 | 0.1271 | None | 76.0000 |
| trace_full_obs_footpos.jsonl | `vanilla` | 5-29 | 0.0561 | 0.1516 | 0.0800 | 0.1617 | 2.4211 | 0.0921 | None | 84.0000 |
| trace_full_obs_footpos.jsonl | `vanilla` | 25-49 | 0.0744 | 0.1659 | 0.0478 | 0.1589 | 2.8157 | 0.1209 | None | 56.0000 |
| trace_full_obs_footpos.jsonl | `vanilla` | 190-214 | 0.0720 | 0.1887 | 0.0571 | 0.1620 | 2.3657 | 0.1176 | None | 52.0000 |
| trace_full_obs_footpos.jsonl | `vanilla` | 185-209 | 0.0706 | 0.1887 | 0.0504 | 0.1620 | 2.3524 | 0.1137 | None | 44.0000 |
| trace_full_obs_footpos.jsonl | `vanilla` | 30-54 | 0.0699 | 0.1526 | 0.0543 | 0.1608 | 2.7049 | 0.1195 | None | 52.0000 |
| trace_full_obs_footpos.jsonl | `vanilla` | 195-219 | 0.0698 | 0.1917 | 0.0571 | 0.1614 | 2.4581 | 0.1203 | None | 44.0000 |
| trace_full_obs_footpos.jsonl | `vanilla` | 20-44 | 0.0686 | 0.1659 | 0.0450 | 0.1589 | 3.0257 | 0.1262 | None | 40.0000 |
| trace_full_obs_footpos.jsonl | `vanilla` | 80-104 | 0.0683 | 0.1936 | 0.0484 | 0.1618 | 2.4914 | 0.1145 | None | 52.0000 |
| trace_full_obs_footpos.jsonl | `vanilla` | 180-204 | 0.0683 | 0.1865 | 0.0495 | 0.1620 | 2.6104 | 0.1143 | None | 48.0000 |
| trace_full_obs_footpos.jsonl | `vanilla` | 115-139 | 0.0668 | 0.1999 | 0.0521 | 0.1611 | 2.3773 | 0.1145 | None | 44.0000 |
| trace_full_obs_footpos.jsonl | `vanilla` | 70-94 | 0.0668 | 0.1945 | 0.0482 | 0.1618 | 2.7084 | 0.1183 | None | 52.0000 |
| trace_full_obs_footpos.jsonl | `vanilla` | 205-229 | 0.0668 | 0.1917 | 0.0571 | 0.1614 | 2.4693 | 0.1189 | None | 52.0000 |
| trace_full_obs_footpos.jsonl | `vanilla` | 60-84 | 0.0667 | 0.1945 | 0.0485 | 0.1618 | 2.7177 | 0.1192 | None | 44.0000 |
| trace_full_obs_footpos.jsonl | `vanilla` | 110-134 | 0.0666 | 0.1884 | 0.0521 | 0.1620 | 2.2850 | 0.1049 | None | 48.0000 |
| trace_full_obs_footpos.jsonl | `vanilla` | 55-79 | 0.0664 | 0.1971 | 0.0485 | 0.1606 | 2.5542 | 0.1160 | None | 52.0000 |
| trace_full_obs_footpos.jsonl | `vanilla` | 175-199 | 0.0664 | 0.1904 | 0.0470 | 0.1620 | 2.7023 | 0.1182 | None | 52.0000 |
| trace_full_obs_footpos.jsonl | `vanilla` | 85-109 | 0.0663 | 0.1594 | 0.0534 | 0.1619 | 2.5021 | 0.1109 | None | 48.0000 |
| trace_full_obs_footpos.jsonl | `vanilla` | 200-224 | 0.0660 | 0.1917 | 0.0571 | 0.1614 | 2.4693 | 0.1178 | None | 48.0000 |
| trace_full_obs_footpos.jsonl | `vanilla` | 90-114 | 0.0660 | 0.1881 | 0.0534 | 0.1619 | 2.3432 | 0.1126 | None | 40.0000 |
| trace_full_obs_footpos.jsonl | `vanilla` | 105-129 | 0.0659 | 0.1884 | 0.0530 | 0.1619 | 2.2850 | 0.1117 | None | 44.0000 |
| trace_full_obs_footpos.jsonl | `vanilla` | 160-184 | 0.0734 | 0.1899 | 0.0494 | 0.1619 | 2.4946 | 0.1134 | None | 48.0000 |
| trace_full_obs_footpos.jsonl | `vanilla` | 110-134 | 0.0728 | 0.1882 | 0.0555 | 0.1620 | 2.4539 | 0.1119 | None | 52.0000 |
| trace_full_obs_footpos.jsonl | `vanilla` | 105-129 | 0.0722 | 0.1882 | 0.0496 | 0.1620 | 2.3637 | 0.1131 | None | 48.0000 |
| trace_full_obs_footpos.jsonl | `vanilla` | 165-189 | 0.0715 | 0.1707 | 0.0550 | 0.1623 | 2.4946 | 0.1121 | None | 48.0000 |
| trace_full_obs_footpos.jsonl | `vanilla` | 115-139 | 0.0714 | 0.1878 | 0.0555 | 0.1623 | 2.5185 | 0.1172 | None | 40.0000 |
| trace_full_obs_footpos.jsonl | `vanilla` | 60-84 | 0.0699 | 0.1989 | 0.0520 | 0.1623 | 2.7254 | 0.1189 | None | 40.0000 |
| trace_full_obs_footpos.jsonl | `vanilla` | 25-49 | 0.0699 | 0.1744 | 0.0570 | 0.1580 | 2.5772 | 0.1188 | None | 60.0000 |
| trace_full_obs_footpos.jsonl | `vanilla` | 30-54 | 0.0695 | 0.1497 | 0.0579 | 0.1607 | 2.4756 | 0.1138 | None | 56.0000 |
| trace_full_obs_footpos.jsonl | `vanilla` | 170-194 | 0.0692 | 0.1807 | 0.0550 | 0.1620 | 2.4926 | 0.1135 | None | 40.0000 |
| trace_full_obs_footpos.jsonl | `vanilla` | 155-179 | 0.0685 | 0.1899 | 0.0475 | 0.1619 | 2.5232 | 0.1162 | None | 40.0000 |
| trace_full_obs_footpos.jsonl | `vanilla` | 70-94 | 0.0685 | 0.1989 | 0.0521 | 0.1623 | 2.6813 | 0.1156 | None | 48.0000 |
| trace_full_obs_footpos.jsonl | `vanilla` | 180-204 | 0.0684 | 0.1775 | 0.0550 | 0.1620 | 2.5910 | 0.1140 | None | 44.0000 |
| trace_full_obs_footpos.jsonl | `vanilla` | 195-219 | 0.0679 | 0.1939 | 0.0529 | 0.1620 | 2.5570 | 0.1149 | None | 40.0000 |
| trace_full_obs_footpos.jsonl | `vanilla` | 65-89 | 0.0679 | 0.1989 | 0.0520 | 0.1623 | 2.6333 | 0.1125 | None | 44.0000 |
| trace_full_obs_footpos.jsonl | `vanilla` | 100-124 | 0.0678 | 0.1820 | 0.0491 | 0.1620 | 2.5854 | 0.1171 | None | 44.0000 |
| trace_full_obs_footpos.jsonl | `vanilla` | 190-214 | 0.0674 | 0.1940 | 0.0529 | 0.1620 | 2.3725 | 0.1146 | None | 48.0000 |
| trace_full_obs_footpos.jsonl | `vanilla` | 75-99 | 0.0671 | 0.1849 | 0.0521 | 0.1623 | 2.6034 | 0.1191 | None | 40.0000 |
| trace_full_obs_footpos.jsonl | `vanilla` | 15-39 | 0.0668 | 0.1694 | 0.0570 | 0.1580 | 2.6426 | 0.1239 | None | 64.0000 |
| trace_full_obs_footpos.jsonl | `vanilla` | 140-164 | 0.0682 | 0.1779 | 0.0513 | 0.1621 | 2.7307 | 0.1138 | None | 44.0000 |
| trace_full_obs_footpos.jsonl | `vanilla` | 180-204 | 0.0678 | 0.1782 | 0.0532 | 0.1621 | 2.6102 | 0.1128 | None | 44.0000 |
| trace_full_obs_footpos.jsonl | `vanilla` | 170-194 | 0.0671 | 0.1943 | 0.0532 | 0.1621 | 2.4995 | 0.1136 | None | 40.0000 |
| trace_full_obs_footpos.jsonl | `vanilla` | 225-249 | 0.0671 | 0.1861 | 0.0524 | 0.1620 | 2.4114 | 0.1118 | None | 40.0000 |
| trace_full_obs_footpos.jsonl | `vanilla` | 165-189 | 0.0668 | 0.1914 | 0.0532 | 0.1625 | 2.4132 | 0.1099 | None | 48.0000 |
| trace_full_obs_footpos.jsonl | `vanilla` | 145-169 | 0.0667 | 0.1865 | 0.0513 | 0.1621 | 2.6209 | 0.1138 | None | 40.0000 |
| trace_full_obs_footpos.jsonl | `vanilla` | 160-184 | 0.0665 | 0.1950 | 0.0501 | 0.1621 | 2.5717 | 0.1129 | None | 48.0000 |
| trace_full_obs_footpos.jsonl | `vanilla` | 35-59 | 0.0661 | 0.1861 | 0.0541 | 0.1620 | 2.3223 | 0.1121 | None | 40.0000 |
| trace_full_obs_footpos.jsonl | `vanilla` | 175-199 | 0.0660 | 0.1943 | 0.0532 | 0.1621 | 2.6102 | 0.1137 | None | 48.0000 |
| trace_full_obs_footpos.jsonl | `vanilla` | 150-174 | 0.0658 | 0.1865 | 0.0513 | 0.1621 | 2.6438 | 0.1171 | None | 48.0000 |
| trace_full_obs_footpos.jsonl | `vanilla` | 220-244 | 0.0657 | 0.1604 | 0.0524 | 0.1620 | 2.5490 | 0.1097 | None | 48.0000 |
| trace_full_obs_footpos.jsonl | `vanilla` | 155-179 | 0.0657 | 0.1950 | 0.0513 | 0.1621 | 2.6278 | 0.1171 | None | 40.0000 |
| trace_full_obs_footpos.jsonl | `vanilla` | 45-69 | 0.0649 | 0.1860 | 0.0541 | 0.1620 | 2.4920 | 0.1119 | None | 44.0000 |

## Top Review-Only Motion Hints

| source | mode | ticks | vx | reasons |
|---|---|---|---:|---|
| trace_full_obs_footpos.jsonl | `vanilla` | 70-94 | 0.0716 | `high_lateral_velocity` |
| trace_full_obs_footpos.jsonl | `vanilla` | 60-84 | 0.0704 | `high_lateral_velocity` |
| trace_full_obs_footpos.jsonl | `vanilla` | 40-64 | 0.0715 | `high_lateral_velocity` |
| trace_full_obs_footpos.jsonl | `vanilla` | 35-59 | 0.0715 | `high_lateral_velocity` |
| trace_full_obs_footpos.jsonl | `vanilla` | 115-139 | 0.0729 | `high_lateral_velocity` |
| trace_full_obs_footpos.jsonl | `vanilla` | 120-144 | 0.0711 | `high_lateral_velocity` |
| trace_full_obs_footpos.jsonl | `vanilla` | 135-159 | 0.0710 | `high_lateral_velocity` |
| trace_full_obs_footpos.jsonl | `vanilla` | 160-184 | 0.0611 | `high_lateral_velocity` |
| trace_full_obs_footpos.jsonl | `vanilla` | 155-179 | 0.0577 | `high_lateral_velocity` |
| trace_full_obs_footpos.jsonl | `vanilla` | 145-169 | 0.0700 | `high_lateral_velocity` |
| trace_full_obs_footpos.jsonl | `vanilla` | 215-239 | 0.0747 | `high_lateral_velocity` |
| trace_full_obs_footpos.jsonl | `vanilla` | 210-234 | 0.0745 | `high_lateral_velocity` |
| trace_full_obs_footpos.jsonl | `vanilla` | 190-214 | 0.0782 | `high_lateral_velocity` |
| trace_full_obs_footpos.jsonl | `vanilla` | 195-219 | 0.0770 | `high_lateral_velocity` |
| trace_full_obs_footpos.jsonl | `vanilla` | 215-239 | 0.0765 | `high_lateral_velocity` |

## Interpretation

- Treat `PASS_CURATED_SEED_WINDOW` rows as possible seed material, not as a complete dataset.
- Treat `REVIEW_MOTION_HINT_ONLY` rows as qualitative motion hints until the failing reason is addressed.
- Do not launch BC/PPO from these windows unless the curated count and diversity are sufficient.
