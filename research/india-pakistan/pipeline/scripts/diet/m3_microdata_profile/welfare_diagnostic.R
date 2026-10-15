# Compare source-defined balance-sheet variants; none is assumed to be welfare.
subtotal <- merge(subtotal, hh[, .(hhcode, region, weight_value)], by = "hhcode",
                    all.x = TRUE, sort = FALSE, allow.cartesian = FALSE)
component_rows <- rbindlist(lapply(c("all", "rural", "urban"), function(residence) {
  people <- if (residence == "all") hh else hh[region == ifelse(residence == "rural", 1, 2)]
  subset <- if (residence == "all") subtotal else subtotal[region == ifelse(residence == "rural", 1, 2)]
  denominator <- sum(people$weight_value)
  subset[, .(residence = residence, households = .N,
       paid_monthly_mean = sum(as.double(v1) * monthly_factor * weight_value, na.rm = TRUE) / denominator,
       wage_kind_monthly_mean = sum(as.double(v2) * monthly_factor * weight_value, na.rm = TRUE) / denominator,
       own_produced_monthly_mean = sum(as.double(v3) * monthly_factor * weight_value, na.rm = TRUE) / denominator,
       gift_monthly_mean = sum(as.double(v4) * monthly_factor * weight_value, na.rm = TRUE) / denominator,
       all_channels_monthly_mean = sum(reported_value_sum * monthly_factor * weight_value) / denominator),
       by = .(part, itc, monthly_factor)]
}))
save_table(component_rows, "welfare_component_channel_diagnostic.csv")
variant_rows <- component_rows[, .(
     source_paid_balance_A_to_D = sum(paid_monthly_mean[part != "E"]),
     source_paid_balance_A_to_E = sum(paid_monthly_mean),
     all_channel_A_to_D = sum(all_channels_monthly_mean[part != "E"]),
     all_channel_A_to_E = sum(all_channels_monthly_mean)), by = residence]
variant_rows[, report_monthly_household_consumption :=
              fifelse(residence == "all", 79150, fifelse(residence == "rural", 67894, 95533))]
save_table(variant_rows, "welfare_source_variant_diagnostic.csv")

# Explicit page-total relationships from female pp21/24 and male p21.
page_map <- data.table(itc = c(1001L, 1002L, 1003L, 2001L, 2002L, 2003L,
                               5001L, 5002L, 5003L, 5004L),
                      parent_total = c(rep(1000L, 3), rep(2000L, 3), rep(5000L, 4)))
page_values <- merge(food[itc %in% page_map$itc, c("hhcode", "itc", paste0("v", 1:4)), with = FALSE],
                        page_map, by = "itc", sort = FALSE, allow.cartesian = FALSE)
pages <- page_values[, c(list(pages_recorded = .N), lapply(.SD, function(x) sum(as.double(x), na.rm = TRUE))),
                       by = .(hhcode, parent_total), .SDcols = paste0("v", 1:4)]
totals <- food[itc %in% c(1000L, 2000L, 5000L), c("hhcode", "itc", paste0("v", 1:4)), with = FALSE]
setnames(totals, c("itc", paste0("v", 1:4)), c("parent_total", paste0("total_v", 1:4)))
page_check <- merge(pages, totals, by = c("hhcode", "parent_total"), all = TRUE,
                       sort = FALSE, allow.cartesian = FALSE)
page_check <- merge(page_check, hh[, .(hhcode, weight_value)], by = "hhcode", all.x = TRUE,
                       sort = FALSE, allow.cartesian = FALSE)
page_checks <- rbindlist(lapply(1:4, function(channel) {
  page_check[, {
    x <- get(paste0("v", channel)); y <- get(paste0("total_v", channel))
    both <- !is.na(x) & !is.na(y)
    list(channel = channel, households = .N, both_observed = sum(both),
       only_page_values_present = sum(!is.na(x) & is.na(y)),
       only_parent_value_present = sum(is.na(x) & !is.na(y)),
       nonzero_differences_both_observed = sum(abs(x[both] - y[both]) > 0.01),
       weighted_parent_minus_pages_both_observed = sum((y[both] - x[both]) * weight_value[both]))
  }, by = parent_total]
}))
save_table(page_checks, "page_to_parent_subtotal_diagnostic.csv")

# Form page boundaries map every actual non-total item to one part.
form_parts <- fread(file.path(out, "form_item_part_mapping.csv"))
stopifnot(!anyDuplicated(form_parts$itc), nrow(form_parts) == 285L,
          setequal(unique(food$itc), c(form_parts$itc, 1000L, 2000L, 4000L, 5000L, 6000L)))
detail <- merge(food[, c("hhcode", "itc", paste0("v", 1:4)), with = FALSE],
                    form_parts[, .(itc, part)], by = "itc", all = FALSE,
                    sort = FALSE, allow.cartesian = FALSE)
detail[, observed_value := rowSums(.SD, na.rm = TRUE), .SDcols = paste0("v", 1:4)]
detail <- detail[, .(detail_value = sum(observed_value), item_records = .N), by = .(hhcode, part)]
part_match <- merge(detail, subtotal[, .(hhcode, part, parent_value = reported_value_sum)],
                     by = c("hhcode", "part"), all = TRUE, sort = FALSE, allow.cartesian = FALSE)
part_match <- merge(part_match, hh[, .(hhcode, region, weight_value)], by = "hhcode",
                     all.x = TRUE, sort = FALSE, allow.cartesian = FALSE)
part_match <- merge(part_match, parts[, .(part, monthly_factor)], by = "part",
                     all.x = TRUE, sort = FALSE, allow.cartesian = FALSE)
detail_rows <- rbindlist(lapply(c("all", "rural", "urban"), function(residence) {
  people <- if (residence == "all") hh else hh[region == ifelse(residence == "rural", 1, 2)]
  subset <- if (residence == "all") part_match else part_match[region == ifelse(residence == "rural", 1, 2)]
  denominator <- sum(people$weight_value)
  subset[, .(residence = residence, households = .N,
       only_detail_present = sum(!is.na(detail_value) & is.na(parent_value)),
       only_parent_present = sum(is.na(detail_value) & !is.na(parent_value)),
       both_observed_differences = sum(abs(detail_value - parent_value) > .01, na.rm = TRUE),
       detail_monthly_weighted_mean = sum(detail_value * weight_value * monthly_factor, na.rm = TRUE) / denominator,
       parent_monthly_weighted_mean = sum(parent_value * weight_value * monthly_factor, na.rm = TRUE) / denominator), by = part]
}))
save_table(detail_rows, "detail_to_parent_subtotal_diagnostic.csv")
