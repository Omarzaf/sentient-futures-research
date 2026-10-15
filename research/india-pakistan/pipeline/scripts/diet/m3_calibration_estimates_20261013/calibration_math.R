# Deterministic method functions. All data-frame returns here are aggregate rows.
positive_weighted_median <- function(cost, population_weight) {
  stopifnot(length(cost) > 0L, length(cost) == length(population_weight),
            all(is.finite(cost)), all(cost > 0), all(is.finite(population_weight)),
            all(population_weight > 0))
  tied <- data.table(cost = cost, weight = population_weight)[,
            .(weight = sum(weight)), by = cost][order(cost)]
  tied[, cumulative := cumsum(weight)]
  answer <- tied[cumulative >= sum(weight) / 2, cost][1L]
  stopifnot(length(answer) == 1L, is.finite(answer), answer > 0)
  answer
}

require_complete_cells <- function(medians, expected) {
  keys <- c("province", "region", "quintile")
  stopifnot(!anyDuplicated(medians, by = keys), nrow(medians) == nrow(expected))
  joined <- merge(expected, medians, by = keys, all.x = TRUE, sort = FALSE,
                  allow.cartesian = FALSE)
  stopifnot(nrow(joined) == 40L, !anyNA(joined$median_cost_rupees_per_g),
            all(is.finite(joined$median_cost_rupees_per_g)),
            all(joined$median_cost_rupees_per_g > 0), all(joined$reference_households > 0))
  joined
}

experimental_components <- function(source_protein, at_home_value, prepared_value, cost) {
  stopifnot(all(is.finite(source_protein)), all(source_protein >= 0),
            all(is.finite(at_home_value)), all(at_home_value >= 0),
            all(is.finite(prepared_value)), all(prepared_value >= 0),
            all(is.finite(cost)), all(cost > 0))
  at_home <- at_home_value / cost
  prepared <- prepared_value / cost
  total <- source_protein + at_home + prepared
  stopifnot(all(is.finite(total)), all(total >= source_protein))
  list(at_home = at_home, prepared = prepared, total = total)
}

calibration_negative_controls <- function() {
  # Synthetic method controls only; never mix these values with empirical data.
  near <- function(a, b) isTRUE(all.equal(a, b, tolerance = 1e-12))
  expect_error <- function(expr) inherits(tryCatch({force(expr); NULL}, error = identity), "error")
  stopifnot(positive_weighted_median(c(1, 3), c(1, 1)) == 1,
            positive_weighted_median(c(3, 1), c(1, 1)) == 1,
            positive_weighted_median(c(1, 1, 3), c(1, 1, 2)) == 1,
            positive_weighted_median(c(1, 2, 3), c(1, 2, 1)) == 2,
            positive_weighted_median(c(1, 3), c(1, 2)) == 3,
            expect_error(positive_weighted_median(numeric(), numeric())),
            expect_error(positive_weighted_median(c(1, Inf), c(1, 1))),
            expect_error(positive_weighted_median(c(1, NA_real_), c(1, 1))),
            expect_error(positive_weighted_median(c(0, 1), c(1, 1))),
            expect_error(positive_weighted_median(c(1, 2), c(0, 1))))
  p <- c(2, 4); v <- c(6, 20); k_at <- c(9, 10); k_prepared <- c(3, 5); w <- c(1, 2)
  u <- positive_weighted_median(v / p, w)
  base <- experimental_components(p, k_at, k_prepared, u)
  scaled <- experimental_components(p, k_at * 100, k_prepared * 100,
                                     positive_weighted_median((v * 100) / p, w))
  stopifnot(near(base$total, scaled$total),
            near(experimental_components(p, c(0, 0), c(0, 0), u)$total, p),
            all(experimental_components(p, k_at, k_prepared,
                    positive_weighted_median((v + 10) / p, w))$total < base$total),
            experimental_components(2, 6, 3, 3)$total == 5,
            expect_error(experimental_components(2, 6, 3, NA_real_)))
  expected <- CJ(province = 1:4, region = 1:2, quintile = 1:5)
  medians <- copy(expected)[, `:=`(median_cost_rupees_per_g = 1, reference_households = 10L)]
  stopifnot(nrow(require_complete_cells(medians, expected)) == 40L,
            expect_error(require_complete_cells(medians[-1], expected)))
  list(status = "PASS", method_controls = 17L, synthetic_only = TRUE,
       dimensions = "rupees_per_day divided by rupees_per_gram yields grams_per_day",
       invalid_reference_cost_hard_stop = TRUE, missing_stratum_hard_stop = TRUE)
}

summarize_estimates <- function(rows, level, keys) {
  value <- rows[, .(households = .N, members = sum(members),
     reference_households = sum(eligible), no_matched_source_households = sum(protein_G == 0),
     households_with_imputed_at_home = sum(imputed_at_home > 0),
     households_with_imputed_prepared = sum(imputed_prepared > 0),
     household_weight = sum(weight), population_weight = sum(population_weight),
     source_weighted_g_per_day = sum(weight * protein_G),
     imputed_at_home_weighted_g_per_day = sum(weight * imputed_at_home),
     imputed_prepared_weighted_g_per_day = sum(weight * imputed_prepared),
     total_weighted_g_per_day = sum(weight * total_protein)), by = keys]
  value[, `:=`(reporting_level = level,
     source_g_per_member_day = source_weighted_g_per_day / population_weight,
     imputed_at_home_g_per_member_day = imputed_at_home_weighted_g_per_day / population_weight,
     imputed_prepared_g_per_member_day = imputed_prepared_weighted_g_per_day / population_weight,
     total_g_per_member_day = total_weighted_g_per_day / population_weight,
     imputed_share = (imputed_at_home_weighted_g_per_day + imputed_prepared_weighted_g_per_day) /
                     total_weighted_g_per_day)]
  for (key in c("province", "region", "quintile")) if (!key %in% names(value)) value[, (key) := NA_integer_]
  value
}

