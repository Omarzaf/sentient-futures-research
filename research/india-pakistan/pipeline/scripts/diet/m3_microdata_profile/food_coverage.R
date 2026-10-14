# Called inside main after the cardinality-checked source tables are loaded.
food_inventory <- fread(file.path(out, "food_item_inventory.csv"))
stopifnot(!anyDuplicated(food_inventory$itc), nrow(food_inventory) == 120L)
food_values <- merge(food[, c("hhcode", "itc", qv), with = FALSE],
    food_inventory[, .(itc, recall_days, classification)], by = "itc", all = FALSE,
    sort = FALSE, allow.cartesian = FALSE)
food_values[, any_quantity := rowSums(!is.na(.SD)) > 0L, .SDcols = paste0("q", 1:4)]
food_values[, any_value := rowSums(!is.na(.SD)) > 0L, .SDcols = paste0("v", 1:4)]
food_values[, known_value := rowSums(.SD, na.rm = TRUE), .SDcols = paste0("v", 1:4)]
food_values[, monthly_factor := ifelse(recall_days == 14, 26/12, 1)]
food_values <- merge(food_values, hh[, .(hhcode, region, weight_value)], by = "hhcode",
                     all.x = TRUE, sort = FALSE, allow.cartesian = FALSE)
classified <- rbindlist(lapply(c("all", "rural", "urban"), function(residence) {
  subset <- if (residence == "all") food_values else food_values[region == ifelse(residence == "rural", 1, 2)]
  subset[, .(residence = residence, item_codes_observed = uniqueN(itc), records = .N,
              households = uniqueN(hhcode), records_with_no_quantity_channel = sum(!any_quantity),
              records_with_no_value_channel = sum(!any_value),
              weighted_monthly_observed_value = sum(weight_value * known_value * monthly_factor),
              paid_weighted_monthly_observed_value = sum(weight_value * as.double(v1) * monthly_factor, na.rm = TRUE),
              wage_kind_weighted_monthly_observed_value = sum(weight_value * as.double(v2) * monthly_factor, na.rm = TRUE),
              own_produced_weighted_monthly_observed_value = sum(weight_value * as.double(v3) * monthly_factor, na.rm = TRUE),
              gift_weighted_monthly_observed_value = sum(weight_value * as.double(v4) * monthly_factor, na.rm = TRUE)), by = classification]
}))
save_table(classified, "food_expenditure_coverage_diagnostic.csv")
save_table(classified[, .(prepared_share_observed_food_expenditure =
               weighted_monthly_observed_value[classification == "prepared_food"] /
               sum(weighted_monthly_observed_value[classification != "milling_service"])), by = residence],
           "prepared_food_share_diagnostic.csv")
rm(food_values)
