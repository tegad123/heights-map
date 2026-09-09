# Market status reconciliation — 2026-09-09

Phase 4 deferred for construction-coverage review. Supply calculation unchanged. All six files contain **119 rows**, not 159.

Original List Price is not current asking price. A missing market record is not proof of unsold/unlisted status. Paired phases belong to the project.

## Input counts and sold union
```json
{
  "files": [
    {
      "file": "heightsactivesinglelots909.csv",
      "sha256": "d3e034cfcc7de0db68f51a6a4867aaa882c8cf7063864b5620ca5e077292c864",
      "read": 35,
      "accepted": 35,
      "classification_matches": 35,
      "excluded": {}
    },
    {
      "file": "heightsactivesplitlots909.csv",
      "sha256": "73441999e98007023c8a8771f0c4b7fb7175a6a1d5922002a969085944a6599c",
      "read": 24,
      "accepted": 24,
      "classification_matches": 24,
      "excluded": {}
    },
    {
      "file": "heightspendingsinglelots909.csv",
      "sha256": "1ce3cf1db5e4ec48e5ced570ca8d2a085c85f938300baba5f306d4291ef8c8e2",
      "read": 4,
      "accepted": 4,
      "classification_matches": 4,
      "excluded": {}
    },
    {
      "file": "heightspendingsplitlots909.csv",
      "sha256": "40102e94f7bc9077c8866f41d3ba7574b75acfcd0e9b39dc4e41a0103cf7784e",
      "read": 8,
      "accepted": 8,
      "classification_matches": 8,
      "excluded": {}
    },
    {
      "file": "heightssoldsinglelotslast180days.csv",
      "sha256": "3379d929904fc10f7dea02981e01212be04f7337351cba344f84a070704d7c9c",
      "read": 19,
      "accepted": 19,
      "classification_matches": 19,
      "excluded": {}
    },
    {
      "file": "heightssoldsplitlotslast180days.csv",
      "sha256": "c1edd04a38c4ba962528a338d33eec0ad6412840f1df2cb9e622723901880509",
      "read": 29,
      "accepted": 29,
      "classification_matches": 29,
      "excluded": {}
    }
  ],
  "sold_reconciliation": {
    "before": 764,
    "after": 767,
    "additions_since_baseline": [
      "s89124616",
      "s88173016",
      "s26903565"
    ],
    "overlap_30_vs_180": [
      "10396812",
      "35621139",
      "72560168",
      "85478626",
      "88173016"
    ],
    "all_prior_ids_preserved": true
  },
  "match_rate": {
    "total": 119,
    "unique_pin": 84,
    "with_phase": 51
  },
  "active_delta": [
    {
      "address": "602 Jewett Street Unit#B",
      "MLS": "56131613",
      "disposition": "unconfirmed; absence does not establish off-market",
      "evidence_mls": []
    },
    {
      "address": "1822 W 23rd Street",
      "MLS": "73224522",
      "disposition": "unconfirmed; absence does not establish off-market",
      "evidence_mls": []
    }
  ],
  "complete_counts": {
    "no market record": 30,
    "pending": 5,
    "sold": 4,
    "active": 13
  },
  "supply_impact": {
    "current": 144,
    "A_total": 4,
    "A_current_supply": 0,
    "C_total": 5,
    "C_current_supply": 0,
    "B_added": 13,
    "D_added": 30,
    "requested_result": 187,
    "additional_known_unavailable_members": 3,
    "availability_scenario_including_building_exclusions": 184,
    "pending_or_sold_under_construction_in_current_supply": [
      {
        "address": "314 W 21st St, Houston, Tx 77008",
        "MLS": "32141788",
        "construction_phase": "interior",
        "current_market_status": "pending",
        "prior_stored_tag": [
          "interior"
        ],
        "conflict_class": [],
        "pin": "2131186599",
        "member": "2131186599",
        "phase_scope": "property",
        "historical_sales": [],
        "in_current_supply": true
      },
      {
        "address": "1113 Voight Street",
        "MLS": "40388055",
        "construction_phase": "mep_finals",
        "current_market_status": "pending",
        "prior_stored_tag": [
          "mep_finals",
          "active_single",
          "listed"
        ],
        "conflict_class": [
          "F"
        ],
        "pin": "act_1113-voight",
        "member": "act_1113-voight",
        "phase_scope": "property",
        "historical_sales": [],
        "in_current_supply": true
      },
      {
        "address": "807 W 22nd St, Houston, TX 77008",
        "MLS": "44304073",
        "construction_phase": "interior",
        "current_market_status": "pending",
        "prior_stored_tag": [],
        "conflict_class": [],
        "pin": "act_805-w-22nd-street",
        "member": "pmt_807-w-22nd-st-77008",
        "phase_scope": "paired project",
        "historical_sales": [],
        "in_current_supply": true
      }
    ],
    "caveat": "D means no matching evidence in finite exports/archive, NOT verified unlisted or unsold. B+D is a requested scenario, not confirmed availability. Paired construction evidence is not per-unit certification."
  }
}

```
## All input rows
| address | MLS | construction_phase | current_market_status | prior_stored_tag | conflict_class |
|---|---|---|---|---|---|
| 845-A West 23rd Street | 17612330 | foundation | active | ["foundation"] | ["H"] |
| 615 Wendel Street | 31557430 | no evidenced phase | active | ["active_single", "listed", "market"] | ["G"] |
| 613 Wendel Street | 6296220 | no evidenced phase | active | ["active_single", "listed", "market"] | ["G"] |
| 1002 E 25th Street | 72762085 | no evidenced phase | active | ["active_single", "listed", "market"] | ["G"] |
| 902 E 25TH Street | 32496070 | complete | active | ["active_single", "complete", "listed"] | ["B"] |
| 830 E 27th Street Street | 94349442 | no evidenced phase | active | ["active_single", "listed", "market"] | ["G"] |
| 920 E 25TH Street | 35798306 | interior | active | ["active_single", "interior", "listed"] | ["H"] |
| 122 E 4th Street | 90552057 | complete | active | ["active_split", "complete", "listed"] | ["B"] |
| 834 WAVERLY Street | 46031576 | no evidenced phase | active | ["active_single", "listed", "market"] | ["G"] |
| 2011 Singleton Street | 5383346 | mep_finals | active | ["active_single", "listed", "mep_finals"] | ["H"] |
| 1502 W 21st Street | 22973800 | no evidenced phase | active | ["active_single", "listed", "market"] | ["G"] |
| 705 Walton Street | 6584972 | no evidenced phase | active | ["active_single", "listed", "market"] | ["G"] |
| 3115 Beauchamp Street | 54037481 | no evidenced phase | active | ["active_single", "listed", "market"] | ["G"] |
| 830 WAVERLY Street | 97695610 | no evidenced phase | active | ["active_single", "listed", "market"] | ["G"] |
| 2603 JULIAN Street | 87208794 | mep_roughs | active | ["active_single", "listed", "mep_roughs"] | ["H"] |
| 1138 Fugate Street | 64823156 | mep_finals | active | ["mep_finals"] | ["H"] |
| 603 E 23rd Street | 70087101 | interior | active | ["active_single", "interior", "listed"] | ["H"] |
| 623 E 13th Street | 89411837 | mep_finals | active | ["active_single", "listed", "mep_finals"] | ["H"] |
| 614 Ridge Street | 90107924 | no evidenced phase | active | ["active_single", "listed", "market"] | ["G"] |
| 1111 E 27th Street | 26389093 | untracked | active | [] | ["G"] |
| 2218 Gostick Street | 87300082 | no evidenced phase | active | ["active_single", "listed", "market"] | ["G"] |
| 609 E 25th Street | 53672595 | complete | active | ["active_single", "complete", "listed"] | ["B"] |
| 212 E 24th Street | 29120139 | complete | active | ["active_single", "complete", "listed"] | ["B"] |
| 906 Bayland Avenue | 56747960 | mep_finals | active | ["mep_finals"] | ["H"] |
| 715 Merrill Street | 88557637 | complete | active | ["active_single", "complete", "listed"] | ["B"] |
| 2015 Harvard Street | 7670973 | no evidenced phase | active | ["active_single", "listed", "market"] | ["G"] |
| 410 Merrill Street | 31444523 | interior | active | ["interior", "needs_clarification"] | ["H"] |
| 2924 Watson Street | 70723638 | interior | active | ["active_single", "interior", "listed"] | ["H"] |
| 735 E 8TH 1/2 Street | 5069786 | interior | active | ["active_single", "interior", "listed"] | ["H"] |
| 731 E 8TH 1/2 Street | 40836939 | interior | active | ["active_single", "interior", "listed"] | ["H"] |
| 248 W 22nd Street | 89221155 | interior | active | ["active_single", "interior", "listed"] | ["H"] |
| 2434 White Oak Drive | 9001753 | framing | active | ["active_single", "framing", "listed"] | ["H"] |
| 1140 Waverly Street | 57009282 | interior | active | ["active_single", "interior", "listed"] | ["H"] |
| 2436 White Oak | 68235642 | framing | active | ["active_single", "framing", "listed"] | ["H"] |
| 1002 E 6TH 1/2 Street | 93562410 | mep_finals | active | ["active_single", "listed", "mep_finals"] | ["H"] |
| 1303 Cordell Street Unit#B | 64036585 | complete | active | ["active_split", "complete", "listed"] | ["B"] |
| 1032 W 17th Street Unit#A | 7485788 | no evidenced phase | active | ["active_split", "listed", "market"] | ["G"] |
| 409 Walton Street Unit#B | 54747421 | complete | active | [] | ["B"] |
| 1122 E 27TH ST Unit#A | 71690573 | no evidenced phase | active | [] | ["G"] |
| 1520 W 21st St Unit#A | 95958213 | complete | active | [] | ["B"] |
| 1218 Prince Street | 57925491 | exterior | active | ["active_split", "exterior", "listed"] | ["H"] |
| 741 W 21st Street Unit#A | 7364673 | no evidenced phase | active | ["active_split", "listed", "market"] | ["G"] |
| 1227 Prince Street | 22766797 | no evidenced phase | active | [] | ["G"] |
| 1120 E 26th Street | 29146166 | interior | active | ["active_split", "interior", "listed"] | ["H"] |
| 835 W 25th Street | 87747647 | complete | active | ["active_split", "complete", "listed"] | ["B"] |
| 805 W 22nd Street | 4182331 | interior | active | ["active_split", "interior", "listed"] | ["H"] |
| 1122 Robbie Street | 89794015 | mep_finals | active | [] | ["H"] |
| 1322 Lawrence Street | 13912427 | complete | active | ["active_split", "complete", "listed"] | ["B"] |
| 1012 E 26TH Street | 54722254 | insulation | active | [] | ["H"] |
| 711 E 26TH Street | 36627624 | interior | active | [] | ["H"] |
| 318 W 21st Street | 69573145 | interior | active | ["active_split", "interior", "listed"] | ["H"] |
| 609 W 27th Street | 98658584 | complete | active | ["active_split", "complete", "listed"] | ["B"] |
| 112 E 27th Street | 34333707 | complete | active | [] | ["B"] |
| 611 E 25th Street Unit#B | 57910089 | no evidenced phase | active | [] | ["G"] |
| 407 E 27TH Street | 10210884 | mep_finals | active | ["active_split", "listed", "mep_finals"] | ["H"] |
| 710 Waverly Street Unit#D | 32352560 | no evidenced phase | active | ["active_split", "listed", "market"] | ["G"] |
| 335 Harvard Street | 65070979 | complete | active | ["active_split", "complete", "listed"] | ["B"] |
| 1504 W 21st Street | 14206939 | no evidenced phase | active | [] | ["G"] |
| 312 w 9th St | 16999317 | interior | active | [] | ["H"] |
| 1315 Waverly Street | 62006938 | no evidenced phase | pending | ["active_single", "listed", "market"] | ["F", "G"] |
| 1116 Highland Street | 42468659 | complete | pending | ["active_single", "complete", "listed", "pending"] | ["C", "F"] |
| 1113 Voight Street | 40388055 | mep_finals | pending | ["active_single", "listed", "mep_finals"] | ["F"] |
| 1126 E 7th 1/2 Street | 95336494 | complete | pending | ["complete", "listed", "off_market_single"] | ["C", "F"] |
| 1208 E 26th Street Unit#A | 58591599 | complete | pending | ["active_split", "complete", "listed", "pending"] | ["C", "F"] |
| 807 W 22nd Street | 44304073 | interior | pending | [] | [] |
| 1434 Alexander Street | 61282363 | complete | pending | [] | ["C"] |
| 816 W 17TH Street | 81354398 | no evidenced phase | pending | [] | ["G"] |
| 814 W 17TH Street | 62144090 | no evidenced phase | pending | ["pending"] | ["G"] |
| 827 W 16th Street Unit#A | 89555500 | mep_finals | pending | ["listed", "mep_finals", "off_market_split"] | ["F"] |
| 314 W 21st Street | 32141788 | interior | pending | ["interior"] | [] |
| 116 E 23RD Street | 81689864 | complete | pending | [] | ["C"] |
| 1737 Tabor Street | 89124616 | untracked | sold | [] | ["G"] |
| 1207 Tabor Street | 85478626 | no evidenced phase | sold | ["active_single", "listed", "market", "pending"] | ["F", "G"] |
| 1023 E 23rd Street | 50869013 | untracked | sold | [] | ["G"] |
| 903 Tabor Street | 93127419 | untracked | sold | [] | ["G"] |
| 107 E 24th Street | 95407673 | no evidenced phase | sold | ["off_market_single"] | ["F", "G"] |
| 1520 Nicholson Street | 33839156 | no evidenced phase | sold | ["listed", "off_market_single"] | ["F", "G"] |
| 1524 Nicholson St | 64831168 | untracked | sold | [] | ["G"] |
| 1106 Robbie Street | 96094299 | untracked | sold | [] | ["G"] |
| 710 E 18th Street | 71056150 | no evidenced phase | sold | ["off_market_single", "pending"] | ["F", "G"] |
| 826 Ralfallen Street | 88173016 | complete | sold | ["complete", "listed", "pending"] | ["A", "F"] |
| 709 Ridge Street | 26903565 | no evidenced phase | sold | ["off_market_single"] | ["F", "G"] |
| 709 E 17th Street | 72560168 | complete | sold | ["active_single", "complete", "listed", "pending"] | ["A", "F"] |
| 1023 Euclid Street | 35621139 | no evidenced phase | sold | ["listed", "pending"] | ["F", "G"] |
| 402 Columbia Street | 33729025 | untracked | sold | [] | ["G"] |
| 406 Columbia Street | 78950517 | untracked | sold | [] | ["G"] |
| 1119 E 7th 1/2 Street | 90671798 | untracked | sold | [] | ["G"] |
| 726 E 7th Street | 16593438 | untracked | sold | [] | ["G"] |
| 2612 Greenleaf Street | 65984026 | untracked | sold | [] | ["G"] |
| 1001 E 7th 1/2 Street | 19950202 | untracked | sold | [] | ["G"] |
| 1316 Heslep Street | 38995142 | untracked | sold | [] | ["G"] |
| 602 Jewett Street Unit#A | 94906411 | untracked | sold | [] | ["G"] |
| 1438-A Dian Street | 66717038 | untracked | sold | [] | ["G"] |
| 1208 E 26th Street Unit#B | 8458741 | untracked | sold | [] | ["G"] |
| 1303 Cordell Street Unit#A | 9530397 | untracked | sold | [] | ["G"] |
| 1121 E 24th Street | 13147368 | untracked | sold | [] | ["G"] |
| 1125 E 24th Street | 61559810 | untracked | sold | [] | ["G"] |
| 310 E 28th St | 78621450 | untracked | sold | [] | ["G"] |
| 224 E 27th Street | 79405032 | untracked | sold | [] | ["G"] |
| 1524 W 21st St | 76530080 | untracked | sold | [] | ["G"] |
| 1122 E 27TH ST Unit#B | 92767147 | no evidenced phase | sold | ["listed", "off_market_split"] | ["F", "G"] |
| 1229 Prince Street | 97105255 | no evidenced phase | sold | ["off_market_split"] | ["F", "G"] |
| 406 E 28th Street | 77501317 | untracked | sold | [] | ["G"] |
| 1436 Alexander St | 5279771 | untracked | sold | [] | ["G"] |
| 404 E 28th Street | 87693150 | untracked | sold | [] | ["G"] |
| 1321 Alexander Street | 10970361 | untracked | sold | [] | ["G"] |
| 1516 Dorothy Street Unit#A | 12794628 | untracked | sold | [] | ["G"] |
| 1516 Dorothy Street Unit#C | 24145604 | untracked | sold | [] | ["G"] |
| 1324 Lawrence Street | 10396812 | complete | sold | [] | ["A"] |
| 1326 Lawrence Street | 16373769 | no evidenced phase | sold | ["off_market_split", "pending"] | ["F", "G"] |
| 827 W 16th Street Unit#B | 42479147 | untracked | sold | [] | ["G"] |
| 525 W 26th Street | 88804104 | untracked | sold | [] | ["G"] |
| 527 W 26th Street | 10589101 | untracked | sold | [] | ["G"] |
| 2715 BEAUCHAMP Street | 90312385 | untracked | sold | [] | ["G"] |
| 611 E 25th Street Unit#A | 30142567 | no evidenced phase | sold | ["pending"] | ["F", "G"] |
| 2713 BEAUCHAMP Street | 60919011 | untracked | sold | [] | ["G"] |
| 815 Lawrence Street Unit#A | 93385395 | no evidenced phase | sold | ["off_market_split"] | ["F", "G"] |
| 815B Lawrence Street | 69395685 | untracked | sold | [] | ["G"] |
| 710 Waverly Street Unit#E | 94092178 | untracked | sold | [] | ["G"] |

