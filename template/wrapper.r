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
      short_word <- substring(word, 2)
      num <- as.numeric(args[i])
      if (!is.na(num)) {
        # number
        val <- num
      } else {
        # string
        val <- args[i]
      }
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
output_string <- args[3]
id <- args[4]

if (length(args) > 5) {
  args_obj <- parse_args(args[5:length(args)])
} else {
  args_obj <- list()
}

load_file <- function(file, args_obj) {
  csv <- read.csv(file.path("temp", file), header = TRUE)
  split <- strsplit(file, "_", fixed = TRUE)
  name <- paste(split[[1]][1:(length(split[[1]]) - 1)], sep = "_")
  args_obj[[name]] <- csv
  args_obj
}

convert_list <- function(val) {
  val_str <- ""
  i <- 0
  if (is.list(val)) {
    for (name in names(val)) {
      if (i == 0) val_str <- paste0("'", name, "': ", convert_list(val[[name]]))
      else val_str <- sprintf("%s, '%s': %s", val_str, name, convert_list(val[[name]]))
      i <- i + 1
    }
    val_str <- paste0("{", val_str, "}")
  } else if (is.character(val)) {
    for (v in val) {
      if (startsWith(v, "[")) {
        if (i == 0) val_str <- paste0("", v, "")
        else val_str <- sprintf("%s, %s", val_str, v)
      } else {
        if (i == 0) val_str <- paste0("'", v, "'")
        else val_str <- sprintf("%s, '%s'", val_str, v)
      }
      i <- i + 1
    }
  if (length(val) > 1) val_str <- paste0("[", val_str, "]")
  } else if (is.numeric(val)) {
    for (v in val) {
      if (i == 0) val_str <- v
      else val_str <- sprintf("%s, %s", val_str, v)
      i <- i + 1
    }
  if (length(val) > 1) val_str <- paste0("[", val_str, "]")
  } else if (is.logical(val)) {
    for (v in val) {
      if (i == 0) val_str <- if (v == TRUE) "True" else "False"
      else val_str <- sprintf("%s, %s", val_str, if (v == TRUE) "True" else "False")
      i <- i + 1
    }
  }
  val_str
}

if (id != "noid") {
  files <- list.files("./temp", pattern = sprintf("\\s*_%s.csv", id))

  for (i in seq_along(files)) {
    args_obj <- load_file(files[i], args_obj = args_obj)
  }
}

options(warn = -1)
suppressPackageStartupMessages(source(args[1]))
options(warn = 0)
func <- get(method_name)

out_obj <- do.call(func, args_obj)

# format output
output_format <- list()
for (name in strsplit(output_string, ",")[[1]]) {
  key <- strsplit(name, ":")[[1]][1]
  value <- strsplit(name, ":")[[1]][2]
  output_format[key] <- value
}

output <- list()
for (name in names(out_obj)) {
  key <- name
  value <- out_obj[[name]]
  inner_list <- list()
  arg_type <- strsplit(output_format[key][[1]], "\\(")[[1]][1]
  inner_list$type <- arg_type
  if (arg_type == "graph") {
    x_var <- strsplit(
      substring(
                output_format[key],
                7,
                nchar(output_format[key]) - 1),
      "/"
    )[[1]][1]
    y_var <- strsplit(
      substring(
                output_format[key],
                7,
                nchar(output_format[key]) - 1),
      "/"
    )[[1]][2]
    inner_list$labels <- value[x_var][[1]]
    inner_list$values <- value[y_var][[1]]
  } else if (arg_type == "table") {
    d <- list(columns = c("Param", "Value"))
    data <- vector()
    precision <- suppressWarnings(as.integer(strsplit(
      substring(
                output_format[key],
                7,
                nchar(output_format[key]) - 1)
    , "\\|")[[1]]))
    if (!any(is.na(precision))) {
      if (length(precision) != 1 && length(precision) != 2) {
        cat(convert_list(list(error = "Table precision should either be \\'any\\', a single integer between 0 and 6, or an array with an integer for each resulting column.")))
        quit()
      }
      if (length(precision) == 1) {
        precision <- rep(precision, 2)
      }
      for (ele in names(value)) {
        if (is.character(ele)) {
          first_elem <- ele
        } else {
          first_elem <- formatC(ele, format = "f", digits = precision[1])
        }
        if (is.character(value[ele][[1]])) {
          second_elem <- value[ele][[1]]
        } else {
          second_elem <- formatC(value[ele][[1]], format = "f", digits = precision[2])
        }
        data <- c(data, convert_list(c(first_elem, second_elem)))
      }
    } else {
      for (ele in names(value)) {
        data <- c(data, convert_list(c(ele, value[ele][[1]])))
      }
    }
    d$data <- data
    inner_list$table <- d
  } else if (arg_type == "text") {
    inner_list$text <- as.character(value)
  } else if (arg_type == "data_table") {
    inner_list$type <- "table"
    rows <- split(value, seq_len(nrow(value)))
    table <- list(data = vector(), columns = names(value))
    precision <- suppressWarnings(as.integer(strsplit(
      substring(
                output_format[key],
                12,
                nchar(output_format[key]) - 1)
    , "\\|")[[1]]))
    if (!any(is.na(precision))) {
      if (length(precision) != 1 && length(precision) != length(names(value))) {
        cat(convert_list(list(error = "Table precision should either be \\'any\\', a single integer between 0 and 6, or an array with an integer for each resulting column.")))
        quit()
      }
      if (length(precision) == 1) {
        precision <- rep(precision, length(names(values)))
      }
      for (row in rows) {
        new_row <- vector()
        i <- 1
        for (ele in row) {
          if (is.character(ele)) {
            new_row <- c(new_row, ele)
          } else {
            new_row <- c(new_row, formatC(ele, format = "f", digits = precision[i]))
          }
          i <- i + 1
        }
        table$data <- c(table$data, convert_list(new_row))
      }
    } else {
      for (row in rows) {
        new_row <- vector()
        for (ele in row) {
          new_row <- c(new_row, as.character(ele))
        }
        table$data <- c(table$data, convert_list(new_row))
      }
    }
    inner_list$table <- table
  }
  i <- length(output) + 1
  output[[i]] <- inner_list
  names(output)[i] <- key
}

cat(convert_list(output))
