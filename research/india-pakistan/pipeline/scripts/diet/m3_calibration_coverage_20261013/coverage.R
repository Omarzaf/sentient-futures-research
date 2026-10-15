# Exploratory source-bound coverage only. No unit costs or imputed intake.
suppressPackageStartupMessages(library(data.table))
setDTthreads(2L)
setNumericRounding(0L)

daily_amount <- function(amount, period_days) {
  stopifnot(all(period_days %in% c(14L, 30L)),
            length(period_days) %in% c(1L, length(amount)))
  amount / period_days
}

classify_channels <- function(work) {
  work[, disposition := "missing_value"]
  work[!is.na(v) & v <= 0, disposition := "known_nonpositive_value_exception"]
  work[v_positive & source_scope == "AT_HOME", disposition := "K_at_home"]
  work[v_positive & source_scope == "PREPARED", disposition := "K_prepared"]
  work[v_positive & role == "G" & known_zero == TRUE, disposition := "G_known_zero"]
  work[v_positive & q_positive & role == "G" & known_zero == FALSE, disposition := "G_positive"]
  work[v_positive & role == "DIRECT_ZERO_OUTSIDE_G", disposition := "direct_zero_prepared"]
  work[role == "SERVICE", disposition := "service_excluded"]
  work
}

channel_negative_controls <- function() {
  # Synthetic routing tests only. Values are not survey observations or estimates.
  test <- data.table(case = c("valid_pair", "quantity_only_channel1", "value_only_channel2",
      "known_zero_no_quantity", "prepared_water", "milling", "negative_quantity",
      "negative_value", "missing_pair", "unresolved_food", "prepared_food"),
    q = c(2, 2, NA, NA, NA, NA, -1, 2, NA, 2, NA),
    v = c(3, NA, 3, 3, 3, 3, 3, -1, NA, 3, 3),
    role = c("G", "G", "G", "G", "DIRECT_ZERO_OUTSIDE_G", "SERVICE", "G", "G", "G", "K", "K"),
    source_scope = c("AT_HOME", "AT_HOME", "AT_HOME", "AT_HOME", "PREPARED", "SERVICE",
                     "AT_HOME", "AT_HOME", "AT_HOME", "AT_HOME", "PREPARED"),
    known_zero = c(FALSE, FALSE, FALSE, TRUE, TRUE, FALSE, FALSE, FALSE, FALSE, FALSE, FALSE))
  test[, `:=`(q_positive = !is.na(q) & q > 0, v_positive = !is.na(v) & v > 0)]
  test <- classify_channels(test)
  expected <- c("G_positive", "missing_value", "K_at_home", "G_known_zero", "direct_zero_prepared",
                "service_excluded", "K_at_home", "known_nonpositive_value_exception", "missing_value",
                "K_at_home", "K_prepared")
  stopifnot(identical(test$disposition, expected),
            !any(test[case %in% c("quantity_only_channel1", "value_only_channel2"), disposition] == "G_positive"))
  stopifnot(identical(daily_amount(c(14, 30), c(14L, 30L)), c(1, 1)),
            identical(daily_amount(c(140, 300), c(14L, 30L)), c(10, 10)),
            daily_amount(14, 30L) != daily_amount(14, 14L))
  list(status = "PASS", synthetic_routing_cases = nrow(test), daily_period_controls = 3L,
       no_synthetic_values_in_empirical_outputs = TRUE)
}

