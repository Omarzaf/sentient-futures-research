# Aggregate-only feasibility profile of the unchanged public PBS Stata archive.
# No household/person rows, identifiers, nutrient values or imputations are written.

suppressPackageStartupMessages(library(data.table))
setDTthreads(2L)

main <- function() {
  root <- normalizePath(getwd())
  out <- file.path(root, "scripts/diet/m3_microdata_profile")
  archive <- file.path(root, "data/raw/diet/m3-reassessment-2026-10-13/pbs-stata-2024-25.zip")
  stopifnot(dir.exists(out), file.exists(archive))
  # Only byte-identical temporary copies are needed by foreign's filename API.
  scratch <- tempfile("pbs-read-only-")
  dir.create(scratch)
  on.exit(unlink(scratch, recursive = TRUE), add = TRUE)
  schemas <- list()
  allowed_labels <- c("province", "region", "itc", "unit", "quater", "s1aq10", "s1aq04", "fstatus")
  save_json <- function(value, name) {
    stopifnot(basename(name) == name)
    jsonlite::write_json(value, file.path(out, name), pretty = TRUE,
                         auto_unbox = TRUE, na = "null", null = "null", digits = NA)
  }
  save_table <- function(value, name) {
    stopifnot(basename(name) == name,
              !any(c("hhcode", "prcode", "hhno", "idc") %in% names(value)))
    # Small cells retain counts only, never an amount attributable to <5 households.
    if ("households" %in% names(value)) {
      amounts <- grep("^(q[1-4]|v[1-4]|sum_[abc]|sum_c02)$", names(value), value = TRUE)
      value <- copy(value)
      value[, amounts_suppressed_small_cell := households < 5L]
      if (length(amounts)) value[households < 5L, (amounts) := NA_real_]
    }
    fwrite(value, file.path(out, name), na = "")
  }
  read_table <- function(name) {
    member <- paste0("Stata data/", name, ".dta")
    local_file <- unzip(archive, files = member, exdir = scratch)
    stopifnot(length(local_file) == 1L)
    frame <- foreign::read.dta(local_file, convert.dates = FALSE,
                               convert.factors = FALSE, missing.type = FALSE,
                               warn.missing.labels = FALSE)
    columns <- names(frame)
    labels <- attr(frame, "label.table")
    val_names <- attr(frame, "val.labels")
    public_labels <- list()
    for (field in intersect(columns, allowed_labels)) {
      target <- val_names[match(field, columns)]
      table <- labels[[target]]
      if (!is.null(table)) {
        public_labels[[field]] <- data.frame(code = unname(table), label = names(table))
      }
    }
    schemas[[name]] <<- list(
      observations = nrow(frame), variables = ncol(frame),
      dataset_label = attr(frame, "datalabel"), saved_timestamp = attr(frame, "time.stamp"),
      stata_version = attr(frame, "version"),
      columns = data.frame(name = columns, storage_type = attr(frame, "types"),
                           format = attr(frame, "formats"),
                           label = attr(frame, "var.labels"), value_label_name = val_names),
      public_classification_labels = public_labels
    )
    setDT(frame)
    frame
  }
  key_check <- function(frame, fields) {
    list(rows = nrow(frame), key_fields = fields,
         rows_missing_any_key = sum(!complete.cases(frame[, ..fields])),
         distinct_keys = uniqueN(frame, by = fields),
         duplicate_rows_on_key = sum(duplicated(frame, by = fields)))
  }
  column_counts <- function(frame, fields, dataset) {
    rbindlist(lapply(fields, function(field) {
      x <- frame[[field]]
      data.table(dataset = dataset, column = field, rows = length(x),
                 missing = sum(is.na(x)), zero = sum(x == 0, na.rm = TRUE),
                 negative = sum(x < 0, na.rm = TRUE), nonmissing = sum(!is.na(x)))
    }))
  }
  info <- read_table("section_info")
  roster <- read_table("plist_roster")
  weights <- read_table("weight")
  food <- read_table("sec_6a_consum_exp")
  qv <- c(paste0("q", 1:4), paste0("v", 1:4))
  durables <- read_table("sec_7")
  transfers <- read_table("sec_8a")
  checks <- list(
    info_household = key_check(info, "hhcode"),
    info_psu_household = key_check(info, c("prcode", "hhno")),
    roster_person = key_check(roster, c("hhcode", "idc")),
    weight_psu = key_check(weights, "prcode"),
    consumption_household_item = key_check(food, c("hhcode", "itc")),
    consumption_household_item_unit_point = key_check(food, c("hhcode", "itc", "unit", "pp")),
    durables_household_item = key_check(durables, c("hhcode", "itc")),
    transfers_household_item = key_check(transfers, c("hhcode", "code"))
  )
  save_json(schemas, "reader_schemas.json")
  stopifnot(checks$info_household$duplicate_rows_on_key == 0L,
            checks$info_household$rows_missing_any_key == 0L,
            checks$roster_person$duplicate_rows_on_key == 0L,
            checks$weight_psu$duplicate_rows_on_key == 0L)
  save_table(info[, .(households = .N), by = .(enum_year, enum_month)][order(enum_year, enum_month)],
             "enumeration_period_counts.csv")
  save_table(info[, .(households = .N), by = .(province, region, fstatus)][order(province, region, fstatus)],
             "sample_household_counts.csv")
  save_table(roster[, .(roster_records = .N), by = .(s1aq10, s1aq04)][order(s1aq10, s1aq04)],
             "membership_residence_counts.csv")
  hh <- roster[, .(roster_n = .N, member_yes_n = sum(s1aq10 == 1, na.rm = TRUE),
                    member_unknown_n = sum(is.na(s1aq10)),
                    weight_count = uniqueN(weight), weight_value = first(weight),
                    psu_count = uniqueN(prcode), prcode = first(prcode)), by = hhcode]
  checks$roster_household_weight <- list(
    household_count = nrow(hh), inconsistent_weight_households = sum(hh$weight_count != 1L),
    missing_weight_households = sum(is.na(hh$weight_value)),
    nonpositive_weight_households = sum(hh$weight_value <= 0, na.rm = TRUE),
    inconsistent_psu_households = sum(hh$psu_count != 1L),
    zero_yes_member_households = sum(hh$member_yes_n == 0),
    info_households_without_roster = sum(!info$hhcode %in% hh$hhcode),
    roster_households_without_info = sum(!hh$hhcode %in% info$hhcode)
  )
  stopifnot(all(hh$weight_count == 1L), all(hh$psu_count == 1L))
  setnames(weights, "weight", "psu_weight")
  hh <- merge(hh, weights, by = "prcode", all.x = TRUE, sort = FALSE, allow.cartesian = FALSE)
  checks$psu_weight_comparison <- list(
    unmatched_households = sum(is.na(hh$psu_weight)),
    unequal_roster_psu_weights = sum(abs(hh$weight_value - hh$psu_weight) > 1e-8, na.rm = TRUE)
  )
  # Cardinalities proved above; only aggregate output escapes these in-memory joins.
  hh <- merge(hh, info[, .(hhcode, province, region, enum_year, enum_month)],
              by = "hhcode", all.x = TRUE, sort = FALSE, allow.cartesian = FALSE)
  save_table(hh[, .(households = .N, roster_records = sum(roster_n),
                     yes_member_records = sum(member_yes_n),
                     sum_household_weight = sum(weight_value),
                     weighted_roster_population = sum(weight_value * roster_n),
                     weighted_yes_member_population = sum(weight_value * member_yes_n)),
                 by = .(province, region)][order(province, region)], "population_weight_aggregates.csv")
  # Diagnostic published-table reconciliation only: no nutrient factors or intake.
  mapping <- fread(file.path(out, "table23_code_mapping.csv"))
  map_long <- mapping[, .(itc = as.integer(strsplit(item_codes, ";", fixed = TRUE)[[1]])),
                     by = .(food_group, recall_days, native_unit, questionnaire_printed_page)]
  stopifnot(!anyDuplicated(map_long$itc))
  matched <- merge(food[, c("hhcode", "itc", qv), with = FALSE], map_long,
                    by = "itc", all = FALSE, sort = FALSE, allow.cartesian = FALSE)
  matched[, qty_known := rowSums(.SD, na.rm = TRUE), .SDcols = paste0("q", 1:4)]
  matched[, qty_all_missing := rowSums(!is.na(.SD)) == 0L, .SDcols = paste0("q", 1:4)]
  matched[, value_known := rowSums(.SD, na.rm = TRUE), .SDcols = paste0("v", 1:4)]
  matched <- merge(matched, hh[, .(hhcode, region, weight_value)], by = "hhcode",
                    all.x = TRUE, sort = FALSE, allow.cartesian = FALSE)
  comparisons <- rbindlist(lapply(c("all", "rural", "urban"), function(residence) {
    region_code <- if (residence == "rural") 1L else 2L
    people <- if (residence == "all") hh else hh[region == region_code]
    subset <- if (residence == "all") matched else matched[region == region_code]
    denominator_all <- sum(people$weight_value * people$roster_n)
    denominator_yes <- sum(people$weight_value * people$member_yes_n)
    subset[, .(residence = residence,
                source_records = .N,
                records_with_value_but_no_quantity = sum(value_known > 0 & qty_all_missing),
                monthly_quantity_per_roster_person = sum(weight_value * qty_known * 30 / recall_days) / denominator_all,
                monthly_quantity_per_yes_member = sum(weight_value * qty_known * 30 / recall_days) / denominator_yes,
                monthly_quantity_annual26_per_roster = sum(weight_value * qty_known * ifelse(recall_days == 14, 26/12, 1)) / denominator_all,
                monthly_quantity_annual26_per_yes_member = sum(weight_value * qty_known * ifelse(recall_days == 14, 26/12, 1)) / denominator_yes),
            by = .(food_group, native_unit, recall_days)]
  }))
  published <- fread(file.path(root, "scripts/diet/pakistan_diet_rows.csv"))[
    quintile == "all", .(food_group, residence, published_value = value, published_unit = unit, raw_locator)]
  stopifnot(!anyDuplicated(published, by = c("food_group", "residence")))
  comparisons <- merge(comparisons, published, by = c("food_group", "residence"),
                         all.x = TRUE, sort = FALSE, allow.cartesian = FALSE)
  comparisons[, difference_roster := monthly_quantity_per_roster_person - published_value]
  comparisons[, difference_yes_member := monthly_quantity_per_yes_member - published_value]
  comparisons[, displayed_2dp_match_roster := round(monthly_quantity_per_roster_person, 2) == round(published_value, 2)]
  comparisons[, displayed_2dp_match_yes_member := round(monthly_quantity_per_yes_member, 2) == round(published_value, 2)]
  save_table(comparisons[order(residence, food_group)], "table23_reconciliation_diagnostic.csv")
  save_table(comparisons[, .(items = .N, two_decimal_matches_roster = sum(displayed_2dp_match_roster),
                              two_decimal_matches_yes_member = sum(displayed_2dp_match_yes_member),
                              quantity_missing_positive_value_records = sum(records_with_value_but_no_quantity)),
                          by = residence], "table23_match_summary.csv")
  rm(matched)
  # Source-backed timing only, no missing amounts filled and no welfare ranking claimed.
  parts <- data.table(itc = c(1000L, 2000L, 4000L, 5000L, 6000L),
                      part = c("A", "B", "C", "D", "E"),
                      monthly_factor = c(26/12, 1, 1, 1/12, 1/12))
  subtotal <- merge(food[itc %in% parts$itc, c("hhcode", "itc", paste0("v", 1:4)), with = FALSE],
                     parts, by = "itc", all.x = TRUE, sort = FALSE, allow.cartesian = FALSE)
  subtotal[, known_channels := rowSums(!is.na(.SD)), .SDcols = paste0("v", 1:4)]
  subtotal[, reported_value_sum := rowSums(.SD, na.rm = TRUE), .SDcols = paste0("v", 1:4)]
  save_table(subtotal[, .(households = uniqueN(hhcode),
                households_without_subtotal_record = nrow(hh) - uniqueN(hhcode),
                records_without_any_value_channel = sum(known_channels == 0L),
                records_with_some_missing_channels = sum(known_channels < 4L),
                records_with_any_positive_value = sum(reported_value_sum > 0)), by = .(itc, part, monthly_factor)],
                "part_subtotal_coverage.csv")
  budget <- subtotal[, .(parts_recorded = uniqueN(part),
              reported_monthly_value = sum(reported_value_sum * monthly_factor),
              records_with_no_value = sum(known_channels == 0L)), by = hhcode]
  budget <- merge(budget, hh[, .(hhcode, region, weight_value, roster_n, member_yes_n)],
                    by = "hhcode", all.x = TRUE, sort = FALSE, allow.cartesian = FALSE)
  save_table(budget[, .(households = .N), by = .(parts_recorded, records_with_no_value)][order(parts_recorded)],
             "budget_part_coverage_counts.csv")
  # These observed-sum comparisons are diagnostics, not imputed complete expenditures.
  budget_diag <- rbindlist(lapply(c("all", "rural", "urban"), function(residence) {
    subset <- if (residence == "all") budget else budget[region == ifelse(residence == "rural", 1, 2)]
    data.table(residence = residence, households = nrow(subset),
      complete_five_part_households = sum(subset$parts_recorded == 5L),
      mean_observed_subtotal_monthly_value = sum(subset$reported_monthly_value * subset$weight_value) / sum(subset$weight_value),
      monthly_observed_subtotal_per_roster_person = sum(subset$reported_monthly_value * subset$weight_value) / sum(subset$weight_value * subset$roster_n),
      monthly_observed_subtotal_per_yes_member = sum(subset$reported_monthly_value * subset$weight_value) / sum(subset$weight_value * subset$member_yes_n))
  }))
  save_table(budget_diag, "observed_budget_reconciliation_diagnostic.csv")
  # A small common denominator residual cannot be repaired by deleting households to fit.
  quantity_presence <- food[itc >= 11101 & itc <= 12206,
      .(has_quantity = any(rowSums(.SD, na.rm = TRUE) > 0)), by = hhcode, .SDcols = paste0("q", 1:4)]
  quantified <- quantity_presence[has_quantity == TRUE, hhcode]
  checks$food_denominator_diagnostic <- list(
      households_without_any_positive_at_home_food_quantity = sum(!hh$hhcode %in% quantified),
      weighted_roster_population_without_positive_food_quantity = sum(hh[!hhcode %in% quantified, weight_value * roster_n]),
      denominator_exclusions_applied = FALSE)

  # Outlier diagnostics describe unchanged values; no exclusion or winsorization.
  tail_items <- food[itc %in% c(11408L, 12101L, 11203L), c("hhcode", "itc", qv), with = FALSE]
  tail_items <- merge(tail_items, hh[, .(hhcode, region, weight_value)],
                         by = "hhcode", all.x = TRUE, sort = FALSE, allow.cartesian = FALSE)
  tail_items[, known_quantity := rowSums(.SD, na.rm = TRUE), .SDcols = paste0("q", 1:4)]
  tail_items[, known_value := rowSums(.SD, na.rm = TRUE), .SDcols = paste0("v", 1:4)]
  tail_rows <- rbindlist(lapply(c("all", "rural", "urban"), function(residence) {
    subset <- if (residence == "all") tail_items else tail_items[region == ifelse(residence == "rural", 1, 2)]
    subset[, {
      positive <- known_quantity[known_quantity > 0]
      contribution <- known_quantity * weight_value
      unit_price <- known_value[known_quantity > 0] / known_quantity[known_quantity > 0]
      list(residence = residence, households = .N, positive_quantity_households = length(positive),
           q_min = min(positive), q_median = median(positive),
           q_p95 = as.numeric(quantile(positive, .95)), q_p99 = as.numeric(quantile(positive, .99)),
           q_p999 = as.numeric(quantile(positive, .999)), q_max = max(positive),
           largest_record_share_weighted_quantity = max(contribution) / sum(contribution),
           largest_1pct_records_share_weighted_quantity = sum(sort(contribution, decreasing = TRUE)[seq_len(max(1L, ceiling(.N * .01)))]) / sum(contribution),
           implied_unit_price_p01 = as.numeric(quantile(unit_price, .01)),
           implied_unit_price_median = median(unit_price),
           implied_unit_price_p99 = as.numeric(quantile(unit_price, .99)),
           q1_weighted = sum(as.double(q1) * weight_value, na.rm = TRUE),
           q2_weighted = sum(as.double(q2) * weight_value, na.rm = TRUE),
           q3_weighted = sum(as.double(q3) * weight_value, na.rm = TRUE),
           q4_weighted = sum(as.double(q4) * weight_value, na.rm = TRUE))
    }, by = itc]
  }))
  save_table(tail_rows, "quantity_tail_diagnostics.csv")
  rm(tail_items)
  source(file.path(out, "food_coverage.R"), local = environment())
  source(file.path(out, "welfare_diagnostic.R"), local = environment())
  checks$coverage <- lapply(list(consumption = food, durables = durables, transfers = transfers), function(frame) {
    keys <- unique(frame$hhcode)
    list(distinct_households = length(keys), households_missing_info = sum(!keys %in% info$hhcode),
         info_households_missing_module = sum(!info$hhcode %in% keys))
  })
  missing <- rbindlist(list(
    column_counts(food, c("itc", "unit", "pp", "quater", qv), "consumption"),
    column_counts(durables, c("itc", "s7m_a", "s7m_b", "s7m_c"), "durables"),
    column_counts(transfers, c("code", "c02"), "transfers")
  ))
  save_table(missing, "column_missingness.csv")
  save_table(food[, c(list(records = .N, households = uniqueN(hhcode)),
                      lapply(.SD, function(x) sum(as.double(x), na.rm = TRUE))),
                  by = .(itc, unit), .SDcols = qv][order(itc, unit)], "item_unit_totals_raw.csv")
  save_table(food[, .(records = .N, households = uniqueN(hhcode)), by = .(province, region, quater)][order(province, region, quater)],
             "consumption_region_quarter_counts.csv")
  pairs <- rbindlist(lapply(1:4, function(i) {
    q <- food[[paste0("q", i)]]; v <- food[[paste0("v", i)]]
    data.table(pair = i, positive_quantity_missing_or_zero_value = sum(q > 0 & (is.na(v) | v == 0), na.rm = TRUE),
               positive_value_missing_or_zero_quantity = sum(v > 0 & (is.na(q) | q == 0), na.rm = TRUE),
               both_missing = sum(is.na(q) & is.na(v)), both_zero = sum(q == 0 & v == 0, na.rm = TRUE))
  }))
  save_table(pairs, "quantity_value_pair_checks.csv")
  save_table(durables[, .(records = .N, households = uniqueN(hhcode),
                          sum_a = sum(as.double(s7m_a), na.rm = TRUE), sum_b = sum(as.double(s7m_b), na.rm = TRUE),
                          sum_c = sum(as.double(s7m_c), na.rm = TRUE)), by = itc][order(itc)], "durables_code_totals_raw.csv")
  save_table(transfers[, .(records = .N, households = uniqueN(hhcode),
                         sum_c02 = sum(as.double(c02), na.rm = TRUE)), by = code][order(code)], "transfers_code_totals_raw.csv")
  save_json(checks, "cardinality_and_coverage.json")
  save_json(list(
    status = "AGGREGATE_PROFILE_PENDING_PERIOD_UNIT_AND_TABLE23_RECONCILIATION",
    reader = "foreign::read.dta", package_versions = list(foreign = as.character(packageVersion("foreign")),
      data_table = as.character(packageVersion("data.table")), jsonlite = as.character(packageVersion("jsonlite"))),
    public_archive_read_only = TRUE, temporary_original_byte_copies_removed_on_exit = TRUE,
    exported_household_or_person_rows = 0, exported_household_or_person_identifiers = 0,
    nutrient_or_imputation_values_computed = 0, shared_files_written = 0,
    quantity_value_pairs_preserved_in_raw_inventory = TRUE, quantity_channels_summed_only_for_published_table_diagnostics = TRUE, quintiles_reconstructed = FALSE, small_cell_amounts_suppressed_below_households = 5,
    note = "Raw aggregate sums preserve each q/v channel and native reporting periods; not consumption estimates. Schema counts are not final analytical samples. Only selected consumption/roster/design modules read."
  ), "profile_receipt.json")
  cat("Aggregate profile saved; zero household/person rows or identifiers exported.\n")
}

main()
