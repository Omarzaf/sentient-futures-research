# Independently read the official SPSS edition; write aggregate cells only.
args <- commandArgs(trailingOnly = TRUE)
stopifnot(length(args) == 2L)
archive <- normalizePath(args[1], mustWork = TRUE)
destination <- args[2]
scratch <- tempfile("pbs-spss-check-")
dir.create(scratch)

main <- function() {
  on.exit(unlink(scratch, recursive = TRUE), add = TRUE)
  read_source <- function(member) {
    target <- unzip(archive, files = member, exdir = scratch)
    value <- foreign::read.spss(target, use.value.labels = FALSE,
                              to.data.frame = TRUE, use.missings = TRUE)
    names(value) <- tolower(names(value))
    value
  }
  info <- read_source("SPSS data/section_info.sav")
  roster <- read_source("SPSS data/plist_roster.sav")
  weights <- read_source("SPSS data/weight.sav")
  food <- read_source("SPSS data/Sec 6a-consum-Exp.sav")
  stopifnot(!anyDuplicated(info$hhcode), !anyDuplicated(weights$prcode),
            !anyDuplicated(roster[, c("hhcode", "idc")]),
            all(roster$s1aq10 %in% c(1, 2)), all(weights$weight > 0))
  members <- aggregate(as.integer(roster$s1aq10 == 1),
                       by = list(hhcode = roster$hhcode), FUN = sum)
  names(members)[2] <- "members"
  hh <- merge(info[, c("hhcode", "prcode", "region")], members,
              by = "hhcode", all.x = TRUE, sort = FALSE)
  hh <- merge(hh, weights[, c("prcode", "weight")], by = "prcode",
              all.x = TRUE, sort = FALSE)
  stopifnot(nrow(hh) == nrow(info), !anyNA(hh$weight), all(hh$members > 0))
  chicken <- food[food$itc == 11203, c("hhcode", "q1", "q2", "q3", "q4")]
  stopifnot(!anyDuplicated(chicken$hhcode),
            all(as.matrix(chicken[, -1]) >= 0, na.rm = TRUE))
  chicken$quantity <- rowSums(chicken[, c("q1", "q2", "q3", "q4")], na.rm = TRUE)
  missing <- rowSums(!is.na(chicken[, c("q1", "q2", "q3", "q4")])) == 0L
  stopifnot(!any(missing))
  hh <- merge(hh, chicken[, c("hhcode", "quantity")], by = "hhcode",
              all.x = TRUE, sort = FALSE)
  out <- do.call(rbind, lapply(c("all", "rural", "urban"), function(residence) {
    x <- if (residence == "all") hh else hh[hh$region == ifelse(residence == "rural", 1, 2), ]
    numerator <- sum(x$weight * x$quantity, na.rm = TRUE)
    denominator <- sum(x$weight * x$members)
    data.frame(residence = residence, households = nrow(x),
               psus = length(unique(x$prcode)),
               weighted_recall_kg_numerator = numerator,
               weighted_person_denominator = denominator,
               estimate_kg_person_month = numerator * 30 / 14 / denominator)
  }))
  options(digits = 17)
  write.table(out, destination, sep = ",", row.names = FALSE, quote = TRUE)
  cat("PASS: independent SPSS all-source reader; respondent rows exported=0; foreign=",
      as.character(utils::packageVersion("foreign")), "\n", sep = "")
}

main()