estimate_case <- function(hh_values, grouping, factor_name, grouping_name, price_name) {
  stopifnot(price_name %in% c("food_restaurant_cpi", "no_cpi", "food_cpi_for_prepared"))
  rows <- merge(hh_values, grouping, by = "hhcode", sort = FALSE, allow.cartesian = FALSE)
  stopifnot(nrow(rows) == 30123L, !anyDuplicated(rows$hhcode))
  if (price_name == "no_cpi") {
    rows[, `:=`(selected_G_value = value_G, selected_K_at = K_at_home_nominal,
                selected_K_prepared = K_prepared_nominal)]
  } else {
    rows[, `:=`(selected_G_value = adjusted_value_G, selected_K_at = K_at_home_adjusted,
                selected_K_prepared = K_prepared_restaurant_adjusted)]
    if (price_name == "food_cpi_for_prepared") rows[, selected_K_prepared := K_prepared_food_adjusted]
  }
  # Eligibility is established in reviewed routing. Never silently filter invalid costs.
  rows[, unit_cost := NA_real_]
  rows[eligible == TRUE, unit_cost := selected_G_value / protein_G]
  stopifnot(all(is.finite(rows[eligible == TRUE, unit_cost])),
            all(rows[eligible == TRUE, unit_cost] > 0),
            all(is.finite(rows$selected_K_at)), all(rows$selected_K_at >= 0),
            all(is.finite(rows$selected_K_prepared)), all(rows$selected_K_prepared >= 0))
  medians <- rows[eligible == TRUE, .(reference_households = .N,
      reference_population_weight = sum(population_weight),
      median_cost_rupees_per_g = positive_weighted_median(unit_cost, population_weight)),
      by = .(province, region, quintile)]
  expected <- CJ(province = 1:4, region = 1:2, quintile = 1:5)
  medians <- require_complete_cells(medians, expected)
  rows <- merge(rows, medians[, .(province, region, quintile, median_cost_rupees_per_g)],
                by = c("province", "region", "quintile"), all.x = TRUE, sort = FALSE, allow.cartesian = FALSE)
  stopifnot(nrow(rows) == 30123L, !anyNA(rows$median_cost_rupees_per_g))
  components <- experimental_components(rows$protein_G, rows$selected_K_at,
                                        rows$selected_K_prepared, rows$median_cost_rupees_per_g)
  rows[, `:=`(imputed_at_home = components$at_home, imputed_prepared = components$prepared,
              total_protein = components$total)]
  levels <- list(national = character(), residence = "region", province = "province",
     province_residence = c("province", "region"), national_quintile = "quintile",
     residence_quintile = c("region", "quintile"), stratum = c("province", "region", "quintile"))
  summaries <- rbindlist(lapply(names(levels), function(level) summarize_estimates(rows, level, levels[[level]])),
                        use.names = TRUE, fill = TRUE)
  stopifnot(nrow(summaries) == 70L)
  national <- summaries[reporting_level == "national"]
  # Disjoint residence, province, and quintile summaries must each reconstruct the same national totals.
  recombination <- rbindlist(lapply(setdiff(names(levels), "national"), function(level) {
    subset <- summaries[reporting_level == level]
    columns <- c("households", "members", "household_weight", "population_weight",
      "source_weighted_g_per_day", "imputed_at_home_weighted_g_per_day",
      "imputed_prepared_weighted_g_per_day", "total_weighted_g_per_day")
    difference <- vapply(columns, function(column) sum(subset[[column]]) - national[[column]], numeric(1))
    relative <- abs(difference) / pmax(1, abs(unlist(national[, ..columns])))
    stopifnot(all(relative < 1e-11))
    data.table(reporting_level = level, maximum_relative_recombination_error = max(relative))
  }))
  for (object in list(summaries, medians, recombination)) object[, `:=`(
     factor_scenario = factor_name, grouping_scenario = grouping_name, price_scenario = price_name)]
  median_summary <- data.table(factor_scenario = factor_name, grouping_scenario = grouping_name,
    price_scenario = price_name, positive_cost_cells = nrow(medians),
    minimum_reference_households = min(medians$reference_households),
    maximum_reference_households = max(medians$reference_households),
    minimum_stratum_median_cost_rupees_per_g = min(medians$median_cost_rupees_per_g),
    maximum_stratum_median_cost_rupees_per_g = max(medians$median_cost_rupees_per_g))
  list(summaries = summaries, medians = medians, median_summary = median_summary,
       recombination = recombination)
}

source_outlier_influence <- function(hh_values, factor_name) {
  values <- hh_values[, .(source_per_member = protein_G / members, protein_G, weight, population_weight)]
  total_source <- sum(values$weight * values$protein_G)
  stopifnot(is.finite(total_source), total_source > 0)
  rbindlist(lapply(c(0.001, 0.01), function(fraction) {
    rank_count <- as.integer(ceiling(nrow(values) * fraction))
    cutoff <- sort(values$source_per_member, decreasing = TRUE)[rank_count]
    selected <- values[source_per_member >= cutoff]
    data.table(factor_scenario = factor_name, requested_unweighted_household_fraction = fraction,
      households = nrow(selected), rank_cutoff_household_count = rank_count,
      actual_unweighted_household_share = nrow(selected) / nrow(values),
      source_per_member_cutoff_g_day = cutoff,
      population_weight_share = sum(selected$population_weight) / sum(values$population_weight),
      weighted_source_protein_share = sum(selected$weight * selected$protein_G) / total_source,
      source_values_removed_or_winsorized = 0L)
  }))
}