main <- function() {
  root <- normalizePath(getwd())
  out <- file.path(root, "scripts/diet/m3_calibration_coverage_20261013")
  profile <- file.path(root, "scripts/diet/m3_microdata_profile")
  frozen <- file.path(profile, "grouping_exploration_20261013")
  factors_dir <- file.path(root, "scripts/diet/m3_calibration_spec")
  stopifnot(file.exists(file.path(out, "input_bindings.json")))
  negative_controls <- channel_negative_controls()
  scratch <- tempfile("pbs-calibration-coverage-")
  dir.create(scratch)
  on.exit(unlink(scratch, recursive = TRUE), add = TRUE)
  read_table <- function(name) {
    archive <- file.path(root, "data/raw/diet/m3-reassessment-2026-10-13/pbs-stata-2024-25.zip")
    file <- unzip(archive, files = paste0("Stata data/", name, ".dta"), exdir = scratch)
    stopifnot(length(file) == 1L)
    as.data.table(foreign::read.dta(file, convert.dates = FALSE, convert.factors = FALSE,
                                  warn.missing.labels = FALSE))
  }
  save_csv <- function(x, name, contributing = "households") {
    x <- copy(x)
    stopifnot(!any(c("hhcode", "prcode", "hhno", "idc") %in% names(x)))
    if (contributing %in% names(x)) {
      x[, measures_suppressed_small_cell := get(contributing) > 0 & get(contributing) < 5]
      measure <- grep("weight|share|rupees|mean|median|ratio|factor", names(x), value = TRUE)
      measure <- setdiff(measure, "factor_scenario")
      if (length(measure)) x[measures_suppressed_small_cell == TRUE, (measure) := NA_real_]
    }
    fwrite(x, file.path(out, name), na = "")
  }
  save_json <- function(x, name) {
    jsonlite::write_json(x, file.path(out, name), pretty = TRUE, auto_unbox = TRUE,
                        na = "null", null = "null", digits = NA)
  }
  close_enough <- function(a, b) all(abs(a - b) <= 1e-7 + 1e-12 * pmax(abs(a), abs(b)))
  info <- read_table("section_info")
  roster <- read_table("plist_roster")
  weights <- read_table("weight")
  consumed <- read_table("sec_6a_consum_exp")
  stopifnot(!anyDuplicated(info$hhcode), !anyDuplicated(roster, by = c("hhcode", "idc")),
            !anyDuplicated(weights$prcode), !anyDuplicated(consumed, by = c("hhcode", "itc")),
            setequal(info$hhcode, unique(consumed$hhcode)), setequal(info$hhcode, unique(roster$hhcode)))
  members <- roster[, .(members = sum(s1aq10 == 1, na.rm = TRUE)), by = hhcode]
  stopifnot(!anyNA(roster$s1aq10))
  hh <- merge(info[, .(hhcode, prcode, province, region, enum_year, enum_month)], members,
              by = "hhcode", sort = FALSE, allow.cartesian = FALSE)
  hh <- merge(hh, weights, by = "prcode", all.x = TRUE, sort = FALSE, allow.cartesian = FALSE)
  stopifnot(nrow(hh) == 30123L, !anyNA(hh$weight), all(hh$weight > 0), all(hh$members > 0))
  hh[, `:=`(population_weight = weight * members, period = sprintf("%04d-%02d", enum_year, enum_month))]
  # Reconstruct the frozen exploratory groups, with monthly rather than food-daily periods.
  form <- fread(file.path(profile, "form_item_part_mapping.csv"))
  stopifnot(nrow(form) == 285L, !anyDuplicated(form$itc))
  monthly <- c(A = 26/12, B = 1, C = 1, D = 1/12, E = 1/12)
  detail <- merge(consumed[, .(hhcode, itc, v1, v2, v3, v4)], form[, .(itc, part)],
                  by = "itc", sort = FALSE, allow.cartesian = FALSE)
  detail[, amount := rowSums(.SD, na.rm = TRUE) * monthly[part], .SDcols = paste0("v", 1:4)]
  observed <- detail[, .(nominal = sum(amount),
       scope_excluded = sum(amount[!itc %in% c(42104L, 72401L, 127001L, 127007L, 123102L)])), by = hhcode]
  hh <- merge(hh, observed, by = "hhcode", sort = FALSE, allow.cartesian = FALSE)
  overall <- fread(file.path(root, "scripts/diet/m3_price_inputs/overall_cpi/overall_cpi.csv"))[
    residence %in% c("rural", "urban") & period >= "2024-10" & period <= "2025-06"]
  overall[, overall_factor := value / mean(value), by = residence]
  overall[, region := ifelse(residence == "rural", 1L, 2L)]
  hh <- merge(hh, overall[, .(region, period, overall_factor)], by = c("region", "period"),
              all.x = TRUE, sort = FALSE, allow.cartesian = FALSE)
  stopifnot(!anyNA(hh$overall_factor))
  hh[, cpi_temporal := nominal / overall_factor]
  groups <- rbindlist(lapply(c("nominal", "scope_excluded", "cpi_temporal"), function(name) {
    rank <- hh[, .(hhcode, per_member = get(name) / members, population_weight)]
    stopifnot(all(rank$per_member > 0))
    ties <- rank[, .(tie_weight = sum(population_weight)), by = per_member][order(per_member)]
    ties[, quintile := pmin(5L, pmax(1L, as.integer(floor(5 *
       (cumsum(tie_weight) - 0.5 * tie_weight) / sum(tie_weight))) + 1L))]
    rank <- merge(rank, ties[, .(per_member, quintile)], by = "per_member", sort = FALSE,
                  allow.cartesian = FALSE)
    stopifnot(nrow(rank) == 30123L, !anyDuplicated(rank$hhcode), !anyNA(rank$quintile))
    rank[, .(hhcode, grouping_scenario = name, quintile)]
  }))
  group_hh <- merge(groups, hh[, .(hhcode, province, region, weight, population_weight)],
                    by = "hhcode", sort = FALSE, allow.cartesian = TRUE)
  rebuilt <- group_hh[, .(households = .N, sum_household_weight = sum(weight),
                         sum_population_weight = sum(population_weight)),
                      by = .(scenario = grouping_scenario, province, region, quintile)]
  previous <- fread(file.path(frozen, "group_coverage_by_geography.csv"))
  comparison <- merge(rebuilt, previous, by = c("scenario", "province", "region", "quintile"),
                       suffixes = c("_new", "_old"), allow.cartesian = FALSE)
  stopifnot(nrow(comparison) == 120L, all(comparison$households_new == comparison$households_old),
            close_enough(comparison$sum_household_weight_new, comparison$sum_household_weight_old),
            close_enough(comparison$sum_population_weight_new, comparison$sum_population_weight_old))
  save_csv(rebuilt[order(scenario, province, region, quintile)], "reconstructed_group_counts.csv")
  # Source inventory, with one item row and no source-record quantity export.
  inventory <- fread(file.path(root, "scripts/diet/m3_food_crosswalk/questionnaire_inventory.csv"))
  stopifnot(nrow(inventory) == 120L, !anyDuplicated(inventory$itc),
            sum(inventory$food_scope) == 119L, inventory[food_scope == FALSE, itc] == 11108L)
  inventory <- merge(inventory[, .(itc, questionnaire_label, native_unit, period_days, food_scope)],
                     form[, .(itc, part)], by = "itc", sort = FALSE, allow.cartesian = FALSE)
  stopifnot(nrow(inventory) == 120L, all(inventory$part %in% c("A", "B")),
            all(inventory$period_days == ifelse(inventory$part == "A", 14L, 30L)))
  inventory[, source_scope := fifelse(!food_scope, "SERVICE",
                         fifelse(itc >= 110001 & itc <= 110021, "PREPARED", "AT_HOME"))]
  inventory[, questionnaire_group_prefix := as.integer(itc %/% 100L)]
  factors <- fread(file.path(factors_dir, "compiled_factors.csv"), na.strings = c("", "NA"),
                   colClasses = list(character = c("protein_factor_numerator", "protein_factor_denominator")))
  factors[, protein_g_per_native_unit := as.double(protein_factor_numerator) / as.double(protein_factor_denominator)]
  stopifnot(!anyDuplicated(factors, by = c("scenario", "itc")))
  for (name in unique(factors$scenario)) stopifnot(setequal(factors[scenario == name, itc], inventory$itc))
  stopifnot(all(factors$role %in% c("G", "K", "DIRECT_ZERO_OUTSIDE_G", "SERVICE")),
            all(is.na(factors[role %in% c("K", "SERVICE"), protein_g_per_native_unit])),
            all(factors[role %in% c("G", "DIRECT_ZERO_OUTSIDE_G"), protein_g_per_native_unit] >= 0),
            all(factors[role == "G" & known_zero == TRUE, protein_g_per_native_unit] == 0),
            all(factors[role == "G" & known_zero == FALSE, protein_g_per_native_unit] > 0),
            all(factors[role == "SERVICE", itc] == 11108L),
            all(factors[role == "DIRECT_ZERO_OUTSIDE_G", itc] == 110018L))
  stopifnot(!anyNA(factors[role %in% c("G", "DIRECT_ZERO_OUTSIDE_G"), protein_g_per_native_unit]),
            all(factors[role == "G", section_group] %in% c("AT_HOME_14_DAY", "AT_HOME_30_DAY")))
  save_csv(factors, "factor_route_inventory.csv", contributing = "not_applicable")
  # Read only the paired amount columns here; roster-linked geography is canonical.
  amount_columns <- c("hhcode", "itc", paste0("q", 1:4), paste0("v", 1:4))
  foods <- merge(consumed[, ..amount_columns], inventory, by = "itc", sort = FALSE, allow.cartesian = FALSE)
  foods <- merge(foods, hh[, .(hhcode, province, region, period, weight, population_weight)],
                 by = "hhcode", sort = FALSE, allow.cartesian = FALSE)
  stopifnot(setequal(unique(foods$itc), inventory$itc), !anyDuplicated(foods, by = c("hhcode", "itc")))
  prices <- fread(file.path(root, "scripts/diet/m3_price_inputs/price_indices_staging.csv"))[
    residence %in% c("rural", "urban") & period >= "2024-10" & period <= "2025-06"]
  stopifnot(nrow(prices) == 36L, !anyDuplicated(prices, by = c("residence", "period", "series")))
  prices[, `:=`(series_mean = mean(value), temporal_factor = value / mean(value)), by = .(residence, series)]
  prices[, region := ifelse(residence == "rural", 1L, 2L)]
  save_csv(prices[, .(residence, period, series, value, series_mean, temporal_factor, source_id,
                       pdf_page, raw_file, raw_sha256)][order(residence, series, period)],
           "temporal_food_price_factors.csv", contributing = "not_applicable")
  foods[, series := ifelse(source_scope == "PREPARED", "restaurants_and_hotels", "food_and_non_alcoholic_beverages")]
  foods <- merge(foods, prices[, .(region, period, series, temporal_factor)],
                 by = c("region", "period", "series"), all.x = TRUE, sort = FALSE, allow.cartesian = FALSE)
  stopifnot(!anyNA(foods$temporal_factor), all(foods$temporal_factor > 0))
  # Independent wide-record value control, before channel classification or factor joins.
  foods[, observed_daily := daily_amount(rowSums(.SD, na.rm = TRUE), period_days), .SDcols = paste0("v", 1:4)]
  control <- foods[, .(households = uniqueN(hhcode), records = .N,
       weighted_nominal_daily_rupees = sum(observed_daily * weight),
       weighted_adjusted_daily_rupees = if (source_scope[1] == "SERVICE") NA_real_ else
                                         sum(observed_daily / temporal_factor * weight)),
       by = .(region, source_scope)]
  save_csv(control[order(region, source_scope)], "source_expenditure_controls.csv")
  paired <- rbindlist(lapply(1:4, function(channel_number) {
    foods[, .(hhcode, itc, questionnaire_label, native_unit, period_days, food_scope, source_scope,
      questionnaire_group_prefix, region, period, weight, temporal_factor, channel = channel_number,
      q = as.double(get(paste0("q", channel_number))), v = as.double(get(paste0("v", channel_number))))]
  }))
  paired[, `:=`(q_positive = !is.na(q) & q > 0, v_positive = !is.na(v) & v > 0)]
  stopifnot(all(is.na(paired$q) | is.finite(paired$q)), all(is.na(paired$v) | is.finite(paired$v)))
  missingness <- paired[, .(households = uniqueN(hhcode), channel_records = .N,
     both_missing = sum(is.na(q) & is.na(v)), quantity_missing = sum(is.na(q)), value_missing = sum(is.na(v)),
     positive_quantity_and_value = sum(q_positive & v_positive),
     positive_value_without_positive_quantity = sum(v_positive & !q_positive),
     positive_quantity_without_positive_value = sum(q_positive & !v_positive),
     negative_quantity = sum(!is.na(q) & q < 0), negative_value = sum(!is.na(v) & v < 0)),
     by = .(itc, questionnaire_label, native_unit, period_days, source_scope, questionnaire_group_prefix, channel)]
  save_csv(missingness[order(itc, channel)], "item_channel_missingness.csv")
  active <- paired[!is.na(q) | !is.na(v)]
  active[, value_daily := daily_amount(v, period_days)]
  rm(paired, detail, consumed, roster, foods)
  ledger_outputs <- list(); national_outputs <- list(); item_outputs <- list(); foodgroup_outputs <- list()
  group_outputs <- list(); hh_outputs <- list(); checks <- list()
  for (factor_name in unique(factors$scenario)) {
    f <- factors[scenario == factor_name]
    stopifnot(nrow(f) == 120L, all(f$period_days == inventory$period_days[match(f$itc, inventory$itc)]),
              all(f$native_unit == inventory$native_unit[match(f$itc, inventory$itc)]))
    work <- merge(active, f[, .(itc, role, protein_g_per_native_unit, known_zero, quantity_required_for_G,
                               calibration_value_eligible, section_group)],
                   by = "itc", all.x = TRUE, sort = FALSE, allow.cartesian = FALSE)
    stopifnot(nrow(work) == nrow(active), !anyNA(work$role),
              all(work[source_scope == "PREPARED", section_group] == "PREPARED_30_DAY"),
              all(work[source_scope == "SERVICE", section_group] == "MILLING_SERVICE_30_DAY"),
              all(work[source_scope == "AT_HOME" & period_days == 14L, section_group] == "AT_HOME_14_DAY"),
              all(work[source_scope == "AT_HOME" & period_days == 30L, section_group] == "AT_HOME_30_DAY"))
    work <- classify_channels(work)
    work[, protein_G := NA_real_]
    work[disposition == "G_positive", protein_G := daily_amount(q, period_days) * protein_g_per_native_unit]
    work[disposition == "G_known_zero", protein_G := 0]
    work[, value_G := fifelse(disposition %in% c("G_positive", "G_known_zero"), value_daily, NA_real_)]
    work[, adjusted_value := fifelse(source_scope == "SERVICE", NA_real_, value_daily / temporal_factor)]
    stopifnot(all(work[disposition == "G_positive", protein_G] > 0),
              all(work[disposition %in% c("G_positive", "G_known_zero"), value_G] > 0),
              all(work[disposition == "G_known_zero", quantity_required_for_G] == FALSE),
              all(work[disposition == "G_positive", quantity_required_for_G] == TRUE),
              all(work[disposition %in% c("G_positive", "G_known_zero"), calibration_value_eligible] == TRUE))
    # Signed daily-value conservation includes exception values, never fabricated missing values.
    check <- work[, .(classified_nominal = sum(value_daily * weight, na.rm = TRUE),
       classified_adjusted = if (source_scope[1] == "SERVICE") NA_real_ else
                              sum(adjusted_value * weight, na.rm = TRUE)), by = .(region, source_scope)]
    check <- merge(check, control, by = c("region", "source_scope"), allow.cartesian = FALSE)
    stopifnot(close_enough(check$classified_nominal, check$weighted_nominal_daily_rupees),
              close_enough(check[source_scope != "SERVICE", classified_adjusted],
                           check[source_scope != "SERVICE", weighted_adjusted_daily_rupees]))
    ledger_outputs[[factor_name]] <- work[, .(factor_scenario = factor_name,
       households = uniqueN(hhcode), active_channel_records = .N,
       positive_value_channel_records = sum(v_positive),
       weighted_nominal_daily_rupees = sum(value_daily * weight, na.rm = TRUE),
       weighted_adjusted_daily_rupees = if (source_scope[1] == "SERVICE") NA_real_ else
                                       sum(adjusted_value * weight, na.rm = TRUE)),
       by = .(region, period_days, source_scope, channel, disposition)]
    national <- work[, .(factor_scenario = factor_name, households = uniqueN(hhcode),
       active_channel_records = .N,
       weighted_nominal_daily_rupees = sum(value_daily * weight, na.rm = TRUE),
       weighted_adjusted_daily_rupees = if (source_scope[1] == "SERVICE") NA_real_ else
                                       sum(adjusted_value * weight, na.rm = TRUE)),
       by = .(source_scope, disposition)]
    food_nominal_total <- sum(control[source_scope != "SERVICE", weighted_nominal_daily_rupees])
    food_adjusted_total <- sum(control[source_scope != "SERVICE", weighted_adjusted_daily_rupees])
    national[, nominal_share_of_food_expenditure := fifelse(source_scope == "SERVICE", NA_real_,
                                   weighted_nominal_daily_rupees / food_nominal_total)]
    national[, adjusted_share_of_food_expenditure := fifelse(source_scope == "SERVICE", NA_real_,
                                   weighted_adjusted_daily_rupees / food_adjusted_total)]
    stopifnot(close_enough(sum(national$nominal_share_of_food_expenditure, na.rm = TRUE), 1),
              close_enough(sum(national$adjusted_share_of_food_expenditure, na.rm = TRUE), 1))
    national_outputs[[factor_name]] <- national
    item_outputs[[factor_name]] <- work[, .(factor_scenario = factor_name, households = uniqueN(hhcode),
       active_channel_records = .N, weighted_nominal_daily_rupees = sum(value_daily * weight, na.rm = TRUE)),
       by = .(itc, questionnaire_label, native_unit, source_scope, questionnaire_group_prefix, channel, disposition)]
    foodgroup_outputs[[factor_name]] <- work[, .(factor_scenario = factor_name,
       households = uniqueN(hhcode), item_codes_present = uniqueN(itc), active_channel_records = .N,
       weighted_nominal_daily_rupees = sum(value_daily * weight, na.rm = TRUE)),
       by = .(source_scope, questionnaire_group_prefix, channel, disposition)]
    hh_values <- work[, .(food_records_present = any(food_scope),
       protein_G = sum(protein_G, na.rm = TRUE), value_G = sum(value_G, na.rm = TRUE),
       adjusted_value_G = sum(value_G / temporal_factor, na.rm = TRUE),
       G_positive_channels = sum(disposition == "G_positive"), G_zero_channels = sum(disposition == "G_known_zero"),
       K_at_home_channels = sum(disposition == "K_at_home"), K_prepared_channels = sum(disposition == "K_prepared"),
       direct_zero_channels = sum(disposition == "direct_zero_prepared"),
       q_without_positive_v_channels = sum(food_scope & q_positive & !v_positive)), by = hhcode]
    hh_diag <- merge(hh[, .(hhcode, province, region, weight, population_weight)], hh_values,
                     by = "hhcode", all.x = TRUE, sort = FALSE, allow.cartesian = FALSE)
    hh_diag[, eligible := !is.na(protein_G) & protein_G > 0 & !is.na(value_G) & value_G > 0]
    hh_diag[, food_records_present := !is.na(food_records_present) & food_records_present]
    hh_diag[, q_value_flag := !is.na(q_without_positive_v_channels) & q_without_positive_v_channels > 0]
    stopifnot(nrow(hh_diag) == 30123L,
              all(hh_diag[eligible == TRUE, adjusted_value_G] > 0))
    hh_outputs[[factor_name]] <- hh_diag[, .(factor_scenario = factor_name, households = .N,
      sum_population_weight = sum(population_weight)),
      by = .(food_records_present, eligible, q_value_flag)]
    cells <- merge(groups, hh_diag, by = "hhcode", sort = FALSE, allow.cartesian = TRUE)
    stopifnot(nrow(cells) == 3L * 30123L)
    group_outputs[[factor_name]] <- cells[, .(factor_scenario = factor_name, households = .N,
      eligible_households = sum(eligible), ineligible_households = sum(!eligible),
      food_absent_households = sum(!food_records_present), q_value_flag_households = sum(q_value_flag),
      eligible_household_share = mean(eligible),
      total_population_weight = sum(population_weight),
      eligible_population_weight = sum(population_weight[eligible]),
      eligible_population_share = sum(population_weight[eligible]) / sum(population_weight),
      G_positive_present_households = sum(G_positive_channels > 0, na.rm = TRUE),
      G_zero_present_households = sum(G_zero_channels > 0, na.rm = TRUE),
      K_at_home_present_households = sum(K_at_home_channels > 0, na.rm = TRUE),
      K_prepared_present_households = sum(K_prepared_channels > 0, na.rm = TRUE),
      direct_zero_present_households = sum(direct_zero_channels > 0, na.rm = TRUE)),
      by = .(grouping_scenario, province, region, quintile)]
    checks[[factor_name]] <- list(active_channel_records = nrow(work),
       positive_quantity_without_positive_value_channels = sum(work$q_positive & !work$v_positive & work$food_scope),
       negative_food_quantity_channels = sum(work$food_scope & !is.na(work$q) & work$q < 0),
       negative_food_value_channels = sum(work$food_scope & !is.na(work$v) & work$v < 0),
       eligible_households = sum(hh_diag$eligible), missing_food_households = sum(!hh_diag$food_records_present),
       conservation_nominal_and_adjusted = TRUE, group_cells = nrow(group_outputs[[factor_name]]))
  }
  save_csv(rbindlist(ledger_outputs)[order(factor_scenario, region, period_days, channel, disposition)], "expenditure_ledger.csv")
  save_csv(rbindlist(national_outputs)[order(factor_scenario, source_scope, disposition)], "national_expenditure_coverage.csv")
  save_csv(rbindlist(item_outputs)[order(factor_scenario, itc, channel, disposition)], "item_disposition_coverage.csv")
  save_csv(rbindlist(foodgroup_outputs)[order(factor_scenario, source_scope, questionnaire_group_prefix, channel, disposition)],
           "questionnaire_group_coverage.csv")
  save_csv(rbindlist(group_outputs)[order(factor_scenario, grouping_scenario, province, region, quintile)],
           "calibration_cell_coverage.csv", contributing = "eligible_households")
  save_csv(rbindlist(hh_outputs)[order(factor_scenario, food_records_present, eligible, q_value_flag)], "household_eligibility_summary.csv")
  save_json(list(status = "EXPLORATORY_COVERAGE_ONLY_NO_UNIT_COSTS_OR_INTAKE", households = nrow(hh),
    food_item_codes = 119L, service_item_codes = 1L, factor_scenarios = names(checks),
    reconstructed_group_cells_match = 120L, scenario_checks = checks,
    channel_negative_controls = negative_controls,
    source_household_or_person_records_or_identifiers_exported = 0L,
    nutrient_unit_costs_computed = 0L, imputed_nutrients_computed = 0L,
    total_intake_or_gap_computed = 0L, runtime = list(R = as.character(getRversion()),
      data_table = as.character(packageVersion("data.table")), foreign = as.character(packageVersion("foreign")))),
    "coverage_checks.json")
  cat("PASS: source-bound aggregate calibration coverage; no unit costs, imputation or intake.\n")
}
main()