## A. Complete but sold — 4

- {"address": "709 E 17th St, Houston, Tx 77008", "MLS": "72560168", "construction_phase": "complete", "current_market_status": "sold", "prior_stored_tag": ["complete", "pending", "active_single", "listed"], "conflict_class": ["A", "F"], "pin": "2131432164", "member": "2131432164", "phase_scope": "property", "historical_sales": [{"MLS": "72560168", "close_date": "2026-08-24", "close_price": 1755000.0, "year_built": 2026.0, "evidence_scope": "new-construction closing"}], "in_current_supply": false}
- {"address": "2013 Sheldon St A, Houston, TX 77008", "MLS": "86833589", "construction_phase": "complete", "current_market_status": "sold", "prior_stored_tag": ["complete"], "conflict_class": ["A"], "pin": "pmt_2013-sheldon-st-a-77008", "member": "pmt_2013-sheldon-st-a-77008", "phase_scope": "paired project", "historical_sales": [{"MLS": "86833589", "close_date": "2026-05-20", "close_price": 899900, "year_built": 2026, "evidence_scope": "new-construction closing"}], "in_current_supply": false}
- {"address": "1324 Lawrence Street", "MLS": "10396812", "construction_phase": "complete", "current_market_status": "sold", "prior_stored_tag": [], "conflict_class": ["A"], "pin": "act_1322-lawrence-street", "member": "act_1324-lawrence-street", "phase_scope": "paired project", "historical_sales": [{"MLS": "10396812", "close_date": "2026-08-28", "close_price": 869900.0, "year_built": 2026.0, "evidence_scope": "new-construction closing"}], "in_current_supply": false}
- {"address": "826 Ralfallen Street", "MLS": "88173016", "construction_phase": "complete", "current_market_status": "sold", "prior_stored_tag": ["complete", "pending", "listed"], "conflict_class": ["A", "F"], "pin": "act_826-ralfallen", "member": "act_826-ralfallen", "phase_scope": "property", "historical_sales": [{"MLS": "88173016", "close_date": "2026-08-26", "close_price": 1655000.0, "year_built": 2026.0, "evidence_scope": "new-construction closing"}], "in_current_supply": false}

## B. Complete but active — 13

- {"address": "1520 W 21st St Unit#A", "MLS": "95958213", "construction_phase": "complete", "current_market_status": "active", "prior_stored_tag": [], "conflict_class": ["B"], "pin": "act_1520-w-21st-st-unit-b", "member": "act_1520-w-21st-st-unit-a", "phase_scope": "paired project", "historical_sales": [], "in_current_supply": false}
- {"address": "112 E 27th Street", "MLS": "34333707", "construction_phase": "complete", "current_market_status": "active", "prior_stored_tag": [], "conflict_class": ["B"], "pin": "pmt_112-e-27th-st-a-77008", "member": "act_112-e-27th-street", "phase_scope": "paired project", "historical_sales": [], "in_current_supply": false}
- {"address": "1322 Lawrence Street", "MLS": "13912427", "construction_phase": "complete", "current_market_status": "active", "prior_stored_tag": ["complete", "active_split", "listed"], "conflict_class": ["B"], "pin": "act_1322-lawrence-street", "member": "act_1322-lawrence-street", "phase_scope": "paired project", "historical_sales": [], "in_current_supply": false}
- {"address": "409 Walton Street Unit#B", "MLS": "54747421", "construction_phase": "complete", "current_market_status": "active", "prior_stored_tag": [], "conflict_class": ["B"], "pin": "pmt_409-walton-st-a-77009", "member": "act_409-walton-street-unit-b", "phase_scope": "paired project", "historical_sales": [], "in_current_supply": false}
- {"address": "902 E 25TH Street", "MLS": "32496070", "construction_phase": "complete", "current_market_status": "active", "prior_stored_tag": ["complete", "active_single", "listed"], "conflict_class": ["B"], "pin": "act_902-e-25", "member": "act_902-e-25", "phase_scope": "property", "historical_sales": [], "in_current_supply": false}
- {"address": "122 E 4th Street", "MLS": "90552057", "construction_phase": "complete", "current_market_status": "active", "prior_stored_tag": ["complete", "active_split", "listed"], "conflict_class": ["B"], "pin": "act_122-e-4", "member": "act_122-e-4", "phase_scope": "property", "historical_sales": [], "in_current_supply": false}
- {"address": "609 E 25th Street", "MLS": "53672595", "construction_phase": "complete", "current_market_status": "active", "prior_stored_tag": ["complete", "active_single", "listed"], "conflict_class": ["B"], "pin": "act_609-e-25", "member": "act_609-e-25", "phase_scope": "property", "historical_sales": [], "in_current_supply": false}
- {"address": "212 E 24th Street", "MLS": "29120139", "construction_phase": "complete", "current_market_status": "active", "prior_stored_tag": ["complete", "active_single", "listed"], "conflict_class": ["B"], "pin": "act_212-e-24", "member": "act_212-e-24", "phase_scope": "property", "historical_sales": [], "in_current_supply": false}
- {"address": "715 Merrill Street", "MLS": "88557637", "construction_phase": "complete", "current_market_status": "active", "prior_stored_tag": ["complete", "active_single", "listed"], "conflict_class": ["B"], "pin": "act_715-merrill", "member": "act_715-merrill", "phase_scope": "property", "historical_sales": [], "in_current_supply": false}
- {"address": "1303 Cordell Street Unit#B", "MLS": "64036585", "construction_phase": "complete", "current_market_status": "active", "prior_stored_tag": ["complete", "active_split", "listed"], "conflict_class": ["B"], "pin": "act_1303-cordell-street-unit-b", "member": "act_1303-cordell-street-unit-b", "phase_scope": "property", "historical_sales": [], "in_current_supply": false}
- {"address": "835 W 25th Street", "MLS": "87747647", "construction_phase": "complete", "current_market_status": "active", "prior_stored_tag": ["complete", "active_split", "listed"], "conflict_class": ["B"], "pin": "act_835-w-25th-street", "member": "act_835-w-25th-street", "phase_scope": "paired project", "historical_sales": [], "in_current_supply": false}
- {"address": "609 W 27th Street", "MLS": "98658584", "construction_phase": "complete", "current_market_status": "active", "prior_stored_tag": ["complete", "active_split", "listed"], "conflict_class": ["B"], "pin": "act_609-w-27th-street", "member": "act_609-w-27th-street", "phase_scope": "paired project", "historical_sales": [], "in_current_supply": false}
- {"address": "335 Harvard Street", "MLS": "65070979", "construction_phase": "complete", "current_market_status": "active", "prior_stored_tag": ["complete", "active_split", "listed"], "conflict_class": ["B"], "pin": "act_335-harvard-street", "member": "act_335-harvard-street", "phase_scope": "property", "historical_sales": [], "in_current_supply": false}

## C. Complete but pending — 5

- {"address": "116 E 23RD Street", "MLS": "81689864", "construction_phase": "complete", "current_market_status": "pending", "prior_stored_tag": [], "conflict_class": ["C"], "pin": "2131144961", "member": "act_116-e-23rd-street", "phase_scope": "paired project", "historical_sales": [], "in_current_supply": false}
- {"address": "1434 Alexander Street", "MLS": "61282363", "construction_phase": "complete", "current_market_status": "pending", "prior_stored_tag": [], "conflict_class": ["C"], "pin": "pmt_1432-alexander-st-77008", "member": "act_1434-alexander-street", "phase_scope": "paired project", "historical_sales": [], "in_current_supply": false}
- {"address": "1116 Highland Street", "MLS": "42468659", "construction_phase": "complete", "current_market_status": "pending", "prior_stored_tag": ["complete", "pending", "active_single", "listed"], "conflict_class": ["C", "F"], "pin": "act_1116-highland", "member": "act_1116-highland", "phase_scope": "property", "historical_sales": [], "in_current_supply": false}
- {"address": "1126 E 7th 1/2 Street", "MLS": "95336494", "construction_phase": "complete", "current_market_status": "pending", "prior_stored_tag": ["complete", "off_market_single", "listed"], "conflict_class": ["C", "F"], "pin": "act_1126-e-7-12", "member": "act_1126-e-7-12", "phase_scope": "property", "historical_sales": [], "in_current_supply": false}
- {"address": "1208 E 26th Street Unit#A", "MLS": "58591599", "construction_phase": "complete", "current_market_status": "pending", "prior_stored_tag": ["complete", "pending", "active_split", "listed"], "conflict_class": ["C", "F"], "pin": "act_1208-e-26th-street-unit-a", "member": "act_1208-e-26th-street-unit-a", "phase_scope": "property", "historical_sales": [], "in_current_supply": false}

## D. Complete, no market record (availability unverified) — 30

