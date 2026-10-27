# T3 model repair

Added two sensitivities and a US comparison row function accepting a supplied year and value per person. No US forecasts invented. Seed 20261015, 10,000 draws and all 104 original values are unchanged. Added two report sentences and three claims in both mirrors.

Values below are p10, p50, p90, in million dollars at constant 2025 prices.

```csv
variant,country,year,p10,p50,p90
drift,India,2026,64.321822,74.379569,85.934216
drift,India,2030,89.628362,119.642204,159.144864
drift,India,2035,134.658168,215.060659,341.253412
drift,Pakistan,2026,1.206835,2.966551,4.990994
drift,Pakistan,2030,1.637255,4.036835,7.079927
drift,Pakistan,2035,2.382182,5.964900,11.690860
drop_urban_animal,Pakistan,2035,2.575709,8.318219,25.341349
```

Adjusted high drift: 5.977774% yearly.

Commands: `python3 research/india-pakistan/tools/build_altprotein_proxy.py`; supplied `run_tests.py research/india-pakistan/tests/test_altprotein_proxy.py` (10 passed); `node tools/build-library.mjs` (exit 0); `node tools/verify.mjs` (failed).

Verification needs renewed export bindings and import provenance outside T3 ownership; other workers' joint-report links also fail. These files were preserved. Claim recomputation used `python3.12 research/india-pakistan/tools/verify_edition.py --only C1`; system Python 3.9 lacks datetime.UTC.

Independent calculation matched all 21 variant quantiles. Repeated model output was byte-identical. Checks C1, C2 and C3 passed: 761 claims, 565 prose bindings and 39 charts/tables.

Two library builds matched all 462 files. Moderator: model PASS, integration NEEDS_FIXES. Retro: paired draws worked; report edits need export/provenance ownership in the integrating task.
