# Source-defined exploratory grouping. Only aggregate diagnostics leave memory.
suppressPackageStartupMessages(library(data.table))
setDTthreads(2L)
setNumericRounding(0L) # Exact double ties, without approximate numeric grouping.

main <- function() {
  root <- normalizePath(getwd())
  base <- file.path(root, "scripts/diet/m3_microdata_profile")
  out <- file.path(base, "grouping_exploration_20261013")
  archive <- file.path(root, "data/raw/diet/m3-reassessment-2026-10-13/pbs-stata-2024-25.zip")
  stopifnot(file.exists(file.path(out, "SPEC.json")))
  scratch <- tempfile("pbs-grouping-read-only-")
  dir.create(scratch)
  on.exit(unlink(scratch, recursive = TRUE), add = TRUE)
  read_table <- function(name) {
    member <- paste0("Stata data/", name, ".dta")
    file <- unzip(archive, files = member, exdir = scratch)
    stopifnot(length(file) == 1L)
    as.data.table(foreign::read.dta(file, convert.dates = FALSE, convert.factors = FALSE,
                                  warn.missing.labels = FALSE))
  }
  save_csv <- function(value, name) {
    stopifnot(!any(c("hhcode", "prcode", "hhno", "idc") %in% names(value)))
    value <- copy(value)
    if ("households" %in% names(value)) {
      value[, measures_suppressed_small_cell := households > 0 & households < 5]
      measures <- grep("weight|share|rupees|factor|mean|median", names(value), value = TRUE)
      if (length(measures)) value[measures_suppressed_small_cell == TRUE, (measures) := NA_real_]
    }
    fwrite(value, file.path(out, name), na = "")
  }
  save_json <- function(value, name) {
    jsonlite::write_json(value, file.path(out, name), pretty = TRUE, auto_unbox = TRUE,
                         na = "null", null = "null", digits = NA)
  }
  info <- read_table("section_info")
  roster <- read_table("plist_roster")
  weights <- read_table("weight")
  food <- read_table("sec_6a_consum_exp")
  stopifnot(!anyDuplicated(info$hhcode), !anyDuplicated(roster, by = c("hhcode", "idc")),
            !anyDuplicated(weights$prcode), !anyDuplicated(food, by = c("hhcode", "itc")),
            setequal(info$hhcode, unique(food$hhcode)), setequal(info$hhcode, unique(roster$hhcode)))
  members <- roster[, .(members = sum(s1aq10 == 1, na.rm = TRUE),
                         membership_unknown = sum(is.na(s1aq10))), by = hhcode]
  hh <- merge(info[, .(hhcode, prcode, province, region, enum_year, enum_month)], members,
                 by = "hhcode", sort = FALSE, allow.cartesian = FALSE)
  hh <- merge(hh, weights, by = "prcode", all.x = TRUE, sort = FALSE, allow.cartesian = FALSE)
  stopifnot(nrow(hh) == 30123L, all(hh$members > 0), all(hh$weight > 0), !anyNA(hh$weight))
  hh[, population_weight := weight * members]
  hh[, period := sprintf("%04d-%02d", enum_year, enum_month)]
  form <- fread(file.path(base, "form_item_part_mapping.csv"))
  stopifnot(nrow(form) == 285L, !anyDuplicated(form$itc),
            setequal(unique(food$itc), c(form$itc, 1000L, 2000L, 4000L, 5000L, 6000L)))
  factors <- data.table(part = c("A", "B", "C", "D", "E"),
                        subtotal_code = c(1000L, 2000L, 4000L, 5000L, 6000L),
                        monthly_factor = c(26/12, 1, 1, 1/12, 1/12))
  detail <- merge(food[, .(hhcode, itc, v1, v2, v3, v4)], form[, .(itc, part)],
                     by = "itc", all = FALSE, sort = FALSE, allow.cartesian = FALSE)
  detail <- merge(detail, factors[, .(part, monthly_factor)], by = "part",
                     all.x = TRUE, sort = FALSE, allow.cartesian = FALSE)
  detail[, known_channels := rowSums(!is.na(.SD)), .SDcols = paste0("v", 1:4)]
  detail[, negative_channels := rowSums(.SD < 0, na.rm = TRUE), .SDcols = paste0("v", 1:4)]
  detail[, observed_value := rowSums(.SD, na.rm = TRUE), .SDcols = paste0("v", 1:4)]
  detail[, observed_monthly := observed_value * monthly_factor]
  excluded <- c(42104L, 72401L, 127001L, 127007L, 123102L)
  stopifnot(all(excluded %in% form$itc))
  detail[, excluded_scope := itc %in% excluded]
  item_quality <- detail[, .(records = .N, households = uniqueN(hhcode),
                all_value_channels_missing = sum(known_channels == 0),
                some_value_channels_missing = sum(known_channels < 4),
                negative_value_records = sum(negative_channels > 0),
                observed_zero_value_records = sum(observed_value == 0 & known_channels > 0)), by = part]
  save_csv(item_quality[order(part)], "record_quality_by_part.csv")
  part_detail <- detail[, .(detail_records = .N, all_missing_records = sum(known_channels == 0),
                  negative_records = sum(negative_channels > 0)), by = .(hhcode, part)]
  subtotal <- merge(food[itc %in% factors$subtotal_code, .(hhcode, subtotal_code = itc)],
                        factors[, .(part, subtotal_code)], by = "subtotal_code", sort = FALSE,
                        allow.cartesian = FALSE)[, .(hhcode, part, subtotal_present = TRUE)]
  grid <- hh[, .(part = factors$part), by = .(hhcode, province, region, weight, population_weight)]
  grid <- merge(grid, part_detail, by = c("hhcode", "part"), all.x = TRUE, sort = FALSE, allow.cartesian = FALSE)
  grid <- merge(grid, subtotal, by = c("hhcode", "part"), all.x = TRUE, sort = FALSE, allow.cartesian = FALSE)
  grid[, coverage := fifelse(is.na(detail_records), fifelse(is.na(subtotal_present),
          "no_detail_or_subtotal_record", "subtotal_without_detail"),
          fifelse(is.na(subtotal_present), "detail_without_subtotal", "detail_and_subtotal"))]
  coverage <- grid[, .(households = .N, sum_household_weight = sum(weight),
                       sum_population_weight = sum(population_weight)), by = .(part, coverage)]
  save_csv(coverage[order(part, coverage)], "part_presence_coverage.csv")
  coverage_geography <- grid[, .(households = .N, sum_population_weight = sum(population_weight)),
                                by = .(province, region, part, coverage)]
  save_csv(coverage_geography[order(province, region, part, coverage)], "part_presence_by_geography.csv")
  hh_presence <- grid[, .(absent_detail_parts = sum(is.na(detail_records)),
                detail_without_subtotal_parts = sum(coverage == "detail_without_subtotal")), by = hhcode]
  observed <- detail[, .(nominal = sum(observed_monthly),
              scope_excluded = sum(observed_monthly[!excluded_scope]),
              known_values = sum(known_channels), all_missing_records = sum(known_channels == 0),
              negative_records = sum(negative_channels > 0)), by = hhcode]
  hh <- merge(hh, observed, by = "hhcode", all.x = TRUE, sort = FALSE, allow.cartesian = FALSE)
  hh <- merge(hh, hh_presence, by = "hhcode", all.x = TRUE, sort = FALSE, allow.cartesian = FALSE)
  cpi <- fread(file.path(root, "scripts/diet/m3_price_inputs/overall_cpi/overall_cpi.csv"))[
      residence %in% c("rural", "urban") & period >= "2024-10" & period <= "2025-06"]
  stopifnot(nrow(cpi) == 18L, !anyDuplicated(cpi, by = c("residence", "period")), all(cpi$value > 0))
  cpi[, residence_mean_cpi := mean(value), by = residence]
  cpi[, temporal_factor := value / residence_mean_cpi]
  cpi[, region := ifelse(residence == "rural", 1L, 2L)]
  save_csv(cpi[, .(residence, period, overall_cpi = value, residence_mean_cpi, temporal_factor,
                   source_id, pdf_page, raw_sha256)][order(residence, period)], "temporal_cpi_factors.csv")
  hh <- merge(hh, cpi[, .(region, period, temporal_factor)], by = c("region", "period"),
                 all.x = TRUE, sort = FALSE, allow.cartesian = FALSE)
  stopifnot(!anyNA(hh$temporal_factor), all(hh$temporal_factor > 0))
  hh[, cpi_temporal := nominal / temporal_factor]
  assign_group <- function(amount) {
    work <- hh[, .(hhcode, population_weight, per_member = get(amount) / members,
                    known_values, weight, province, region)]
    work[, eligible := !is.na(per_member) & per_member > 0 & known_values > 0]
    ties <- work[eligible == TRUE, .(tie_population_weight = sum(population_weight),
                                    tie_households = .N), by = per_member][order(per_member)]
    stopifnot(nrow(ties) > 5L)
    ties[, cumulative_population_weight := cumsum(tie_population_weight)]
    total <- sum(ties$tie_population_weight)
    ties[, midpoint := (cumulative_population_weight - 0.5 * tie_population_weight) / total]
    ties[, quintile := pmin(5L, pmax(1L, as.integer(floor(midpoint * 5)) + 1L))]
    stopifnot(all(diff(ties$quintile) >= 0), setequal(ties$quintile, 1:5))
    work <- merge(work, ties[, .(per_member, quintile)], by = "per_member", all.x = TRUE,
                     sort = FALSE, allow.cartesian = FALSE)
    stopifnot(nrow(work) == nrow(hh), !anyDuplicated(work$hhcode),
              !anyNA(work[eligible == TRUE, quintile]),
              work[eligible == TRUE, uniqueN(quintile), by = per_member][, all(V1 == 1L)])
    bounds <- ties[, .(households = sum(tie_households), distinct_value_ties = .N,
          population_weight = sum(tie_population_weight),
          lower_observed_rupees_per_member = min(per_member),
          upper_observed_rupees_per_member = max(per_member)), by = quintile]
    bounds[, scenario := amount]
    bounds[, population_share := population_weight / total]
    stopifnot(abs(sum(bounds$population_share) - 1) < 1e-12,
              sum(bounds$households) == sum(work$eligible),
              max(abs(bounds$population_share - 0.2)) <= max(ties$tie_population_weight) / total)
    summary <- list(scenario = amount, eligible_households = sum(work$eligible),
           ineligible_households = sum(!work$eligible), distinct_exact_values = nrow(ties),
           tied_value_groups = sum(ties$tie_households > 1),
           households_in_tied_groups = sum(ties$tie_households[ties$tie_households > 1]),
           maximum_tie_population_share = max(ties$tie_population_weight) / total,
           same_values_share_group = TRUE, groups_are_official = FALSE)
    list(work = work, bounds = bounds, summary = summary)
  }
  scenarios <- lapply(c("nominal", "scope_excluded", "cpi_temporal"), assign_group)
  names(scenarios) <- c("nominal", "scope_excluded", "cpi_temporal")
  save_csv(rbindlist(lapply(scenarios, function(x) x$bounds))[order(scenario, quintile)], "group_boundaries_and_population_shares.csv")
  group_geo <- rbindlist(lapply(names(scenarios), function(name) {
    scenarios[[name]]$work[, .(scenario = name, households = .N,
       sum_household_weight = sum(weight), sum_population_weight = sum(population_weight)),
       by = .(province, region, quintile)]
  }))
  save_csv(group_geo[order(scenario, province, region, quintile)], "group_coverage_by_geography.csv")
  baseline <- scenarios$nominal$work[, .(hhcode, baseline_group = quintile)]
  transitions <- list(); changes <- list()
  for (scenario in c("scope_excluded", "cpi_temporal")) {
    paired <- merge(scenarios[[scenario]]$work, baseline, by = "hhcode", sort = FALSE, allow.cartesian = FALSE)
    paired[, both_eligible := !is.na(quintile) & !is.na(baseline_group)]
    paired[, changed := both_eligible & quintile != baseline_group]
    transitions[[scenario]] <- paired[, .(scenario = scenario, households = .N,
           sum_population_weight = sum(population_weight)), by = .(baseline_group, alternate_group = quintile)]
    changes[[scenario]] <- paired[, .(scenario = scenario, households = .N,
           paired_eligible_households = sum(both_eligible), changed_households = sum(changed),
           household_changed_share = mean(changed[both_eligible]),
           population_changed_share = sum(population_weight[changed]) / sum(population_weight[both_eligible]))]
  }
  save_csv(rbindlist(transitions)[order(scenario, baseline_group, alternate_group)], "sensitivity_transition_counts.csv")
  save_csv(rbindlist(changes), "sensitivity_membership_changes.csv")
  baseline_coverage <- merge(hh[, .(hhcode, absent_detail_parts, detail_without_subtotal_parts,
                         all_missing_records, negative_records, weight, population_weight)],
                            baseline, by = "hhcode", sort = FALSE, allow.cartesian = FALSE)
  save_csv(baseline_coverage[, .(households = .N, sum_population_weight = sum(population_weight)),
       by = .(baseline_group, absent_detail_parts, detail_without_subtotal_parts,
               all_missing_records, negative_records)][order(baseline_group, absent_detail_parts)],
       "baseline_missingness_coverage.csv")
  monetary <- rbindlist(lapply(c("nominal", "scope_excluded", "cpi_temporal"), function(scenario) {
    hh[, .(scenario = scenario, households = .N,
         weighted_observed_monthly_mean_rupees = sum(get(scenario) * weight) / sum(weight),
         weighted_observed_per_member_mean_rupees = sum(get(scenario) * weight) / sum(population_weight))]
  }))
  save_csv(monetary, "scenario_observed_amount_diagnostic.csv")
  save_json(list(status = "EXPLORATORY_GROUPING_ONLY_NOT_ACCEPTED_NUTRIENT_GROUPS",
      households = nrow(hh), detail_records = nrow(detail), source_detail_codes = uniqueN(detail$itc),
      records_with_all_value_channels_missing = sum(detail$known_channels == 0),
      records_with_any_negative_value = sum(detail$negative_channels > 0),
      households_with_any_negative_value = sum(hh$negative_records > 0),
      households_with_any_absent_detail_part = sum(hh$absent_detail_parts > 0),
      households_with_unknown_member_flag = sum(hh$membership_unknown > 0),
      cpi_unmatched_households = sum(is.na(hh$temporal_factor)),
      numeric_rounding_bytes = getNumericRounding(),
      runtime = list(R = as.character(getRversion()),
                     data_table = as.character(packageVersion("data.table")),
                     foreign = as.character(packageVersion("foreign")),
                     jsonlite = as.character(packageVersion("jsonlite"))),
      scenarios = lapply(scenarios, function(x) x$summary),
      source_records_or_identifiers_exported = 0, nutrition_values_computed = 0,
      missing_amounts_imputed = 0, source_values_winsorized = 0), "grouping_checks.json")
  cat("PASS: exploratory grouping and coverage complete; aggregate-only exports; no nutrition or accepted official groups.\n")
}
main()