- {"address": "118 E 23rd St, Houston, Tx 77008", "MLS": "", "construction_phase": "complete", "current_market_status": "no market record", "prior_stored_tag": ["complete"], "conflict_class": ["D"], "pin": "2131144961", "member": "2131144961", "phase_scope": "paired project", "historical_sales": [], "in_current_supply": false}
- {"address": "1520 W 21st St Unit#B", "MLS": "", "construction_phase": "complete", "current_market_status": "no market record", "prior_stored_tag": ["complete", "active_split", "listed"], "conflict_class": ["D"], "pin": "act_1520-w-21st-st-unit-b", "member": "act_1520-w-21st-st-unit-b", "phase_scope": "paired project", "historical_sales": [], "in_current_supply": false}
- {"address": "1623 Blount St, Houston, TX 77008", "MLS": "", "construction_phase": "complete", "current_market_status": "no market record", "prior_stored_tag": ["complete"], "conflict_class": ["D"], "pin": "pmt_1623-blount-st-77008", "member": "pmt_1623-blount-st-77008", "phase_scope": "property", "historical_sales": [], "in_current_supply": false}
- {"address": "1343 Nashua St, Houston, TX 77008", "MLS": "", "construction_phase": "complete", "current_market_status": "no market record", "prior_stored_tag": ["complete"], "conflict_class": ["D"], "pin": "pmt_1343-nashua-st-77008", "member": "pmt_1343-nashua-st-77008", "phase_scope": "property", "historical_sales": [], "in_current_supply": false}
- {"address": "2013 Sheldon St B, Houston, TX 77008", "MLS": "", "construction_phase": "complete", "current_market_status": "no market record", "prior_stored_tag": [], "conflict_class": ["D"], "pin": "pmt_2013-sheldon-st-a-77008", "member": "pmt_2013-sheldon-st-b-77008", "phase_scope": "paired project", "historical_sales": [], "in_current_supply": false}
- {"address": "737 W 21st St C, Houston, TX 77008", "MLS": "", "construction_phase": "complete", "current_market_status": "no market record", "prior_stored_tag": ["complete"], "conflict_class": ["D"], "pin": "pmt_737-w-21st-st-c-77008", "member": "pmt_737-w-21st-st-c-77008", "phase_scope": "property", "historical_sales": [], "in_current_supply": false}
- {"address": "737 W 21st St B, Houston, TX 77008", "MLS": "", "construction_phase": "complete", "current_market_status": "no market record", "prior_stored_tag": ["complete"], "conflict_class": ["D"], "pin": "pmt_737-w-21st-st-b-77008", "member": "pmt_737-w-21st-st-b-77008", "phase_scope": "property", "historical_sales": [], "in_current_supply": false}
- {"address": "737 W 21st St A, Houston, TX 77008", "MLS": "", "construction_phase": "complete", "current_market_status": "no market record", "prior_stored_tag": ["complete"], "conflict_class": ["D"], "pin": "pmt_737-w-21st-st-a-77008", "member": "pmt_737-w-21st-st-a-77008", "phase_scope": "property", "historical_sales": [], "in_current_supply": false}
- {"address": "737 W 21st St D, Houston, TX 77008", "MLS": "", "construction_phase": "complete", "current_market_status": "no market record", "prior_stored_tag": ["complete"], "conflict_class": ["D"], "pin": "pmt_737-w-21st-st-d-77008", "member": "pmt_737-w-21st-st-d-77008", "phase_scope": "property", "historical_sales": [], "in_current_supply": false}
- {"address": "729 W 21st St A, Houston, TX 77008", "MLS": "", "construction_phase": "complete", "current_market_status": "no market record", "prior_stored_tag": ["complete"], "conflict_class": ["D"], "pin": "pmt_729-w-21st-st-a-77008", "member": "pmt_729-w-21st-st-a-77008", "phase_scope": "property", "historical_sales": [], "in_current_supply": false}
- {"address": "723 W 21st St, Houston, TX 77008", "MLS": "", "construction_phase": "complete", "current_market_status": "no market record", "prior_stored_tag": ["complete"], "conflict_class": ["D"], "pin": "pmt_723-w-21st-st-77008", "member": "pmt_723-w-21st-st-77008", "phase_scope": "property", "historical_sales": [], "in_current_supply": false}
- {"address": "725 W 21st St, Houston, TX 77008", "MLS": "", "construction_phase": "complete", "current_market_status": "no market record", "prior_stored_tag": ["complete"], "conflict_class": ["D"], "pin": "pmt_725-w-21st-st-77008", "member": "pmt_725-w-21st-st-77008", "phase_scope": "property", "historical_sales": [], "in_current_supply": false}
- {"address": "729 W 21st St B, Houston, TX 77008", "MLS": "", "construction_phase": "complete", "current_market_status": "no market record", "prior_stored_tag": ["complete"], "conflict_class": ["D"], "pin": "pmt_729-w-21st-st-b-77008", "member": "pmt_729-w-21st-st-b-77008", "phase_scope": "property", "historical_sales": [], "in_current_supply": false}
- {"address": "1432 Alexander St, Houston, TX 77008", "MLS": "", "construction_phase": "complete", "current_market_status": "no market record", "prior_stored_tag": ["complete"], "conflict_class": ["D"], "pin": "pmt_1432-alexander-st-77008", "member": "pmt_1432-alexander-st-77008", "phase_scope": "paired project", "historical_sales": [], "in_current_supply": false}
- {"address": "112 E 27th St A, Houston, TX 77008", "MLS": "", "construction_phase": "complete", "current_market_status": "no market record", "prior_stored_tag": ["complete"], "conflict_class": ["D"], "pin": "pmt_112-e-27th-st-a-77008", "member": "pmt_112-e-27th-st-a-77008", "phase_scope": "paired project", "historical_sales": [], "in_current_supply": false}
- {"address": "729 W 21st St C, Houston, TX 77008", "MLS": "", "construction_phase": "complete", "current_market_status": "no market record", "prior_stored_tag": ["complete"], "conflict_class": ["D"], "pin": "pmt_729-w-21st-st-c-77008", "member": "pmt_729-w-21st-st-c-77008", "phase_scope": "property", "historical_sales": [], "in_current_supply": false}
- {"address": "715 E 12th St, Houston, TX 77008", "MLS": "", "construction_phase": "complete", "current_market_status": "no market record", "prior_stored_tag": ["complete", "active_single"], "conflict_class": ["D"], "pin": "pmt_715-e-12th-st-77008", "member": "pmt_715-e-12th-st-77008", "phase_scope": "property", "historical_sales": [], "in_current_supply": false}
- {"address": "2811 Ave, Houston, TX 77009", "MLS": "", "construction_phase": "complete", "current_market_status": "no market record", "prior_stored_tag": ["complete"], "conflict_class": ["D"], "pin": "pmt_2811-ave-77009", "member": "pmt_2811-ave-77009", "phase_scope": "property", "historical_sales": [], "in_current_supply": false}
- {"address": "1301 Tabor St, Houston, TX 77009", "MLS": "", "construction_phase": "complete", "current_market_status": "no market record", "prior_stored_tag": ["complete"], "conflict_class": ["D"], "pin": "pmt_1301-tabor-st-77009", "member": "pmt_1301-tabor-st-77009", "phase_scope": "property", "historical_sales": [], "in_current_supply": false}
- {"address": "1107 E 24th St, Houston, TX 77009", "MLS": "", "construction_phase": "complete", "current_market_status": "no market record", "prior_stored_tag": ["complete"], "conflict_class": ["D"], "pin": "pmt_1107-e-24th-st-77009", "member": "pmt_1107-e-24th-st-77009", "phase_scope": "paired project", "historical_sales": [], "in_current_supply": false}
- {"address": "1109 E 24th St, Houston, TX 77009", "MLS": "", "construction_phase": "complete", "current_market_status": "no market record", "prior_stored_tag": [], "conflict_class": ["D"], "pin": "pmt_1107-e-24th-st-77009", "member": "pmt_1109-e-24th-st-77009", "phase_scope": "paired project", "historical_sales": [], "in_current_supply": false}
- {"address": "826 E 27th St, Houston, TX 77009", "MLS": "", "construction_phase": "complete", "current_market_status": "no market record", "prior_stored_tag": ["complete"], "conflict_class": ["D"], "pin": "pmt_826-e-27th-st-77009", "member": "pmt_826-e-27th-st-77009", "phase_scope": "property", "historical_sales": [], "in_current_supply": false}
- {"address": "409 Walton St A, Houston, TX 77009", "MLS": "", "construction_phase": "complete", "current_market_status": "no market record", "prior_stored_tag": ["complete"], "conflict_class": ["D"], "pin": "pmt_409-walton-st-a-77009", "member": "pmt_409-walton-st-a-77009", "phase_scope": "paired project", "historical_sales": [], "in_current_supply": false}
- {"address": "931 Merrill St, Houston, TX 77009", "MLS": "", "construction_phase": "complete", "current_market_status": "no market record", "prior_stored_tag": ["complete"], "conflict_class": ["D"], "pin": "pmt_931-merrill-st-77009", "member": "pmt_931-merrill-st-77009", "phase_scope": "property", "historical_sales": [], "in_current_supply": false}
- {"address": "833 W 25th Street", "MLS": "", "construction_phase": "complete", "current_market_status": "no market record", "prior_stored_tag": [], "conflict_class": ["D"], "pin": "act_835-w-25th-street", "member": "act_833-w-25th-street", "phase_scope": "paired project", "historical_sales": [], "in_current_supply": false}
- {"address": "607 W 27th St, Houston, TX 77008", "MLS": "", "construction_phase": "complete", "current_market_status": "no market record", "prior_stored_tag": [], "conflict_class": ["D"], "pin": "act_609-w-27th-street", "member": "pmt_607-w-27th-st-77008", "phase_scope": "paired project", "historical_sales": [], "in_current_supply": false}
- {"address": "1602 Turnpike Rd, Houston, TX 77008", "MLS": "", "construction_phase": "complete", "current_market_status": "no market record", "prior_stored_tag": ["complete", "needs_clarification"], "conflict_class": ["D"], "pin": "pmt_1602-turnpike-rd-77008", "member": "pmt_1602-turnpike-rd-77008", "phase_scope": "property", "historical_sales": [], "in_current_supply": false}
- {"address": "Unidentified represented home 1 at 122 E 4th Street", "MLS": "", "construction_phase": "complete", "current_market_status": "no market record", "prior_stored_tag": [], "conflict_class": ["D"], "pin": "act_122-e-4", "member": null, "inferred_weight": true}
- {"address": "Unidentified represented home 1 at 1208 E 26th Street Unit#A", "MLS": "", "construction_phase": "complete", "current_market_status": "no market record", "prior_stored_tag": [], "conflict_class": ["D"], "pin": "act_1208-e-26th-street-unit-a", "member": null, "inferred_weight": true}
- {"address": "Unidentified represented home 1 at 335 Harvard Street", "MLS": "", "construction_phase": "complete", "current_market_status": "no market record", "prior_stored_tag": [], "conflict_class": ["D"], "pin": "act_335-harvard-street", "member": null, "inferred_weight": true}

## E. Under construction but sold — 0


## F. Stale tags — 19

