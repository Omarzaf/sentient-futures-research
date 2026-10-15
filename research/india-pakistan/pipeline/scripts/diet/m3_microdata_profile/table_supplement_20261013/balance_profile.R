# Bounded schema/aggregate inspection of the public balance supplement only.
suppressPackageStartupMessages(library(data.table))
setDTthreads(2L)

main <- function() {
  root <- normalizePath(getwd())
  out <- file.path(root, "scripts/diet/m3_microdata_profile/table_supplement_20261013")
  archive <- file.path(root, "data/raw/diet/m3-survey-inputs-2026-10-13/health-balance.rar")
  scratch <- tempfile("pbs-balance-read-only-")
  dir.create(scratch)
  on.exit(unlink(scratch, recursive = TRUE), add = TRUE)
  member <- "Out of Pocket Health Exp & Balance sheet/balancesheet.dta"
  result <- system2("bsdtar", c("-xf", shQuote(archive), "-C", shQuote(scratch), shQuote(member)),
                    stdout = TRUE, stderr = TRUE)
  stopifnot(is.null(attr(result, "status")), file.exists(file.path(scratch, member)))
  frame <- foreign::read.dta(file.path(scratch, member), convert.dates = FALSE,
                             convert.factors = FALSE, warn.missing.labels = FALSE)
  schema <- list(rows = nrow(frame), variables = ncol(frame), stata_version = attr(frame, "version"),
                 columns = data.frame(name = names(frame), storage_type = attr(frame, "types"),
                                      label = attr(frame, "var.labels"),
                                      format = attr(frame, "formats")))
  jsonlite::write_json(schema, file.path(out, "balance_schema.json"), pretty = TRUE,
                       auto_unbox = TRUE, na = "null", null = "null", digits = NA)
  setDT(frame)
  stopifnot(!anyDuplicated(frame$hhcode), !anyNA(frame$hhcode))
  main_archive <- file.path(root, "data/raw/diet/m3-reassessment-2026-10-13/pbs-stata-2024-25.zip")
  member_weight <- "Stata data/weight.dta"
  member_info <- "Stata data/section_info.dta"
  unzip(main_archive, files = c(member_weight, member_info), exdir = scratch)
  weights <- as.data.table(foreign::read.dta(file.path(scratch, member_weight), convert.factors = FALSE))
  info <- as.data.table(foreign::read.dta(file.path(scratch, member_info), convert.factors = FALSE))
  stopifnot(!anyDuplicated(weights$prcode), !anyDuplicated(info$hhcode),
            setequal(frame$hhcode, info$hhcode))
  frame <- merge(frame, weights, by = "prcode", all.x = TRUE, sort = FALSE, allow.cartesian = FALSE)
  stopifnot(!anyNA(frame$weight), all(frame$weight > 0))
  geography <- merge(frame[, .(hhcode, province, region)], info[, .(hhcode, province, region)],
                       by = "hhcode", sort = FALSE, allow.cartesian = FALSE)
  stopifnot(all(geography$province.x == geography$province.y), all(geography$region.x == geography$region.y))
  # Expense fields only. No income, health or household-level values are exported.
  fields <- c("sum_v1_1000_a", "sum_v1_2000_b", "sum_v1_4000_c", "sum_v1_5000_d",
              "sum_exp", "z", "sum_v1_6000_sum", "z_e")
  output <- rbindlist(lapply(c("all", "rural", "urban"), function(residence) {
    subset <- if (residence == "all") frame else frame[region == ifelse(residence == "rural", 1, 2)]
    rbindlist(lapply(fields, function(field) {
      value <- subset[[field]]
      data.table(residence = residence, variable = field, households = nrow(subset),
          nonmissing = sum(!is.na(value)), zero = sum(value == 0, na.rm = TRUE),
          negative = sum(value < 0, na.rm = TRUE),
          weighted_observed_sum_per_all_households = sum(as.double(value) * subset$weight, na.rm = TRUE) / sum(subset$weight))
    }))
  }))
  fwrite(output, file.path(out, "balance_expense_aggregate.csv"))
  frame[, stored_four_sum := rowSums(.SD, na.rm = TRUE),
           .SDcols = c("sum_v1_1000_a", "sum_v1_2000_b", "sum_v1_4000_c", "sum_v1_5000_d")]
  frame[, annualized_four_sum := as.double(sum_v1_1000_a) * 26 + as.double(sum_v1_2000_b) * 12 +
                   as.double(sum_v1_4000_c) * 12 + as.double(sum_v1_5000_d)]
  checks <- list(
      balance_households = nrow(frame), unique_household_keys = uniqueN(frame$hhcode),
      key_sets_equal_main_info = TRUE, geography_equal_main_info = TRUE,
      supplied_quintile_named_variables = grep("quint|welfare|percap|deflat", names(frame), value = TRUE, ignore.case = TRUE),
      sum_exp_nonmissing = sum(!is.na(frame$sum_exp)),
      sum_exp_matches_stored_four_field_sum = sum(abs(frame$sum_exp - frame$stored_four_sum) <= 1, na.rm = TRUE),
      sum_exp_matches_annualizing_four_fields = sum(abs(frame$sum_exp - frame$annualized_four_sum) <= 1, na.rm = TRUE),
      z_matches_sum_exp = sum(abs(as.double(frame$z) - frame$sum_exp) <= 1, na.rm = TRUE),
      z_e_matches_z_plus_e = sum(abs(as.double(frame$z_e) - as.double(frame$z) - as.double(frame$sum_v1_6000_sum)) <= 1, na.rm = TRUE),
      health_module_read = FALSE, records_or_identifiers_exported = 0,
      note = "Supplied expense labels describe paid-and-consumed balance checking, not an all-channel welfare/quintile variable. No adjustment applied.")
  jsonlite::write_json(checks, file.path(out, "balance_integrity_checks.json"), pretty = TRUE,
                       auto_unbox = TRUE, na = "null", null = "null", digits = NA)
  cat("Balance aggregate/schema inspection passed; no records or identifiers exported; no health module read.\n")
}
main()
