parse_args <- function(args) {
  obj <- list()
  i <- 1
  n <- 1
  while (i <= length(args)) {
    word <- args[i]
    if (startsWith(word, "--")) {
      # true
      short_word <- substring(word, 3)
      val <- TRUE
    } else if (startsWith(word, "-!")) {
      # true
      short_word <- substring(word, 3)
      val <- FALSE
    } else if (startsWith(word, "-")) {
      i <- i + 1
      # string
      short_word <- substring(word, 2)
      val <- args[i]
    }
    obj[[short_word]] <- val
    i <- i + 1
    n <- n + 1
  }
  obj
}

args <- commandArgs(trailingOnly = TRUE)
filename <- args[1]
method_name <- args[2]
id <- args[3]

if (length(args) > 4) {
  args_obj <- parse_args(args[4:length(args)])
} else {
  args_obj <- list()
}

load_file <- function(file, files_obj) {
  csv <- read.csv(file.path("temp", file), header = TRUE)
  split <- strsplit(file, "_", fixed = TRUE)
  name <- paste(split[[1]][1:(length(split[[1]]) - 1)], sep = "_")
  files_obj[[name]] <- csv
  files_obj
}

files <- list.files("./temp", pattern = sprintf("\\s*_%s.csv", id))

# bind 'files' dataframe
files_obj <- list()
for (i in seq_along(files)) {
  files_obj <- load_file(files[i], files_obj = files_obj)
}

args_obj$files <- files_obj

source(args[1])
func <- get(method_name)

print(func(args_obj))