- {"address": "709 E 17th St, Houston, Tx 77008", "MLS": "72560168", "construction_phase": "complete", "current_market_status": "sold", "prior_stored_tag": ["complete", "pending", "active_single", "listed"], "conflict_class": ["A", "F"], "pin": "2131432164", "member": "2131432164", "phase_scope": "property", "historical_sales": [{"MLS": "72560168", "close_date": "2026-08-24", "close_price": 1755000.0, "year_built": 2026.0, "evidence_scope": "new-construction closing"}], "in_current_supply": false}
- {"address": "1207 Tabor Street", "MLS": "85478626", "construction_phase": null, "current_market_status": "sold", "prior_stored_tag": ["market", "pending", "active_single", "listed"], "conflict_class": ["F"], "pin": "act_1207-tabor", "member": "act_1207-tabor", "phase_scope": "property", "historical_sales": [{"MLS": "85478626", "close_date": "2026-08-31", "close_price": 949000.0, "year_built": 2026.0, "evidence_scope": "new-construction closing"}], "in_current_supply": false}
- {"address": "1315 Waverly Street", "MLS": "62006938", "construction_phase": null, "current_market_status": "pending", "prior_stored_tag": ["market", "active_single", "listed"], "conflict_class": ["F"], "pin": "act_1315-waverly", "member": "act_1315-waverly", "phase_scope": "property", "historical_sales": [], "in_current_supply": false}
- {"address": "1520 Nicholson Street", "MLS": "33839156", "construction_phase": null, "current_market_status": "sold", "prior_stored_tag": ["off_market_single", "listed"], "conflict_class": ["F"], "pin": "act_1520-nicholson", "member": "act_1520-nicholson", "phase_scope": "property", "historical_sales": [{"MLS": "33839156", "close_date": "2026-08-01", "close_price": 1470000.0, "year_built": 2026.0, "evidence_scope": "new-construction closing"}], "in_current_supply": false}
- {"address": "826 Ralfallen Street", "MLS": "88173016", "construction_phase": "complete", "current_market_status": "sold", "prior_stored_tag": ["complete", "pending", "listed"], "conflict_class": ["A", "F"], "pin": "act_826-ralfallen", "member": "act_826-ralfallen", "phase_scope": "property", "historical_sales": [{"MLS": "88173016", "close_date": "2026-08-26", "close_price": 1655000.0, "year_built": 2026.0, "evidence_scope": "new-construction closing"}], "in_current_supply": false}
- {"address": "1023 Euclid Street", "MLS": "35621139", "construction_phase": null, "current_market_status": "sold", "prior_stored_tag": ["pending", "listed"], "conflict_class": ["F"], "pin": "act_1023-euclid", "member": "act_1023-euclid", "phase_scope": "property", "historical_sales": [{"MLS": "35621139", "close_date": "2026-09-04", "close_price": 1825000.0, "year_built": 2025.0, "evidence_scope": "new-construction closing"}], "in_current_supply": false}
- {"address": "1116 Highland Street", "MLS": "42468659", "construction_phase": "complete", "current_market_status": "pending", "prior_stored_tag": ["complete", "pending", "active_single", "listed"], "conflict_class": ["C", "F"], "pin": "act_1116-highland", "member": "act_1116-highland", "phase_scope": "property", "historical_sales": [], "in_current_supply": false}
- {"address": "1113 Voight Street", "MLS": "40388055", "construction_phase": "mep_finals", "current_market_status": "pending", "prior_stored_tag": ["mep_finals", "active_single", "listed"], "conflict_class": ["F"], "pin": "act_1113-voight", "member": "act_1113-voight", "phase_scope": "property", "historical_sales": [], "in_current_supply": true}
- {"address": "1126 E 7th 1/2 Street", "MLS": "95336494", "construction_phase": "complete", "current_market_status": "pending", "prior_stored_tag": ["complete", "off_market_single", "listed"], "conflict_class": ["C", "F"], "pin": "act_1126-e-7-12", "member": "act_1126-e-7-12", "phase_scope": "property", "historical_sales": [], "in_current_supply": false}
- {"address": "107 E 24th Street", "MLS": "95407673", "construction_phase": null, "current_market_status": "sold", "prior_stored_tag": ["off_market_single"], "conflict_class": ["F"], "pin": "act_107-e-24", "member": "act_107-e-24", "phase_scope": "property", "historical_sales": [{"MLS": "95407673", "close_date": "2026-07-20", "close_price": 1350000.0, "year_built": 2026.0, "evidence_scope": "new-construction closing"}], "in_current_supply": false}
- {"address": "710 E 18th Street", "MLS": "71056150", "construction_phase": null, "current_market_status": "sold", "prior_stored_tag": ["pending", "off_market_single"], "conflict_class": ["F"], "pin": "act_710-e-18", "member": "act_710-e-18", "phase_scope": "property", "historical_sales": [{"MLS": "71056150", "close_date": "2026-07-27", "close_price": 1580000.0, "year_built": 2025.0, "evidence_scope": "new-construction closing"}], "in_current_supply": false}
- {"address": "709 Ridge Street", "MLS": "26903565", "construction_phase": null, "current_market_status": "sold", "prior_stored_tag": ["off_market_single"], "conflict_class": ["F"], "pin": "act_709-ridge", "member": "act_709-ridge", "phase_scope": "property", "historical_sales": [{"MLS": "26903565", "close_date": "2026-07-15", "close_price": 1709000.0, "year_built": 2026.0, "evidence_scope": "new-construction closing"}], "in_current_supply": false}
- {"address": "1208 E 26th Street Unit#A", "MLS": "58591599", "construction_phase": "complete", "current_market_status": "pending", "prior_stored_tag": ["complete", "pending", "active_split", "listed"], "conflict_class": ["C", "F"], "pin": "act_1208-e-26th-street-unit-a", "member": "act_1208-e-26th-street-unit-a", "phase_scope": "property", "historical_sales": [], "in_current_supply": false}
- {"address": "1122 E 27TH ST Unit#B", "MLS": "92767147", "construction_phase": null, "current_market_status": "sold", "prior_stored_tag": ["off_market_split", "listed"], "conflict_class": ["F"], "pin": "act_1122-e-27th-st-unit-b", "member": "act_1122-e-27th-st-unit-b", "phase_scope": "paired project", "historical_sales": [{"MLS": "92767147", "close_date": "2026-07-24", "close_price": 685000.0, "year_built": 2026.0, "evidence_scope": "new-construction closing"}], "in_current_supply": false}
- {"address": "827 W 16th Street Unit#A", "MLS": "89555500", "construction_phase": "mep_finals", "current_market_status": "pending", "prior_stored_tag": ["mep_finals", "off_market_split", "listed"], "conflict_class": ["F"], "pin": "act_827-w-16th-street-unit-a", "member": "act_827-w-16th-street-unit-a", "phase_scope": "property", "historical_sales": [], "in_current_supply": false}
- {"address": "1229 Prince Street", "MLS": "97105255", "construction_phase": null, "current_market_status": "sold", "prior_stored_tag": ["off_market_split"], "conflict_class": ["F"], "pin": "act_1229-prince-street", "member": "act_1229-prince-street", "phase_scope": "paired project", "historical_sales": [{"MLS": "97105255", "close_date": "2026-07-17", "close_price": 709900.0, "year_built": 2026.0, "evidence_scope": "new-construction closing"}], "in_current_supply": false}
- {"address": "1326 Lawrence Street", "MLS": "16373769", "construction_phase": null, "current_market_status": "sold", "prior_stored_tag": ["pending", "off_market_split"], "conflict_class": ["F"], "pin": "act_1326-lawrence-street", "member": "act_1326-lawrence-street", "phase_scope": "property", "historical_sales": [{"MLS": "16373769", "close_date": "2026-07-31", "close_price": 869900.0, "year_built": 2026.0, "evidence_scope": "new-construction closing"}], "in_current_supply": false}
- {"address": "815 Lawrence Street Unit#A", "MLS": "93385395", "construction_phase": null, "current_market_status": "sold", "prior_stored_tag": ["off_market_split"], "conflict_class": ["F"], "pin": "act_815-lawrence-street-unit-a", "member": "act_815-lawrence-street-unit-a", "phase_scope": "property", "historical_sales": [{"MLS": "93385395", "close_date": "2026-07-14", "close_price": 1070000.0, "year_built": 2026.0, "evidence_scope": "new-construction closing"}], "in_current_supply": false}
- {"address": "611 E 25th Street Unit#A", "MLS": "30142567", "construction_phase": null, "current_market_status": "sold", "prior_stored_tag": ["pending"], "conflict_class": ["F"], "pin": "act_611-e-25th-street-unit-a", "member": "act_611-e-25th-street-unit-a", "phase_scope": "paired project", "historical_sales": [{"MLS": "30142567", "close_date": "2026-05-21", "close_price": 1050000.0, "year_built": 2026.0, "evidence_scope": "new-construction closing"}], "in_current_supply": false}

## G. Listed/sold without tracked construction evidence — 68

