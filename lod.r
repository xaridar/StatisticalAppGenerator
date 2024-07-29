library(dplyr)

lod_calc <- function(n, cv, beta, k) {
  if (cv == 0) {
    return(-log(beta) / (n * k))
  }
  d <- 1 / cv ^ 2
  ((d / beta ^ (1 / (n * d))) - d) / k
}

calc <- function(cv, beta, k, threshold, arr) {
  lod <- data.frame(n = seq(from = 1, to = 1000, by = 1))
  lod <- mutate(lod, LOD = sapply(lod$n, lod_calc, cv = cv, beta = beta, k = k))
  lod <- mutate(lod, LOD2 = sapply(lod$n, lod_calc, cv = 0, beta = beta, k = k))

  table <- list()
  below_threshold <- lod[lod$LOD < threshold, ]
  if (length(below_threshold[[1]]) == 0) {
    table["Minimum n"] <- "> 1000"
  } else {
    table["Minimum n"] <- below_threshold[1, ]$n
    table["LOD"] <- below_threshold[1, ]$LOD
  }
  ret <- list()
  ret$Graph <- lod[lod$n <= 50, ]
  ret$Graph1 <- lod[lod$n <= 50, ]
  ret$Table <- table
  ret$Table2 <- lod[lod$n <= 10, ]
  ret$Text <- "test"
  ret
}