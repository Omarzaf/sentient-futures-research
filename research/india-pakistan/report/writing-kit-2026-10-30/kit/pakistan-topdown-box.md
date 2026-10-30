# Pakistan: conventional-value scale check

**Conditional scale comparison. It shows how large the transferred Pakistan scenarios are relative to conventional poultry and milk value. It does not estimate alternative-protein sales or an observed market share.**

Conventional value multiplies quantity by price and converts at PKR 281.143001173202/USD, the retained 2025 annual-average rate. Poultry uses [OECD-FAO consumption quantities](https://sdmx.oecd.org/public/rest/data/OECD.TAD.ATM,DSD_AGR@DF_OUTLOOK_2025_2034,1.1/IND+PAK.A....?startPeriod=2010&endPeriod=2034&dimensionAtObservation=AllDimensions), ready-to-cook weight, from the outlook published in 2025; the 2034 quantity is carried unchanged into 2035. Milk uses [FAOSTAT](https://www.fao.org/faostat/en/#data/FBS) 2023 food availability for milk excluding butter, held fixed.

Prices come from the [PBS issue of 24 December 2025](https://www.pbs.gov.pk/wp-content/uploads/2020/07/Annex_24.12.2025.pdf), page 3, whose national averages cover an urban-market sample: PKR 424.89/kg of live broiler and PKR 203.51/litre of fresh milk. The live-bird price is divided by an assumed dressed/live yield of 0.70. The milk price is converted with the [FAO INFOODS](https://www.fao.org/fileadmin/templates/food_composition/documents/density_DB_v2_0_01.pdf) whole-liquid-milk density of 1.031 kg/litre. Neither conversion is validated for this national basket.

**Central conversion assumptions; values in US dollars at conditional 2025 reference prices.**

| Comparison year | Conventional poultry and milk value, USD billion | Transfer 10th to 90th percentile, USD million | Transfer range as a share of conventional value |
|---|---:|---:|---:|
| 2026 | 27.9 | 1.47 to 6.62 | 0.005% to 0.024% |
| 2030 | 28.4 | 2.28 to 13.68 | 0.008% to 0.048% |
| 2035 | 28.9 | 3.59 to 36.10 | 0.012% to 0.125% |

Across all 18 combinations of quantity source and price profile, the 2035 share spans 0.003% to 0.137%. The alternatives include fiscal-year 2024 to 2025 Economic Survey quantities and Naheed premium-outlet prices deflated by the 7.1% CPI projection. Higher conventional values give lower shares.

The requested capture shares of 0.05%, 0.1% and 0.5% each exceed the 2026 share under all 18 profiles. Across the full 162-row grid, 139 rows exceed the transfer's 90th percentile and none falls below its 10th percentile. At 0.5%, the milk component alone is USD 112.70 million in 2026, over 17 times the transfer's 90th percentile.

This is a scale check because the baskets differ. Conventional value includes nonmarketed and loose milk at an urban fresh-milk price, while the retained alternative-protein price evidence comes from formal retail. FAOSTAT's milk item excludes the milk equivalent of butter and ghee, listed separately at 1,268 thousand tonnes of food; the Economic Survey's milk for human consumption is 58,300 thousand tonnes against FAOSTAT's 32,104. The live-bird price values poultry below retail. The transfer's basket includes plant-based meat, dairy and eggs; the conventional basket covers poultry and milk only. No retained source gives an observed alternative-protein share of conventional value in either country, so the requested shares remain unanchored.

**AI draft, replace:** We compare Pakistan's transferred scenarios with the value of conventional poultry and milk. Under central conversion assumptions, the scenarios equal about 0.005% to 0.024% of that value in 2026 and 0.012% to 0.125% in 2035. These shares describe scale only. The conventional value includes milk that never passes through formal retail, and its price conversions are assumptions. With no observed share to compare against, the result supports measuring a Pakistan sales baseline before any market share is assumed.

[Full grid](../../../build/pakistan-topdown/pakistan_topdown.csv); [assumptions and reproduction](../../../data/pakistan-topdown/README.md).