- {"address": "615 Wendel Street", "MLS": "31557430", "source_file": "heightsactivesinglelots909.csv", "source_status": "active", "construction_phase": "no evidenced phase", "current_market_status": "active", "prior_stored_tag": ["active_single", "listed", "market"], "conflict_class": [], "matches": [{"pin": "act_615-wendel-street", "member": "act_615-wendel-street", "construction_phase": null}], "exclusion": null, "assessment": "Recent-build construction coverage gap", "year_built": 2025.0}
- {"address": "613 Wendel Street", "MLS": "6296220", "source_file": "heightsactivesinglelots909.csv", "source_status": "active", "construction_phase": "no evidenced phase", "current_market_status": "active", "prior_stored_tag": ["active_single", "listed", "market"], "conflict_class": [], "matches": [{"pin": "act_613-wendel", "member": "act_613-wendel", "construction_phase": null}], "exclusion": null, "assessment": "Recent-build construction coverage gap", "year_built": 2025.0}
- {"address": "1002 E 25th Street", "MLS": "72762085", "source_file": "heightsactivesinglelots909.csv", "source_status": "active", "construction_phase": "no evidenced phase", "current_market_status": "active", "prior_stored_tag": ["active_single", "listed", "market"], "conflict_class": [], "matches": [{"pin": "act_1002-e-25th-street", "member": "act_1002-e-25th-street", "construction_phase": null}], "exclusion": null, "assessment": "Recent-build construction coverage gap", "year_built": 2025.0}
- {"address": "830 E 27th Street Street", "MLS": "94349442", "source_file": "heightsactivesinglelots909.csv", "source_status": "active", "construction_phase": "no evidenced phase", "current_market_status": "active", "prior_stored_tag": ["active_single", "listed", "market"], "conflict_class": [], "matches": [{"pin": "act_830-e-27", "member": "act_830-e-27", "construction_phase": null}], "exclusion": null, "assessment": "Recent-build construction coverage gap", "year_built": 2025.0}
- {"address": "834 WAVERLY Street", "MLS": "46031576", "source_file": "heightsactivesinglelots909.csv", "source_status": "active", "construction_phase": "no evidenced phase", "current_market_status": "active", "prior_stored_tag": ["active_single", "listed", "market"], "conflict_class": [], "matches": [{"pin": "act_834-waverly-street", "member": "act_834-waverly-street", "construction_phase": null}], "exclusion": null, "assessment": "Recent-build construction coverage gap", "year_built": 2026.0}
- {"address": "1502 W 21st Street", "MLS": "22973800", "source_file": "heightsactivesinglelots909.csv", "source_status": "active", "construction_phase": "no evidenced phase", "current_market_status": "active", "prior_stored_tag": ["active_single", "listed", "market"], "conflict_class": [], "matches": [{"pin": "act_1502-w-21", "member": "act_1502-w-21", "construction_phase": null}], "exclusion": null, "assessment": "Recent-build construction coverage gap", "year_built": 2026.0}
- {"address": "705 Walton Street", "MLS": "6584972", "source_file": "heightsactivesinglelots909.csv", "source_status": "active", "construction_phase": "no evidenced phase", "current_market_status": "active", "prior_stored_tag": ["active_single", "listed", "market"], "conflict_class": [], "matches": [{"pin": "act_705-walton-street", "member": "act_705-walton-street", "construction_phase": null}], "exclusion": null, "assessment": "Recent-build construction coverage gap", "year_built": 2026.0}
- {"address": "3115 Beauchamp Street", "MLS": "54037481", "source_file": "heightsactivesinglelots909.csv", "source_status": "active", "construction_phase": "no evidenced phase", "current_market_status": "active", "prior_stored_tag": ["active_single", "listed", "market"], "conflict_class": [], "matches": [{"pin": "act_3115-beauchamp", "member": "act_3115-beauchamp", "construction_phase": null}], "exclusion": null, "assessment": "Recent-build construction coverage gap", "year_built": 2026.0}
- {"address": "830 WAVERLY Street", "MLS": "97695610", "source_file": "heightsactivesinglelots909.csv", "source_status": "active", "construction_phase": "no evidenced phase", "current_market_status": "active", "prior_stored_tag": ["active_single", "listed", "market"], "conflict_class": [], "matches": [{"pin": "act_830-waverly-street", "member": "act_830-waverly-street", "construction_phase": null}], "exclusion": null, "assessment": "Recent-build construction coverage gap", "year_built": 2026.0}
- {"address": "614 Ridge Street", "MLS": "90107924", "source_file": "heightsactivesinglelots909.csv", "source_status": "active", "construction_phase": "no evidenced phase", "current_market_status": "active", "prior_stored_tag": ["active_single", "listed", "market"], "conflict_class": [], "matches": [{"pin": "act_614-ridge-street", "member": "act_614-ridge-street", "construction_phase": null}], "exclusion": null, "assessment": "Recent-build construction coverage gap", "year_built": 2026.0}
- {"address": "1111 E 27th Street", "MLS": "26389093", "source_file": "heightsactivesinglelots909.csv", "source_status": "active", "construction_phase": "untracked", "current_market_status": "active", "prior_stored_tag": [], "conflict_class": [], "matches": [], "exclusion": null, "assessment": "Resale candidate; year built predates 2025, construction linkage unverified", "year_built": 2024.0}
- {"address": "2218 Gostick Street", "MLS": "87300082", "source_file": "heightsactivesinglelots909.csv", "source_status": "active", "construction_phase": "no evidenced phase", "current_market_status": "active", "prior_stored_tag": ["active_single", "listed", "market"], "conflict_class": [], "matches": [{"pin": "act_2218-gostick-street", "member": "act_2218-gostick-street", "construction_phase": null}], "exclusion": null, "assessment": "Recent-build construction coverage gap", "year_built": 2026.0}
- {"address": "2015 Harvard Street", "MLS": "7670973", "source_file": "heightsactivesinglelots909.csv", "source_status": "active", "construction_phase": "no evidenced phase", "current_market_status": "active", "prior_stored_tag": ["active_single", "listed", "market"], "conflict_class": [], "matches": [{"pin": "act_2015-harvard", "member": "act_2015-harvard", "construction_phase": null}], "exclusion": null, "assessment": "Recent-build construction coverage gap", "year_built": 2026.0}
- {"address": "1032 W 17th Street Unit#A", "MLS": "7485788", "source_file": "heightsactivesplitlots909.csv", "source_status": "active", "construction_phase": "no evidenced phase", "current_market_status": "active", "prior_stored_tag": ["active_split", "listed", "market"], "conflict_class": [], "matches": [{"pin": "act_1032-w-17th-street-unit-a", "member": "act_1032-w-17th-street-unit-a", "construction_phase": null}], "exclusion": null, "assessment": "Recent-build construction coverage gap", "year_built": 2026.0}
- {"address": "1122 E 27TH ST Unit#A", "MLS": "71690573", "source_file": "heightsactivesplitlots909.csv", "source_status": "active", "construction_phase": "no evidenced phase", "current_market_status": "active", "prior_stored_tag": [], "conflict_class": [], "matches": [{"pin": "act_1122-e-27th-st-unit-b", "member": "act_1122-e-27th-st-unit-a", "construction_phase": null}], "exclusion": null, "assessment": "Recent-build construction coverage gap", "year_built": 2026.0}
- {"address": "741 W 21st Street Unit#A", "MLS": "7364673", "source_file": "heightsactivesplitlots909.csv", "source_status": "active", "construction_phase": "no evidenced phase", "current_market_status": "active", "prior_stored_tag": ["active_split", "listed", "market"], "conflict_class": [], "matches": [{"pin": "act_741-w-21st-street-unit-a", "member": "act_741-w-21st-street-unit-a", "construction_phase": null}], "exclusion": null, "assessment": "Recent-build construction coverage gap", "year_built": 2026.0}
- {"address": "1227 Prince Street", "MLS": "22766797", "source_file": "heightsactivesplitlots909.csv", "source_status": "active", "construction_phase": "no evidenced phase", "current_market_status": "active", "prior_stored_tag": [], "conflict_class": [], "matches": [{"pin": "act_1229-prince-street", "member": "act_1227-prince-street", "construction_phase": null}], "exclusion": null, "assessment": "Recent-build construction coverage gap", "year_built": 2025.0}
- {"address": "611 E 25th Street Unit#B", "MLS": "57910089", "source_file": "heightsactivesplitlots909.csv", "source_status": "active", "construction_phase": "no evidenced phase", "current_market_status": "active", "prior_stored_tag": [], "conflict_class": [], "matches": [{"pin": "act_611-e-25th-street-unit-a", "member": "act_611-e-25th-street-unit-b", "construction_phase": null}], "exclusion": null, "assessment": "Recent-build construction coverage gap", "year_built": 2026.0}
- {"address": "710 Waverly Street Unit#D", "MLS": "32352560", "source_file": "heightsactivesplitlots909.csv", "source_status": "active", "construction_phase": "no evidenced phase", "current_market_status": "active", "prior_stored_tag": ["active_split", "listed", "market"], "conflict_class": [], "matches": [{"pin": "act_710-waverly-street-unit-d", "member": "act_710-waverly-street-unit-d", "construction_phase": null}], "exclusion": null, "assessment": "Recent-build construction coverage gap", "year_built": 2025.0}
- {"address": "1504 W 21st Street", "MLS": "14206939", "source_file": "heightsactivesplitlots909.csv", "source_status": "active", "construction_phase": "no evidenced phase", "current_market_status": "active", "prior_stored_tag": [], "conflict_class": [], "matches": [{"pin": "act_1502-w-21", "member": "act_1504-w-21st-street", "construction_phase": null}], "exclusion": null, "assessment": "Recent-build construction coverage gap", "year_built": 2026.0}
- {"address": "1315 Waverly Street", "MLS": "62006938", "source_file": "heightspendingsinglelots909.csv", "source_status": "pending", "construction_phase": "no evidenced phase", "current_market_status": "pending", "prior_stored_tag": ["active_single", "listed", "market"], "conflict_class": ["F"], "matches": [{"pin": "act_1315-waverly", "member": "act_1315-waverly", "construction_phase": null}], "exclusion": null, "assessment": "Recent-build construction coverage gap", "year_built": 2025.0}
- {"address": "816 W 17TH Street", "MLS": "81354398", "source_file": "heightspendingsplitlots909.csv", "source_status": "pending", "construction_phase": "no evidenced phase", "current_market_status": "pending", "prior_stored_tag": [], "conflict_class": [], "matches": [{"pin": "act_814-w-17th-street", "member": "act_816-w-17th-street", "construction_phase": null}], "exclusion": null, "assessment": "Recent-build construction coverage gap", "year_built": 2026.0}
- {"address": "814 W 17TH Street", "MLS": "62144090", "source_file": "heightspendingsplitlots909.csv", "source_status": "pending", "construction_phase": "no evidenced phase", "current_market_status": "pending", "prior_stored_tag": ["pending"], "conflict_class": [], "matches": [{"pin": "act_814-w-17th-street", "member": "act_814-w-17th-street", "construction_phase": null}], "exclusion": null, "assessment": "Recent-build construction coverage gap", "year_built": 2026.0}
- {"address": "1737 Tabor Street", "MLS": "89124616", "source_file": "heightssoldsinglelotslast180days.csv", "source_status": "sold", "construction_phase": "untracked", "current_market_status": "sold", "prior_stored_tag": [], "conflict_class": [], "matches": [], "exclusion": null, "assessment": "Recent-build construction coverage gap", "year_built": 2025.0}
- {"address": "1207 Tabor Street", "MLS": "85478626", "source_file": "heightssoldsinglelotslast180days.csv", "source_status": "sold", "construction_phase": "no evidenced phase", "current_market_status": "sold", "prior_stored_tag": ["active_single", "listed", "market", "pending"], "conflict_class": ["F"], "matches": [{"pin": "act_1207-tabor", "member": "act_1207-tabor", "construction_phase": null}], "exclusion": null, "assessment": "Recent-build construction coverage gap", "year_built": 2026.0}
- {"address": "1023 E 23rd Street", "MLS": "50869013", "source_file": "heightssoldsinglelotslast180days.csv", "source_status": "sold", "construction_phase": "untracked", "current_market_status": "sold", "prior_stored_tag": [], "conflict_class": [], "matches": [], "exclusion": null, "assessment": "Recent-build construction coverage gap", "year_built": 2026.0}
- {"address": "903 Tabor Street", "MLS": "93127419", "source_file": "heightssoldsinglelotslast180days.csv", "source_status": "sold", "construction_phase": "untracked", "current_market_status": "sold", "prior_stored_tag": [], "conflict_class": [], "matches": [], "exclusion": null, "assessment": "Recent-build construction coverage gap", "year_built": 2025.0}
- {"address": "107 E 24th Street", "MLS": "95407673", "source_file": "heightssoldsinglelotslast180days.csv", "source_status": "sold", "construction_phase": "no evidenced phase", "current_market_status": "sold", "prior_stored_tag": ["off_market_single"], "conflict_class": ["F"], "matches": [{"pin": "act_107-e-24", "member": "act_107-e-24", "construction_phase": null}], "exclusion": null, "assessment": "Recent-build construction coverage gap", "year_built": 2026.0}
- {"address": "1520 Nicholson Street", "MLS": "33839156", "source_file": "heightssoldsinglelotslast180days.csv", "source_status": "sold", "construction_phase": "no evidenced phase", "current_market_status": "sold", "prior_stored_tag": ["listed", "off_market_single"], "conflict_class": ["F"], "matches": [{"pin": "act_1520-nicholson", "member": "act_1520-nicholson", "construction_phase": null}], "exclusion": null, "assessment": "Recent-build construction coverage gap", "year_built": 2026.0}
- {"address": "1524 Nicholson St", "MLS": "64831168", "source_file": "heightssoldsinglelotslast180days.csv", "source_status": "sold", "construction_phase": "untracked", "current_market_status": "sold", "prior_stored_tag": [], "conflict_class": [], "matches": [], "exclusion": null, "assessment": "Recent-build construction coverage gap", "year_built": 2025.0}
- {"address": "1106 Robbie Street", "MLS": "96094299", "source_file": "heightssoldsinglelotslast180days.csv", "source_status": "sold", "construction_phase": "untracked", "current_market_status": "sold", "prior_stored_tag": [], "conflict_class": [], "matches": [], "exclusion": null, "assessment": "Recent-build construction coverage gap", "year_built": 2025.0}
- {"address": "710 E 18th Street", "MLS": "71056150", "source_file": "heightssoldsinglelotslast180days.csv", "source_status": "sold", "construction_phase": "no evidenced phase", "current_market_status": "sold", "prior_stored_tag": ["off_market_single", "pending"], "conflict_class": ["F"], "matches": [{"pin": "act_710-e-18", "member": "act_710-e-18", "construction_phase": null}], "exclusion": null, "assessment": "Recent-build construction coverage gap", "year_built": 2025.0}
- {"address": "709 Ridge Street", "MLS": "26903565", "source_file": "heightssoldsinglelotslast180days.csv", "source_status": "sold", "construction_phase": "no evidenced phase", "current_market_status": "sold", "prior_stored_tag": ["off_market_single"], "conflict_class": ["F"], "matches": [{"pin": "act_709-ridge", "member": "act_709-ridge", "construction_phase": null}], "exclusion": null, "assessment": "Recent-build construction coverage gap", "year_built": 2026.0}
- {"address": "1023 Euclid Street", "MLS": "35621139", "source_file": "heightssoldsinglelotslast180days.csv", "source_status": "sold", "construction_phase": "no evidenced phase", "current_market_status": "sold", "prior_stored_tag": ["listed", "pending"], "conflict_class": ["F"], "matches": [{"pin": "act_1023-euclid", "member": "act_1023-euclid", "construction_phase": null}], "exclusion": null, "assessment": "Recent-build construction coverage gap", "year_built": 2025.0}
- {"address": "402 Columbia Street", "MLS": "33729025", "source_file": "heightssoldsinglelotslast180days.csv", "source_status": "sold", "construction_phase": "untracked", "current_market_status": "sold", "prior_stored_tag": [], "conflict_class": [], "matches": [], "exclusion": null, "assessment": "Recent-build construction coverage gap", "year_built": 2026.0}
- {"address": "406 Columbia Street", "MLS": "78950517", "source_file": "heightssoldsinglelotslast180days.csv", "source_status": "sold", "construction_phase": "untracked", "current_market_status": "sold", "prior_stored_tag": [], "conflict_class": [], "matches": [], "exclusion": null, "assessment": "Recent-build construction coverage gap", "year_built": 2026.0}
- {"address": "1119 E 7th 1/2 Street", "MLS": "90671798", "source_file": "heightssoldsinglelotslast180days.csv", "source_status": "sold", "construction_phase": "untracked", "current_market_status": "sold", "prior_stored_tag": [], "conflict_class": [], "matches": [], "exclusion": null, "assessment": "Recent-build construction coverage gap", "year_built": 2026.0}
- {"address": "726 E 7th Street", "MLS": "16593438", "source_file": "heightssoldsinglelotslast180days.csv", "source_status": "sold", "construction_phase": "untracked", "current_market_status": "sold", "prior_stored_tag": [], "conflict_class": [], "matches": [], "exclusion": null, "assessment": "Recent-build construction coverage gap", "year_built": 2026.0}
- {"address": "2612 Greenleaf Street", "MLS": "65984026", "source_file": "heightssoldsinglelotslast180days.csv", "source_status": "sold", "construction_phase": "untracked", "current_market_status": "sold", "prior_stored_tag": [], "conflict_class": [], "matches": [], "exclusion": null, "assessment": "Recent-build construction coverage gap", "year_built": 2026.0}
- {"address": "1001 E 7th 1/2 Street", "MLS": "19950202", "source_file": "heightssoldsinglelotslast180days.csv", "source_status": "sold", "construction_phase": "untracked", "current_market_status": "sold", "prior_stored_tag": [], "conflict_class": [], "matches": [], "exclusion": null, "assessment": "Recent-build construction coverage gap", "year_built": 2026.0}
- {"address": "1316 Heslep Street", "MLS": "38995142", "source_file": "heightssoldsplitlotslast180days.csv", "source_status": "sold", "construction_phase": "untracked", "current_market_status": "sold", "prior_stored_tag": [], "conflict_class": [], "matches": [], "exclusion": null, "assessment": "Recent-build construction coverage gap", "year_built": 2026.0}
- {"address": "602 Jewett Street Unit#A", "MLS": "94906411", "source_file": "heightssoldsplitlotslast180days.csv", "source_status": "sold", "construction_phase": "untracked", "current_market_status": "sold", "prior_stored_tag": [], "conflict_class": [], "matches": [], "exclusion": null, "assessment": "Recent-build construction coverage gap", "year_built": 2025.0}
- {"address": "1438-A Dian Street", "MLS": "66717038", "source_file": "heightssoldsplitlotslast180days.csv", "source_status": "sold", "construction_phase": "untracked", "current_market_status": "sold", "prior_stored_tag": [], "conflict_class": [], "matches": [], "exclusion": null, "assessment": "Recent-build construction coverage gap", "year_built": 2025.0}
- {"address": "1208 E 26th Street Unit#B", "MLS": "8458741", "source_file": "heightssoldsplitlotslast180days.csv", "source_status": "sold", "construction_phase": "untracked", "current_market_status": "sold", "prior_stored_tag": [], "conflict_class": [], "matches": [], "exclusion": null, "assessment": "Recent-build construction coverage gap", "year_built": 2026.0}
- {"address": "1303 Cordell Street Unit#A", "MLS": "9530397", "source_file": "heightssoldsplitlotslast180days.csv", "source_status": "sold", "construction_phase": "untracked", "current_market_status": "sold", "prior_stored_tag": [], "conflict_class": [], "matches": [], "exclusion": null, "assessment": "Recent-build construction coverage gap", "year_built": 2025.0}
- {"address": "1121 E 24th Street", "MLS": "13147368", "source_file": "heightssoldsplitlotslast180days.csv", "source_status": "sold", "construction_phase": "untracked", "current_market_status": "sold", "prior_stored_tag": [], "conflict_class": [], "matches": [], "exclusion": null, "assessment": "Recent-build construction coverage gap", "year_built": 2026.0}
- {"address": "1125 E 24th Street", "MLS": "61559810", "source_file": "heightssoldsplitlotslast180days.csv", "source_status": "sold", "construction_phase": "untracked", "current_market_status": "sold", "prior_stored_tag": [], "conflict_class": [], "matches": [], "exclusion": null, "assessment": "Recent-build construction coverage gap", "year_built": 2026.0}
- {"address": "310 E 28th St", "MLS": "78621450", "source_file": "heightssoldsplitlotslast180days.csv", "source_status": "sold", "construction_phase": "untracked", "current_market_status": "sold", "prior_stored_tag": [], "conflict_class": [], "matches": [], "exclusion": null, "assessment": "Recent-build construction coverage gap", "year_built": 2025.0}
- {"address": "224 E 27th Street", "MLS": "79405032", "source_file": "heightssoldsplitlotslast180days.csv", "source_status": "sold", "construction_phase": "untracked", "current_market_status": "sold", "prior_stored_tag": [], "conflict_class": [], "matches": [], "exclusion": null, "assessment": "Recent-build construction coverage gap", "year_built": 2026.0}
- {"address": "1524 W 21st St", "MLS": "76530080", "source_file": "heightssoldsplitlotslast180days.csv", "source_status": "sold", "construction_phase": "untracked", "current_market_status": "sold", "prior_stored_tag": [], "conflict_class": [], "matches": [], "exclusion": null, "assessment": "Recent-build construction coverage gap", "year_built": 2026.0}
- {"address": "1122 E 27TH ST Unit#B", "MLS": "92767147", "source_file": "heightssoldsplitlotslast180days.csv", "source_status": "sold", "construction_phase": "no evidenced phase", "current_market_status": "sold", "prior_stored_tag": ["listed", "off_market_split"], "conflict_class": ["F"], "matches": [{"pin": "act_1122-e-27th-st-unit-b", "member": "act_1122-e-27th-st-unit-b", "construction_phase": null}], "exclusion": null, "assessment": "Recent-build construction coverage gap", "year_built": 2026.0}
- {"address": "1229 Prince Street", "MLS": "97105255", "source_file": "heightssoldsplitlotslast180days.csv", "source_status": "sold", "construction_phase": "no evidenced phase", "current_market_status": "sold", "prior_stored_tag": ["off_market_split"], "conflict_class": ["F"], "matches": [{"pin": "act_1229-prince-street", "member": "act_1229-prince-street", "construction_phase": null}], "exclusion": null, "assessment": "Recent-build construction coverage gap", "year_built": 2026.0}
- {"address": "406 E 28th Street", "MLS": "77501317", "source_file": "heightssoldsplitlotslast180days.csv", "source_status": "sold", "construction_phase": "untracked", "current_market_status": "sold", "prior_stored_tag": [], "conflict_class": [], "matches": [], "exclusion": null, "assessment": "Recent-build construction coverage gap", "year_built": 2026.0}
- {"address": "1436 Alexander St", "MLS": "5279771", "source_file": "heightssoldsplitlotslast180days.csv", "source_status": "sold", "construction_phase": "untracked", "current_market_status": "sold", "prior_stored_tag": [], "conflict_class": [], "matches": [], "exclusion": null, "assessment": "Recent-build construction coverage gap", "year_built": 2026.0}
- {"address": "404 E 28th Street", "MLS": "87693150", "source_file": "heightssoldsplitlotslast180days.csv", "source_status": "sold", "construction_phase": "untracked", "current_market_status": "sold", "prior_stored_tag": [], "conflict_class": [], "matches": [], "exclusion": null, "assessment": "Recent-build construction coverage gap", "year_built": 2025.0}
- {"address": "1321 Alexander Street", "MLS": "10970361", "source_file": "heightssoldsplitlotslast180days.csv", "source_status": "sold", "construction_phase": "untracked", "current_market_status": "sold", "prior_stored_tag": [], "conflict_class": [], "matches": [], "exclusion": null, "assessment": "Recent-build construction coverage gap", "year_built": 2025.0}
- {"address": "1516 Dorothy Street Unit#A", "MLS": "12794628", "source_file": "heightssoldsplitlotslast180days.csv", "source_status": "sold", "construction_phase": "untracked", "current_market_status": "sold", "prior_stored_tag": [], "conflict_class": [], "matches": [], "exclusion": null, "assessment": "Recent-build construction coverage gap", "year_built": 2025.0}
- {"address": "1516 Dorothy Street Unit#C", "MLS": "24145604", "source_file": "heightssoldsplitlotslast180days.csv", "source_status": "sold", "construction_phase": "untracked", "current_market_status": "sold", "prior_stored_tag": [], "conflict_class": [], "matches": [], "exclusion": null, "assessment": "Recent-build construction coverage gap", "year_built": 2025.0}
- {"address": "1326 Lawrence Street", "MLS": "16373769", "source_file": "heightssoldsplitlotslast180days.csv", "source_status": "sold", "construction_phase": "no evidenced phase", "current_market_status": "sold", "prior_stored_tag": ["off_market_split", "pending"], "conflict_class": ["F"], "matches": [{"pin": "act_1326-lawrence-street", "member": "act_1326-lawrence-street", "construction_phase": null}], "exclusion": null, "assessment": "Recent-build construction coverage gap", "year_built": 2026.0}
- {"address": "827 W 16th Street Unit#B", "MLS": "42479147", "source_file": "heightssoldsplitlotslast180days.csv", "source_status": "sold", "construction_phase": "untracked", "current_market_status": "sold", "prior_stored_tag": [], "conflict_class": [], "matches": [], "exclusion": null, "assessment": "Recent-build construction coverage gap", "year_built": 2026.0}
- {"address": "525 W 26th Street", "MLS": "88804104", "source_file": "heightssoldsplitlotslast180days.csv", "source_status": "sold", "construction_phase": "untracked", "current_market_status": "sold", "prior_stored_tag": [], "conflict_class": [], "matches": [], "exclusion": null, "assessment": "Recent-build construction coverage gap", "year_built": 2026.0}
- {"address": "527 W 26th Street", "MLS": "10589101", "source_file": "heightssoldsplitlotslast180days.csv", "source_status": "sold", "construction_phase": "untracked", "current_market_status": "sold", "prior_stored_tag": [], "conflict_class": [], "matches": [], "exclusion": null, "assessment": "Recent-build construction coverage gap", "year_built": 2026.0}
- {"address": "2715 BEAUCHAMP Street", "MLS": "90312385", "source_file": "heightssoldsplitlotslast180days.csv", "source_status": "sold", "construction_phase": "untracked", "current_market_status": "sold", "prior_stored_tag": [], "conflict_class": [], "matches": [], "exclusion": null, "assessment": "Recent-build construction coverage gap", "year_built": 2026.0}
- {"address": "611 E 25th Street Unit#A", "MLS": "30142567", "source_file": "heightssoldsplitlotslast180days.csv", "source_status": "sold", "construction_phase": "no evidenced phase", "current_market_status": "sold", "prior_stored_tag": ["pending"], "conflict_class": ["F"], "matches": [{"pin": "act_611-e-25th-street-unit-a", "member": "act_611-e-25th-street-unit-a", "construction_phase": null}], "exclusion": null, "assessment": "Recent-build construction coverage gap", "year_built": 2026.0}
- {"address": "2713 BEAUCHAMP Street", "MLS": "60919011", "source_file": "heightssoldsplitlotslast180days.csv", "source_status": "sold", "construction_phase": "untracked", "current_market_status": "sold", "prior_stored_tag": [], "conflict_class": [], "matches": [], "exclusion": null, "assessment": "Recent-build construction coverage gap", "year_built": 2026.0}
- {"address": "815 Lawrence Street Unit#A", "MLS": "93385395", "source_file": "heightssoldsplitlotslast180days.csv", "source_status": "sold", "construction_phase": "no evidenced phase", "current_market_status": "sold", "prior_stored_tag": ["off_market_split"], "conflict_class": ["F"], "matches": [{"pin": "act_815-lawrence-street-unit-a", "member": "act_815-lawrence-street-unit-a", "construction_phase": null}], "exclusion": null, "assessment": "Recent-build construction coverage gap", "year_built": 2026.0}
- {"address": "815B Lawrence Street", "MLS": "69395685", "source_file": "heightssoldsplitlotslast180days.csv", "source_status": "sold", "construction_phase": "untracked", "current_market_status": "sold", "prior_stored_tag": [], "conflict_class": [], "matches": [], "exclusion": null, "assessment": "Recent-build construction coverage gap", "year_built": 2026.0}
- {"address": "710 Waverly Street Unit#E", "MLS": "94092178", "source_file": "heightssoldsplitlotslast180days.csv", "source_status": "sold", "construction_phase": "untracked", "current_market_status": "sold", "prior_stored_tag": [], "conflict_class": [], "matches": [], "exclusion": null, "assessment": "Recent-build construction coverage gap", "year_built": 2025.0}

## H. Under construction and active — 26

- {"address": "2011 Singleton St, Houston, Tx 77008", "MLS": "5383346", "construction_phase": "mep_finals", "current_market_status": "active", "prior_stored_tag": ["mep_finals", "active_single", "listed"], "conflict_class": ["H"], "pin": "2131129832", "member": "2131129832", "phase_scope": "property", "historical_sales": [], "in_current_supply": true}
- {"address": "711 E 26TH Street", "MLS": "36627624", "construction_phase": "interior", "current_market_status": "active", "prior_stored_tag": [], "conflict_class": ["H"], "pin": "2131192874", "member": "act_711-e-26th-street", "phase_scope": "paired project", "historical_sales": [], "in_current_supply": true}
- {"address": "1120 E 26th St, Houston, Tx 77009", "MLS": "29146166", "construction_phase": "interior", "current_market_status": "active", "prior_stored_tag": ["interior", "active_split", "listed"], "conflict_class": ["H"], "pin": "2131318242", "member": "2131318242", "phase_scope": "paired project", "historical_sales": [], "in_current_supply": true}
- {"address": "410 Merrill St, Houston, Tx 77009", "MLS": "31444523", "construction_phase": "interior", "current_market_status": "active", "prior_stored_tag": ["interior", "needs_clarification"], "conflict_class": ["H"], "pin": "2131421176", "member": "2131421176", "phase_scope": "property", "historical_sales": [], "in_current_supply": true}
- {"address": "312 w 9th St", "MLS": "16999317", "construction_phase": "interior", "current_market_status": "active", "prior_stored_tag": [], "conflict_class": ["H"], "pin": "pmt_310-w-9th-st-77007", "member": "act_312-w-9th-st", "phase_scope": "paired project", "historical_sales": [], "in_current_supply": true}
- {"address": "906 Bayland Ave, Houston, TX 77009", "MLS": "56747960", "construction_phase": "mep_finals", "current_market_status": "active", "prior_stored_tag": ["mep_finals"], "conflict_class": ["H"], "pin": "pmt_906-bayland-ave-77009", "member": "pmt_906-bayland-ave-77009", "phase_scope": "property", "historical_sales": [], "in_current_supply": true}
- {"address": "1012 E 26TH Street", "MLS": "54722254", "construction_phase": "insulation", "current_market_status": "active", "prior_stored_tag": [], "conflict_class": ["H"], "pin": "pmt_1010-e-26th-st-77009", "member": "act_1012-e-26th-street", "phase_scope": "paired project", "historical_sales": [], "in_current_supply": true}
- {"address": "1122 Robbie Street", "MLS": "89794015", "construction_phase": "mep_finals", "current_market_status": "active", "prior_stored_tag": [], "conflict_class": ["H"], "pin": "pmt_1124-robbie-st-77009", "member": "act_1122-robbie-street", "phase_scope": "paired project", "historical_sales": [], "in_current_supply": true}
- {"address": "920 E 25TH Street", "MLS": "35798306", "construction_phase": "interior", "current_market_status": "active", "prior_stored_tag": ["interior", "active_single", "listed"], "conflict_class": ["H"], "pin": "act_920-e-25", "member": "act_920-e-25", "phase_scope": "property", "historical_sales": [], "in_current_supply": true}
- {"address": "2603 JULIAN Street", "MLS": "87208794", "construction_phase": "mep_roughs", "current_market_status": "active", "prior_stored_tag": ["mep_roughs", "active_single", "listed"], "conflict_class": ["H"], "pin": "act_2603-julian", "member": "act_2603-julian", "phase_scope": "property", "historical_sales": [], "in_current_supply": true}
- {"address": "623 E 13th Street", "MLS": "89411837", "construction_phase": "mep_finals", "current_market_status": "active", "prior_stored_tag": ["mep_finals", "active_single", "listed"], "conflict_class": ["H"], "pin": "act_623-e-13", "member": "act_623-e-13", "phase_scope": "property", "historical_sales": [], "in_current_supply": true}
- {"address": "603 E 23rd Street", "MLS": "70087101", "construction_phase": "interior", "current_market_status": "active", "prior_stored_tag": ["interior", "active_single", "listed"], "conflict_class": ["H"], "pin": "act_603-e-23", "member": "act_603-e-23", "phase_scope": "property", "historical_sales": [], "in_current_supply": true}
- {"address": "735 E 8TH 1/2 Street", "MLS": "5069786", "construction_phase": "interior", "current_market_status": "active", "prior_stored_tag": ["interior", "active_single", "listed"], "conflict_class": ["H"], "pin": "act_735-e-8-12", "member": "act_735-e-8-12", "phase_scope": "property", "historical_sales": [], "in_current_supply": true}
- {"address": "731 E 8TH 1/2 Street", "MLS": "40836939", "construction_phase": "interior", "current_market_status": "active", "prior_stored_tag": ["interior", "active_single", "listed"], "conflict_class": ["H"], "pin": "act_731-e-8-12", "member": "act_731-e-8-12", "phase_scope": "property", "historical_sales": [], "in_current_supply": true}
- {"address": "248 W 22nd Street", "MLS": "89221155", "construction_phase": "interior", "current_market_status": "active", "prior_stored_tag": ["interior", "active_single", "listed"], "conflict_class": ["H"], "pin": "act_248-w-22", "member": "act_248-w-22", "phase_scope": "property", "historical_sales": [], "in_current_supply": true}
- {"address": "2434 White Oak Drive", "MLS": "9001753", "construction_phase": "framing", "current_market_status": "active", "prior_stored_tag": ["framing", "active_single", "listed"], "conflict_class": ["H"], "pin": "act_2434-white-oak", "member": "act_2434-white-oak", "phase_scope": "property", "historical_sales": [], "in_current_supply": true}
- {"address": "1140 Waverly Street", "MLS": "57009282", "construction_phase": "interior", "current_market_status": "active", "prior_stored_tag": ["interior", "active_single", "listed"], "conflict_class": ["H"], "pin": "act_1140-waverly", "member": "act_1140-waverly", "phase_scope": "property", "historical_sales": [], "in_current_supply": true}
- {"address": "2436 White Oak", "MLS": "68235642", "construction_phase": "framing", "current_market_status": "active", "prior_stored_tag": ["framing", "active_single", "listed"], "conflict_class": ["H"], "pin": "act_2436-white-oak", "member": "act_2436-white-oak", "phase_scope": "property", "historical_sales": [], "in_current_supply": true}
- {"address": "1002 E 6TH 1/2 Street", "MLS": "93562410", "construction_phase": "mep_finals", "current_market_status": "active", "prior_stored_tag": ["mep_finals", "active_single", "listed"], "conflict_class": ["H"], "pin": "act_1002-e-6-12", "member": "act_1002-e-6-12", "phase_scope": "property", "historical_sales": [], "in_current_supply": true}
- {"address": "1218 Prince Street", "MLS": "57925491", "construction_phase": "exterior", "current_market_status": "active", "prior_stored_tag": ["exterior", "active_split", "listed"], "conflict_class": ["H"], "pin": "act_1218-prince-street", "member": "act_1218-prince-street", "phase_scope": "property", "historical_sales": [], "in_current_supply": true}
- {"address": "805 W 22nd Street", "MLS": "4182331", "construction_phase": "interior", "current_market_status": "active", "prior_stored_tag": ["interior", "active_split", "listed"], "conflict_class": ["H"], "pin": "act_805-w-22nd-street", "member": "act_805-w-22nd-street", "phase_scope": "paired project", "historical_sales": [], "in_current_supply": true}
- {"address": "318 W 21st Street", "MLS": "69573145", "construction_phase": "interior", "current_market_status": "active", "prior_stored_tag": ["interior", "active_split", "listed"], "conflict_class": ["H"], "pin": "act_318-w-21st-street", "member": "act_318-w-21st-street", "phase_scope": "paired project", "historical_sales": [], "in_current_supply": true}
- {"address": "407 E 27TH Street", "MLS": "10210884", "construction_phase": "mep_finals", "current_market_status": "active", "prior_stored_tag": ["mep_finals", "active_split", "listed"], "conflict_class": ["H"], "pin": "act_407-e-27th-street", "member": "act_407-e-27th-street", "phase_scope": "paired project", "historical_sales": [], "in_current_supply": true}
- {"address": "1138 Fugate St, Houston, TX 77009", "MLS": "64823156", "construction_phase": "mep_finals", "current_market_status": "active", "prior_stored_tag": ["mep_finals"], "conflict_class": ["H"], "pin": "pmt_1138-fugate-st-77009", "member": "pmt_1138-fugate-st-77009", "phase_scope": "property", "historical_sales": [], "in_current_supply": true}
- {"address": "2924 Watson Street", "MLS": "70723638", "construction_phase": "interior", "current_market_status": "active", "prior_stored_tag": ["interior", "active_single", "listed"], "conflict_class": ["H"], "pin": "act_2924-watson-street", "member": "act_2924-watson-street", "phase_scope": "property", "historical_sales": [], "in_current_supply": true}
- {"address": "845 W 23rd St A, Houston, TX 77008", "MLS": "17612330", "construction_phase": "foundation", "current_market_status": "active", "prior_stored_tag": ["foundation"], "conflict_class": ["H"], "pin": "pmt_845-w-23rd-st-a-77008", "member": "pmt_845-w-23rd-st-a-77008", "phase_scope": "property", "historical_sales": [], "in_current_supply": true}

## Complete: all represented homes
```json
[
  {
    "address": "118 E 23rd St, Houston, Tx 77008",
    "MLS": "",
    "construction_phase": "complete",
    "current_market_status": "no market record",
    "prior_stored_tag": [
      "complete"
    ],
    "conflict_class": [
      "D"
    ],
    "pin": "2131144961",
    "member": "2131144961",
    "phase_scope": "paired project",
    "historical_sales": [],
    "in_current_supply": false
  },
  {
    "address": "116 E 23RD Street",
    "MLS": "81689864",
    "construction_phase": "complete",
    "current_market_status": "pending",
    "prior_stored_tag": [],
    "conflict_class": [
      "C"
    ],
    "pin": "2131144961",
    "member": "act_116-e-23rd-street",
    "phase_scope": "paired project",
    "historical_sales": [],
    "in_current_supply": false
  },
  {
    "address": "709 E 17th St, Houston, Tx 77008",
    "MLS": "72560168",
    "construction_phase": "complete",
    "current_market_status": "sold",
    "prior_stored_tag": [
      "complete",
      "pending",
      "active_single",
      "listed"
    ],
    "conflict_class": [
      "A",
      "F"
    ],
    "pin": "2131432164",
    "member": "2131432164",
    "phase_scope": "property",
    "historical_sales": [
      {
        "MLS": "72560168",
        "close_date": "2026-08-24",
        "close_price": 1755000.0,
        "year_built": 2026.0,
        "evidence_scope": "new-construction closing"
      }
    ],
    "in_current_supply": false
  },
  {
    "address": "1520 W 21st St Unit#B",
    "MLS": "",
    "construction_phase": "complete",
    "current_market_status": "no market record",
    "prior_stored_tag": [
      "complete",
      "active_split",
      "listed"
    ],
    "conflict_class": [
      "D"
    ],
    "pin": "act_1520-w-21st-st-unit-b",
    "member": "act_1520-w-21st-st-unit-b",
    "phase_scope": "paired project",
    "historical_sales": [],
    "in_current_supply": false
  },
  {
    "address": "1520 W 21st St Unit#A",
    "MLS": "95958213",
    "construction_phase": "complete",
    "current_market_status": "active",
    "prior_stored_tag": [],
    "conflict_class": [
      "B"
    ],
    "pin": "act_1520-w-21st-st-unit-b",
    "member": "act_1520-w-21st-st-unit-a",
    "phase_scope": "paired project",
    "historical_sales": [],
    "in_current_supply": false
  },
  {
    "address": "1623 Blount St, Houston, TX 77008",
    "MLS": "",
    "construction_phase": "complete",
    "current_market_status": "no market record",
    "prior_stored_tag": [
      "complete"
    ],
    "conflict_class": [
      "D"
    ],
    "pin": "pmt_1623-blount-st-77008",
    "member": "pmt_1623-blount-st-77008",
    "phase_scope": "property",
    "historical_sales": [],
    "in_current_supply": false
  },
  {
    "address": "1343 Nashua St, Houston, TX 77008",
    "MLS": "",
    "construction_phase": "complete",
    "current_market_status": "no market record",
    "prior_stored_tag": [
      "complete"
    ],
    "conflict_class": [
      "D"
    ],
    "pin": "pmt_1343-nashua-st-77008",
    "member": "pmt_1343-nashua-st-77008",
    "phase_scope": "property",
    "historical_sales": [],
    "in_current_supply": false
  },
  {
    "address": "2013 Sheldon St A, Houston, TX 77008",
    "MLS": "86833589",
    "construction_phase": "complete",
    "current_market_status": "sold",
    "prior_stored_tag": [
      "complete"
    ],
    "conflict_class": [
      "A"
    ],
    "pin": "pmt_2013-sheldon-st-a-77008",
    "member": "pmt_2013-sheldon-st-a-77008",
    "phase_scope": "paired project",
    "historical_sales": [
      {
        "MLS": "86833589",
        "close_date": "2026-05-20",
        "close_price": 899900,
        "year_built": 2026,
        "evidence_scope": "new-construction closing"
      }
    ],
    "in_current_supply": false
  },
  {
    "address": "2013 Sheldon St B, Houston, TX 77008",
    "MLS": "",
    "construction_phase": "complete",
    "current_market_status": "no market record",
    "prior_stored_tag": [],
    "conflict_class": [
      "D"
    ],
    "pin": "pmt_2013-sheldon-st-a-77008",
    "member": "pmt_2013-sheldon-st-b-77008",
    "phase_scope": "paired project",
    "historical_sales": [],
    "in_current_supply": false
  },
  {
    "address": "737 W 21st St C, Houston, TX 77008",
    "MLS": "",
    "construction_phase": "complete",
    "current_market_status": "no market record",
    "prior_stored_tag": [
      "complete"
    ],
    "conflict_class": [
      "D"
    ],
    "pin": "pmt_737-w-21st-st-c-77008",
    "member": "pmt_737-w-21st-st-c-77008",
    "phase_scope": "property",
    "historical_sales": [],
    "in_current_supply": false
  },
  {
    "address": "737 W 21st St B, Houston, TX 77008",
    "MLS": "",
    "construction_phase": "complete",
    "current_market_status": "no market record",
    "prior_stored_tag": [
      "complete"
    ],
    "conflict_class": [
      "D"
    ],
    "pin": "pmt_737-w-21st-st-b-77008",
    "member": "pmt_737-w-21st-st-b-77008",
    "phase_scope": "property",
    "historical_sales": [],
    "in_current_supply": false
  },
  {
    "address": "737 W 21st St A, Houston, TX 77008",
    "MLS": "",
    "construction_phase": "complete",
    "current_market_status": "no market record",
    "prior_stored_tag": [
      "complete"
    ],
    "conflict_class": [
      "D"
    ],
    "pin": "pmt_737-w-21st-st-a-77008",
    "member": "pmt_737-w-21st-st-a-77008",
    "phase_scope": "property",
    "historical_sales": [],
    "in_current_supply": false
  },
  {
    "address": "737 W 21st St D, Houston, TX 77008",
    "MLS": "",
    "construction_phase": "complete",
    "current_market_status": "no market record",
    "prior_stored_tag": [
      "complete"
    ],
    "conflict_class": [
      "D"
    ],
    "pin": "pmt_737-w-21st-st-d-77008",
    "member": "pmt_737-w-21st-st-d-77008",
    "phase_scope": "property",
    "historical_sales": [],
    "in_current_supply": false
  },
  {
    "address": "729 W 21st St A, Houston, TX 77008",
    "MLS": "",
    "construction_phase": "complete",
    "current_market_status": "no market record",
    "prior_stored_tag": [
      "complete"
    ],
    "conflict_class": [
      "D"
    ],
    "pin": "pmt_729-w-21st-st-a-77008",
    "member": "pmt_729-w-21st-st-a-77008",
    "phase_scope": "property",
    "historical_sales": [],
    "in_current_supply": false
  },
  {
    "address": "723 W 21st St, Houston, TX 77008",
    "MLS": "",
    "construction_phase": "complete",
    "current_market_status": "no market record",
    "prior_stored_tag": [
      "complete"
    ],
    "conflict_class": [
      "D"
    ],
    "pin": "pmt_723-w-21st-st-77008",
    "member": "pmt_723-w-21st-st-77008",
    "phase_scope": "property",
    "historical_sales": [],
    "in_current_supply": false
  },
  {
    "address": "725 W 21st St, Houston, TX 77008",
    "MLS": "",
    "construction_phase": "complete",
    "current_market_status": "no market record",
    "prior_stored_tag": [
      "complete"
    ],
    "conflict_class": [
      "D"
    ],
    "pin": "pmt_725-w-21st-st-77008",
    "member": "pmt_725-w-21st-st-77008",
    "phase_scope": "property",
    "historical_sales": [],
    "in_current_supply": false
  },
  {
    "address": "729 W 21st St B, Houston, TX 77008",
    "MLS": "",
    "construction_phase": "complete",
    "current_market_status": "no market record",
    "prior_stored_tag": [
      "complete"
    ],
    "conflict_class": [
      "D"
    ],
    "pin": "pmt_729-w-21st-st-b-77008",
    "member": "pmt_729-w-21st-st-b-77008",
    "phase_scope": "property",
    "historical_sales": [],
    "in_current_supply": false
  },
  {
    "address": "1432 Alexander St, Houston, TX 77008",
    "MLS": "",
    "construction_phase": "complete",
    "current_market_status": "no market record",
    "prior_stored_tag": [
      "complete"
    ],
    "conflict_class": [
      "D"
    ],
    "pin": "pmt_1432-alexander-st-77008",
    "member": "pmt_1432-alexander-st-77008",
    "phase_scope": "paired project",
    "historical_sales": [],
    "in_current_supply": false
  },
  {
    "address": "1434 Alexander Street",
    "MLS": "61282363",
    "construction_phase": "complete",
    "current_market_status": "pending",
    "prior_stored_tag": [],
    "conflict_class": [
      "C"
    ],
    "pin": "pmt_1432-alexander-st-77008",
    "member": "act_1434-alexander-street",
    "phase_scope": "paired project",
    "historical_sales": [],
    "in_current_supply": false
  },
  {
    "address": "112 E 27th St A, Houston, TX 77008",
    "MLS": "",
    "construction_phase": "complete",
    "current_market_status": "no market record",
    "prior_stored_tag": [
      "complete"
    ],
    "conflict_class": [
      "D"
    ],
    "pin": "pmt_112-e-27th-st-a-77008",
    "member": "pmt_112-e-27th-st-a-77008",
    "phase_scope": "paired project",
    "historical_sales": [],
    "in_current_supply": false
  },
  {
    "address": "112 E 27th Street",
    "MLS": "34333707",
    "construction_phase": "complete",
    "current_market_status": "active",
    "prior_stored_tag": [],
    "conflict_class": [
      "B"
    ],
    "pin": "pmt_112-e-27th-st-a-77008",
    "member": "act_112-e-27th-street",
    "phase_scope": "paired project",
    "historical_sales": [],
    "in_current_supply": false
  },
  {
    "address": "729 W 21st St C, Houston, TX 77008",
    "MLS": "",
    "construction_phase": "complete",
    "current_market_status": "no market record",
    "prior_stored_tag": [
      "complete"
    ],
    "conflict_class": [
      "D"
    ],
    "pin": "pmt_729-w-21st-st-c-77008",
    "member": "pmt_729-w-21st-st-c-77008",
    "phase_scope": "property",
    "historical_sales": [],
    "in_current_supply": false
  },
  {
    "address": "1322 Lawrence Street",
    "MLS": "13912427",
    "construction_phase": "complete",
    "current_market_status": "active",
    "prior_stored_tag": [
      "complete",
      "active_split",
      "listed"
    ],
    "conflict_class": [
      "B"
    ],
    "pin": "act_1322-lawrence-street",
    "member": "act_1322-lawrence-street",
    "phase_scope": "paired project",
    "historical_sales": [],
    "in_current_supply": false
  },
  {
    "address": "1324 Lawrence Street",
    "MLS": "10396812",
    "construction_phase": "complete",
    "current_market_status": "sold",
    "prior_stored_tag": [],
    "conflict_class": [
      "A"
    ],
    "pin": "act_1322-lawrence-street",
    "member": "act_1324-lawrence-street",
    "phase_scope": "paired project",
    "historical_sales": [
      {
        "MLS": "10396812",
        "close_date": "2026-08-28",
        "close_price": 869900.0,
        "year_built": 2026.0,
        "evidence_scope": "new-construction closing"
      }
    ],
    "in_current_supply": false
  },
  {
    "address": "715 E 12th St, Houston, TX 77008",
    "MLS": "",
    "construction_phase": "complete",
    "current_market_status": "no market record",
    "prior_stored_tag": [
      "complete",
      "active_single"
    ],
    "conflict_class": [
      "D"
    ],
    "pin": "pmt_715-e-12th-st-77008",
    "member": "pmt_715-e-12th-st-77008",
    "phase_scope": "property",
    "historical_sales": [],
    "in_current_supply": false
  },
  {
    "address": "2811 Ave, Houston, TX 77009",
    "MLS": "",
    "construction_phase": "complete",
    "current_market_status": "no market record",
    "prior_stored_tag": [
      "complete"
    ],
    "conflict_class": [
      "D"
    ],
    "pin": "pmt_2811-ave-77009",
    "member": "pmt_2811-ave-77009",
    "phase_scope": "property",
    "historical_sales": [],
    "in_current_supply": false
  },
  {
    "address": "1301 Tabor St, Houston, TX 77009",
    "MLS": "",
    "construction_phase": "complete",
    "current_market_status": "no market record",
    "prior_stored_tag": [
      "complete"
    ],
    "conflict_class": [
      "D"
    ],
    "pin": "pmt_1301-tabor-st-77009",
    "member": "pmt_1301-tabor-st-77009",
    "phase_scope": "property",
    "historical_sales": [],
    "in_current_supply": false
  },
  {
    "address": "1107 E 24th St, Houston, TX 77009",
    "MLS": "",
    "construction_phase": "complete",
    "current_market_status": "no market record",
    "prior_stored_tag": [
      "complete"
    ],
    "conflict_class": [
      "D"
    ],
    "pin": "pmt_1107-e-24th-st-77009",
    "member": "pmt_1107-e-24th-st-77009",
    "phase_scope": "paired project",
    "historical_sales": [],
    "in_current_supply": false
  },
  {
    "address": "1109 E 24th St, Houston, TX 77009",
    "MLS": "",
    "construction_phase": "complete",
    "current_market_status": "no market record",
    "prior_stored_tag": [],
    "conflict_class": [
      "D"
    ],
    "pin": "pmt_1107-e-24th-st-77009",
    "member": "pmt_1109-e-24th-st-77009",
    "phase_scope": "paired project",
    "historical_sales": [],
    "in_current_supply": false
  },
  {
    "address": "826 E 27th St, Houston, TX 77009",
    "MLS": "",
    "construction_phase": "complete",
    "current_market_status": "no market record",
    "prior_stored_tag": [
      "complete"
    ],
    "conflict_class": [
      "D"
    ],
    "pin": "pmt_826-e-27th-st-77009",
    "member": "pmt_826-e-27th-st-77009",
    "phase_scope": "property",
    "historical_sales": [],
    "in_current_supply": false
  },
  {
    "address": "409 Walton St A, Houston, TX 77009",
    "MLS": "",
    "construction_phase": "complete",
    "current_market_status": "no market record",
    "prior_stored_tag": [
      "complete"
    ],
    "conflict_class": [
      "D"
    ],
    "pin": "pmt_409-walton-st-a-77009",
    "member": "pmt_409-walton-st-a-77009",
    "phase_scope": "paired project",
    "historical_sales": [],
    "in_current_supply": false
  },
  {
    "address": "409 Walton Street Unit#B",
    "MLS": "54747421",
    "construction_phase": "complete",
    "current_market_status": "active",
    "prior_stored_tag": [],
    "conflict_class": [
      "B"
    ],
    "pin": "pmt_409-walton-st-a-77009",
    "member": "act_409-walton-street-unit-b",
    "phase_scope": "paired project",
    "historical_sales": [],
    "in_current_supply": false
  },
  {
    "address": "931 Merrill St, Houston, TX 77009",
    "MLS": "",
    "construction_phase": "complete",
    "current_market_status": "no market record",
    "prior_stored_tag": [
      "complete"
    ],
    "conflict_class": [
      "D"
    ],
    "pin": "pmt_931-merrill-st-77009",
    "member": "pmt_931-merrill-st-77009",
    "phase_scope": "property",
    "historical_sales": [],
    "in_current_supply": false
  },
  {
    "address": "902 E 25TH Street",
    "MLS": "32496070",
    "construction_phase": "complete",
    "current_market_status": "active",
    "prior_stored_tag": [
      "complete",
      "active_single",
      "listed"
    ],
    "conflict_class": [
      "B"
    ],
    "pin": "act_902-e-25",
    "member": "act_902-e-25",
    "phase_scope": "property",
    "historical_sales": [],
    "in_current_supply": false
  },
  {
    "address": "122 E 4th Street",
    "MLS": "90552057",
    "construction_phase": "complete",
    "current_market_status": "active",
    "prior_stored_tag": [
      "complete",
      "active_split",
      "listed"
    ],
    "conflict_class": [
      "B"
    ],
    "pin": "act_122-e-4",
    "member": "act_122-e-4",
    "phase_scope": "property",
    "historical_sales": [],
    "in_current_supply": false
  },
  {
    "address": "826 Ralfallen Street",
    "MLS": "88173016",
    "construction_phase": "complete",
    "current_market_status": "sold",
    "prior_stored_tag": [
      "complete",
      "pending",
      "listed"
    ],
    "conflict_class": [
      "A",
      "F"
    ],
    "pin": "act_826-ralfallen",
    "member": "act_826-ralfallen",
    "phase_scope": "property",
    "historical_sales": [
      {
        "MLS": "88173016",
        "close_date": "2026-08-26",
        "close_price": 1655000.0,
        "year_built": 2026.0,
        "evidence_scope": "new-construction closing"
      }
    ],
    "in_current_supply": false
  },
  {
    "address": "609 E 25th Street",
    "MLS": "53672595",
    "construction_phase": "complete",
    "current_market_status": "active",
    "prior_stored_tag": [
      "complete",
      "active_single",
      "listed"
    ],
    "conflict_class": [
      "B"
    ],
    "pin": "act_609-e-25",
    "member": "act_609-e-25",
    "phase_scope": "property",
    "historical_sales": [],
    "in_current_supply": false
  },
  {
    "address": "212 E 24th Street",
    "MLS": "29120139",
    "construction_phase": "complete",
    "current_market_status": "active",
    "prior_stored_tag": [
      "complete",
      "active_single",
      "listed"
    ],
    "conflict_class": [
      "B"
    ],
    "pin": "act_212-e-24",
    "member": "act_212-e-24",
    "phase_scope": "property",
    "historical_sales": [],
    "in_current_supply": false
  },
  {
    "address": "1116 Highland Street",
    "MLS": "42468659",
    "construction_phase": "complete",
    "current_market_status": "pending",
    "prior_stored_tag": [
      "complete",
      "pending",
      "active_single",
      "listed"
    ],
    "conflict_class": [
      "C",
      "F"
    ],
    "pin": "act_1116-highland",
    "member": "act_1116-highland",
    "phase_scope": "property",
    "historical_sales": [],
    "in_current_supply": false
  },
  {
    "address": "715 Merrill Street",
    "MLS": "88557637",
    "construction_phase": "complete",
    "current_market_status": "active",
    "prior_stored_tag": [
      "complete",
      "active_single",
      "listed"
    ],
    "conflict_class": [
      "B"
    ],
    "pin": "act_715-merrill",
    "member": "act_715-merrill",
    "phase_scope": "property",
    "historical_sales": [],
    "in_current_supply": false
  },
  {
    "address": "1126 E 7th 1/2 Street",
    "MLS": "95336494",
    "construction_phase": "complete",
    "current_market_status": "pending",
    "prior_stored_tag": [
      "complete",
      "off_market_single",
      "listed"
    ],
    "conflict_class": [
      "C",
      "F"
    ],
    "pin": "act_1126-e-7-12",
    "member": "act_1126-e-7-12",
    "phase_scope": "property",
    "historical_sales": [],
    "in_current_supply": false
  },
  {
    "address": "1208 E 26th Street Unit#A",
    "MLS": "58591599",
    "construction_phase": "complete",
    "current_market_status": "pending",
    "prior_stored_tag": [
      "complete",
      "pending",
      "active_split",
      "listed"
    ],
    "conflict_class": [
      "C",
      "F"
    ],
    "pin": "act_1208-e-26th-street-unit-a",
    "member": "act_1208-e-26th-street-unit-a",
    "phase_scope": "property",
    "historical_sales": [],
    "in_current_supply": false
  },
  {
    "address": "1303 Cordell Street Unit#B",
    "MLS": "64036585",
    "construction_phase": "complete",
    "current_market_status": "active",
    "prior_stored_tag": [
      "complete",
      "active_split",
      "listed"
    ],
    "conflict_class": [
      "B"
    ],
    "pin": "act_1303-cordell-street-unit-b",
    "member": "act_1303-cordell-street-unit-b",
    "phase_scope": "property",
    "historical_sales": [],
    "in_current_supply": false
  },
  {
    "address": "835 W 25th Street",
    "MLS": "87747647",
    "construction_phase": "complete",
    "current_market_status": "active",
    "prior_stored_tag": [
      "complete",
      "active_split",
      "listed"
    ],
    "conflict_class": [
      "B"
    ],
    "pin": "act_835-w-25th-street",
    "member": "act_835-w-25th-street",
    "phase_scope": "paired project",
    "historical_sales": [],
    "in_current_supply": false
  },
  {
    "address": "833 W 25th Street",
    "MLS": "",
    "construction_phase": "complete",
    "current_market_status": "no market record",
    "prior_stored_tag": [],
    "conflict_class": [
      "D"
    ],
    "pin": "act_835-w-25th-street",
    "member": "act_833-w-25th-street",
    "phase_scope": "paired project",
    "historical_sales": [],
    "in_current_supply": false
  },
  {
    "address": "609 W 27th Street",
    "MLS": "98658584",
    "construction_phase": "complete",
    "current_market_status": "active",
    "prior_stored_tag": [
      "complete",
      "active_split",
      "listed"
    ],
    "conflict_class": [
      "B"
    ],
    "pin": "act_609-w-27th-street",
    "member": "act_609-w-27th-street",
    "phase_scope": "paired project",
    "historical_sales": [],
    "in_current_supply": false
  },
  {
    "address": "607 W 27th St, Houston, TX 77008",
    "MLS": "",
    "construction_phase": "complete",
    "current_market_status": "no market record",
    "prior_stored_tag": [],
    "conflict_class": [
      "D"
    ],
    "pin": "act_609-w-27th-street",
    "member": "pmt_607-w-27th-st-77008",
    "phase_scope": "paired project",
    "historical_sales": [],
    "in_current_supply": false
  },
  {
    "address": "335 Harvard Street",
    "MLS": "65070979",
    "construction_phase": "complete",
    "current_market_status": "active",
    "prior_stored_tag": [
      "complete",
      "active_split",
      "listed"
    ],
    "conflict_class": [
      "B"
    ],
    "pin": "act_335-harvard-street",
    "member": "act_335-harvard-street",
    "phase_scope": "property",
    "historical_sales": [],
    "in_current_supply": false
  },
  {
    "address": "1602 Turnpike Rd, Houston, TX 77008",
    "MLS": "",
    "construction_phase": "complete",
    "current_market_status": "no market record",
    "prior_stored_tag": [
      "complete",
      "needs_clarification"
    ],
    "conflict_class": [
      "D"
    ],
    "pin": "pmt_1602-turnpike-rd-77008",
    "member": "pmt_1602-turnpike-rd-77008",
    "phase_scope": "property",
    "historical_sales": [],
    "in_current_supply": false
  },
  {
    "address": "Unidentified represented home 1 at 122 E 4th Street",
    "MLS": "",
    "construction_phase": "complete",
    "current_market_status": "no market record",
    "prior_stored_tag": [],
    "conflict_class": [
      "D"
    ],
    "pin": "act_122-e-4",
    "member": null,
    "inferred_weight": true
  },
  {
    "address": "Unidentified represented home 1 at 1208 E 26th Street Unit#A",
    "MLS": "",
    "construction_phase": "complete",
    "current_market_status": "no market record",
    "prior_stored_tag": [],
    "conflict_class": [
      "D"
    ],
    "pin": "act_1208-e-26th-street-unit-a",
    "member": null,
    "inferred_weight": true
  },
  {
    "address": "Unidentified represented home 1 at 335 Harvard Street",
    "MLS": "",
    "construction_phase": "complete",
    "current_market_status": "no market record",
    "prior_stored_tag": [],
    "conflict_class": [
      "D"
    ],
    "pin": "act_335-harvard-street",
    "member": null,
    "inferred_weight": true
  }
]

```
## Under-construction active phase distribution
```json
{
  "mep_finals": 7,
  "interior": 13,
  "insulation": 1,
  "mep_roughs": 1,
  "framing": 2,
  "exterior": 1,
  "foundation": 1
}

```
## Historical resale matches — not current-build sold evidence
```json
[
  {
    "address": "310 E 25th St, Houston, Tx 77008",
    "MLS": "88338062",
    "construction_phase": "interior",
    "current_market_status": "no market record",
    "prior_stored_tag": [
      "interior",
      "needs_clarification"
    ],
    "conflict_class": [],
    "pin": "2131318733",
    "member": "2131318733",
    "phase_scope": "property",
    "historical_sales": [
      {
        "MLS": "88338062",
        "close_date": "2025-12-16",
        "close_price": 615000,
        "year_built": 1920,
        "evidence_scope": "prior-structure resale; not current build sold"
      }
    ],
    "in_current_supply": true
  },
  {
    "address": "2052 Columbia St, Houston, TX 77008",
    "MLS": "92049997",
    "construction_phase": "interior",
    "current_market_status": "no market record",
    "prior_stored_tag": [
      "interior"
    ],
    "conflict_class": [],
    "pin": "pmt_2052-columbia-st-77008",
    "member": "pmt_2052-columbia-st-77008",
    "phase_scope": "property",
    "historical_sales": [
      {
        "MLS": "92049997",
        "close_date": "2025-09-30",
        "close_price": 750000,
        "year_built": 1941,
        "evidence_scope": "prior-structure resale; not current build sold"
      }
    ],
    "in_current_supply": true
  }
]

```
## Review gate
DEFER: only 3/48 sold rows have a construction phase; 34 have no tracked pin. No cross-market exports supplied. Resolve construction linkage before Phase 4.

Supply scenario: 144 − 0 (A already excluded) − 0 (C already excluded) + 13 (B) + 30 (D) = 187. D availability remains unverified. Under-construction pending/sold members are listed separately above.
