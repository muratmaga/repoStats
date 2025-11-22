#!/usr/bin/env Rscript
# Plot SlicerMorph repository statistics over time

# Load required libraries
library(jsonlite)
library(ggplot2)
library(dplyr)
library(lubridate)

# Read the JSON data from the GitHub URL
url <- "https://raw.githubusercontent.com/muratmaga/repoStats/main/SlicerMorph.json"

# The file contains multiple JSON objects appended together
# We need to extract all of them and combine the views
raw_json <- readLines(url, warn = FALSE)
json_text <- paste(raw_json, collapse = "")

# Split by "}{"  to separate multiple JSON objects
json_objects <- strsplit(json_text, "\\}\\{")[[1]]

# Reconstruct each JSON object by adding back the braces
for (i in seq_along(json_objects)) {
  if (i == 1) {
    json_objects[i] <- paste0(json_objects[i], "}")
  } else if (i == length(json_objects)) {
    json_objects[i] <- paste0("{", json_objects[i])
  } else {
    json_objects[i] <- paste0("{", json_objects[i], "}")
  }
}

# Parse all JSON objects and combine the views
all_views <- list()
for (json_obj in json_objects) {
  data_obj <- fromJSON(json_obj)
  all_views[[length(all_views) + 1]] <- data_obj$views
}

# Combine all views into a single data frame
views_df <- bind_rows(all_views)

# Remove duplicate dates (keep the most recent data for each date)
views_df <- views_df %>%
  group_by(timestamp) %>%
  slice_tail(n = 1) %>%
  ungroup()

# Calculate cumulative totals across all historical data
total_cumulative_views <- sum(views_df$count)
total_cumulative_uniques <- sum(views_df$uniques)

# Use the last JSON object for reference (but we'll use our calculated totals)
data <- fromJSON(json_objects[length(json_objects)])
# Override with our calculated cumulative totals
data$count <- total_cumulative_views
data$uniques <- total_cumulative_uniques

# Convert timestamp to Date object
views_df$date <- as.Date(views_df$timestamp)

# Calculate average daily views
avg_daily_count <- mean(views_df$count)
avg_daily_uniques <- mean(views_df$uniques)

# Create a plot with both count and uniques
p1 <- ggplot(views_df, aes(x = date)) +
  geom_line(aes(y = count, color = "Total Views"), size = 1) +
  geom_point(aes(y = count, color = "Total Views"), size = 2) +
  geom_line(aes(y = uniques, color = "Unique Visitors"), size = 1) +
  geom_point(aes(y = uniques, color = "Unique Visitors"), size = 2) +
  geom_hline(aes(yintercept = avg_daily_count, linetype = "Avg Total Views"), 
             color = "#2E86AB", alpha = 0.7, size = 0.8) +
  geom_hline(aes(yintercept = avg_daily_uniques, linetype = "Avg Unique Visitors"), 
             color = "#A23B72", alpha = 0.7, size = 0.8) +
  scale_color_manual(values = c("Total Views" = "#2E86AB", 
                                 "Unique Visitors" = "#A23B72"),
                     labels = c(paste0("Total Views (Cumulative: ", data$count, ")"),
                               paste0("Unique Visitors (Cumulative: ", data$uniques, ")"))) +
  scale_linetype_manual(name = "Averages",
                        values = c("Avg Total Views" = "dashed",
                                  "Avg Unique Visitors" = "dashed"),
                        labels = c(paste0("Avg Total Views (", round(avg_daily_count, 1), ")"),
                                  paste0("Avg Unique Visitors (", round(avg_daily_uniques, 1), ")"))) +
  labs(title = "SlicerMorph Repository Views Over Time",
       subtitle = paste0("Total: ", data$count, " views from ", 
                        data$uniques, " unique visitors"),
       x = "Date",
       y = "Number of Views",
       color = "Metric") +
  theme_minimal() +
  theme(legend.position = "bottom",
        plot.title = element_text(size = 14, face = "bold"),
        plot.subtitle = element_text(size = 10))

# Save the plot
ggsave("slicermorph_views.png", p1, width = 10, height = 6, dpi = 300)

# Create a second plot showing daily growth rate
views_df <- views_df %>%
  arrange(date) %>%
  mutate(count_change = count - lag(count, default = 0),
         unique_change = uniques - lag(uniques, default = 0))

p2 <- ggplot(views_df, aes(x = date)) +
  geom_col(aes(y = count_change, fill = "Daily Total Views Change")) +
  geom_line(aes(y = unique_change, color = "Daily Unique Visitors Change"), 
            size = 1) +
  geom_point(aes(y = unique_change, color = "Daily Unique Visitors Change"), 
             size = 2) +
  scale_fill_manual(values = c("Daily Total Views Change" = "#A7C7E7")) +
  scale_color_manual(values = c("Daily Unique Visitors Change" = "#FF6B35")) +
  labs(title = "SlicerMorph Repository - Daily Changes",
       x = "Date",
       y = "Change in Views/Visitors",
       fill = "",
       color = "") +
  theme_minimal() +
  theme(legend.position = "bottom",
        plot.title = element_text(size = 14, face = "bold"))

# Save the second plot
ggsave("slicermorph_changes.png", p2, width = 10, height = 6, dpi = 300)

# Print summary statistics
cat("\n=== SlicerMorph Repository Statistics Summary ===\n")
cat(sprintf("Total Views: %d\n", data$count))
cat(sprintf("Unique Visitors: %d\n", data$uniques))
cat(sprintf("Date Range: %s to %s\n", 
            min(views_df$date), max(views_df$date)))
cat(sprintf("Average Daily Views: %.1f\n", mean(views_df$count)))
cat(sprintf("Average Daily Unique Visitors: %.1f\n", mean(views_df$uniques)))
cat(sprintf("Peak Daily Views: %d (on %s)\n", 
            max(views_df$count), 
            views_df$date[which.max(views_df$count)]))
cat(sprintf("Peak Daily Unique Visitors: %d (on %s)\n", 
            max(views_df$uniques), 
            views_df$date[which.max(views_df$uniques)]))

cat("\nPlots saved as:\n")
cat("  - slicermorph_views.png\n")
cat("  - slicermorph_changes.png\n")

# ============================================================================
# Process Tutorials Repository
# ============================================================================

cat("\n\n=================================================\n")
cat("Processing Tutorials Repository...\n")
cat("=================================================\n")

# Read the Tutorials JSON data
url_tutorials <- "https://raw.githubusercontent.com/muratmaga/repoStats/main/Tutorials.json"

raw_json_tutorials <- readLines(url_tutorials, warn = FALSE)
json_text_tutorials <- paste(raw_json_tutorials, collapse = "")

# Split by "}{"  to separate multiple JSON objects
json_objects_tutorials <- strsplit(json_text_tutorials, "\\}\\{")[[1]]

# Reconstruct each JSON object by adding back the braces
for (i in seq_along(json_objects_tutorials)) {
  if (i == 1) {
    json_objects_tutorials[i] <- paste0(json_objects_tutorials[i], "}")
  } else if (i == length(json_objects_tutorials)) {
    json_objects_tutorials[i] <- paste0("{", json_objects_tutorials[i])
  } else {
    json_objects_tutorials[i] <- paste0("{", json_objects_tutorials[i], "}")
  }
}

# Parse all JSON objects and combine the views
all_views_tutorials <- list()
for (json_obj in json_objects_tutorials) {
  data_obj <- fromJSON(json_obj)
  all_views_tutorials[[length(all_views_tutorials) + 1]] <- data_obj$views
}

# Combine all views into a single data frame
views_df_tutorials <- bind_rows(all_views_tutorials)

# Remove duplicate dates (keep the most recent data for each date)
views_df_tutorials <- views_df_tutorials %>%
  group_by(timestamp) %>%
  slice_tail(n = 1) %>%
  ungroup()

# Calculate cumulative totals across all historical data
total_cumulative_views_tutorials <- sum(views_df_tutorials$count)
total_cumulative_uniques_tutorials <- sum(views_df_tutorials$uniques)

# Use the last JSON object for reference
data_tutorials <- fromJSON(json_objects_tutorials[length(json_objects_tutorials)])
data_tutorials$count <- total_cumulative_views_tutorials
data_tutorials$uniques <- total_cumulative_uniques_tutorials

# Convert timestamp to Date object
views_df_tutorials$date <- as.Date(views_df_tutorials$timestamp)

# Calculate average daily views
avg_daily_count_tutorials <- mean(views_df_tutorials$count)
avg_daily_uniques_tutorials <- mean(views_df_tutorials$uniques)

# Create a plot with both count and uniques for Tutorials
p3 <- ggplot(views_df_tutorials, aes(x = date)) +
  geom_line(aes(y = count, color = "Total Views"), size = 1) +
  geom_point(aes(y = count, color = "Total Views"), size = 2) +
  geom_line(aes(y = uniques, color = "Unique Visitors"), size = 1) +
  geom_point(aes(y = uniques, color = "Unique Visitors"), size = 2) +
  geom_hline(aes(yintercept = avg_daily_count_tutorials, linetype = "Avg Total Views"), 
             color = "#2E86AB", alpha = 0.7, size = 0.8) +
  geom_hline(aes(yintercept = avg_daily_uniques_tutorials, linetype = "Avg Unique Visitors"), 
             color = "#A23B72", alpha = 0.7, size = 0.8) +
  scale_color_manual(values = c("Total Views" = "#2E86AB", 
                                 "Unique Visitors" = "#A23B72"),
                     labels = c(paste0("Total Views (Cumulative: ", data_tutorials$count, ")"),
                               paste0("Unique Visitors (Cumulative: ", data_tutorials$uniques, ")"))) +
  scale_linetype_manual(name = "Averages",
                        values = c("Avg Total Views" = "dashed",
                                  "Avg Unique Visitors" = "dashed"),
                        labels = c(paste0("Avg Total Views (", round(avg_daily_count_tutorials, 1), ")"),
                                  paste0("Avg Unique Visitors (", round(avg_daily_uniques_tutorials, 1), ")"))) +
  labs(title = "Tutorials Repository Views Over Time",
       subtitle = paste0("Total: ", data_tutorials$count, " views from ", 
                        data_tutorials$uniques, " unique visitors"),
       x = "Date",
       y = "Number of Views",
       color = "Metric") +
  theme_minimal() +
  theme(legend.position = "bottom",
        plot.title = element_text(size = 14, face = "bold"),
        plot.subtitle = element_text(size = 10))

# Save the plot
ggsave("tutorials_views.png", p3, width = 10, height = 6, dpi = 300)

# Create a second plot showing daily growth rate for Tutorials
views_df_tutorials <- views_df_tutorials %>%
  arrange(date) %>%
  mutate(count_change = count - lag(count, default = 0),
         unique_change = uniques - lag(uniques, default = 0))

p4 <- ggplot(views_df_tutorials, aes(x = date)) +
  geom_col(aes(y = count_change, fill = "Daily Total Views Change")) +
  geom_line(aes(y = unique_change, color = "Daily Unique Visitors Change"), 
            size = 1) +
  geom_point(aes(y = unique_change, color = "Daily Unique Visitors Change"), 
             size = 2) +
  scale_fill_manual(values = c("Daily Total Views Change" = "#A7C7E7")) +
  scale_color_manual(values = c("Daily Unique Visitors Change" = "#FF6B35")) +
  labs(title = "Tutorials Repository - Daily Changes",
       x = "Date",
       y = "Change in Views/Visitors",
       fill = "",
       color = "") +
  theme_minimal() +
  theme(legend.position = "bottom",
        plot.title = element_text(size = 14, face = "bold"))

# Save the second plot
ggsave("tutorials_changes.png", p4, width = 10, height = 6, dpi = 300)

# Print summary statistics for Tutorials
cat("\n=== Tutorials Repository Statistics Summary ===\n")
cat(sprintf("Total Views: %d\n", data_tutorials$count))
cat(sprintf("Unique Visitors: %d\n", data_tutorials$uniques))
cat(sprintf("Date Range: %s to %s\n", 
            min(views_df_tutorials$date), max(views_df_tutorials$date)))
cat(sprintf("Average Daily Views: %.1f\n", mean(views_df_tutorials$count)))
cat(sprintf("Average Daily Unique Visitors: %.1f\n", mean(views_df_tutorials$uniques)))
cat(sprintf("Peak Daily Views: %d (on %s)\n", 
            max(views_df_tutorials$count), 
            views_df_tutorials$date[which.max(views_df_tutorials$count)]))
cat(sprintf("Peak Daily Unique Visitors: %d (on %s)\n", 
            max(views_df_tutorials$uniques), 
            views_df_tutorials$date[which.max(views_df_tutorials$uniques)]))

cat("\nPlots saved as:\n")
cat("  - tutorials_views.png\n")
cat("  - tutorials_changes.png\n")

# ============================================================================
# Process MCI Repository
# ============================================================================

cat("\n\n=================================================\n")
cat("Processing MCI Repository...\n")
cat("=================================================\n")

# Read the MCI JSON data
url_mci <- "https://raw.githubusercontent.com/muratmaga/repoStats/main/MCI.json"

raw_json_mci <- readLines(url_mci, warn = FALSE)
json_text_mci <- paste(raw_json_mci, collapse = "")

# Split by "}{"  to separate multiple JSON objects
json_objects_mci <- strsplit(json_text_mci, "\\}\\{")[[1]]

# Reconstruct each JSON object by adding back the braces
for (i in seq_along(json_objects_mci)) {
  if (i == 1) {
    json_objects_mci[i] <- paste0(json_objects_mci[i], "}")
  } else if (i == length(json_objects_mci)) {
    json_objects_mci[i] <- paste0("{", json_objects_mci[i])
  } else {
    json_objects_mci[i] <- paste0("{", json_objects_mci[i], "}")
  }
}

# Parse all JSON objects and combine the views
all_views_mci <- list()
for (json_obj in json_objects_mci) {
  data_obj <- fromJSON(json_obj)
  all_views_mci[[length(all_views_mci) + 1]] <- data_obj$views
}

# Combine all views into a single data frame
views_df_mci <- bind_rows(all_views_mci)

# Remove duplicate dates (keep the most recent data for each date)
views_df_mci <- views_df_mci %>%
  group_by(timestamp) %>%
  slice_tail(n = 1) %>%
  ungroup()

# Calculate cumulative totals across all historical data
total_cumulative_views_mci <- sum(views_df_mci$count)
total_cumulative_uniques_mci <- sum(views_df_mci$uniques)

# Use the last JSON object for reference
data_mci <- fromJSON(json_objects_mci[length(json_objects_mci)])
data_mci$count <- total_cumulative_views_mci
data_mci$uniques <- total_cumulative_uniques_mci

# Convert timestamp to Date object
views_df_mci$date <- as.Date(views_df_mci$timestamp)

# Calculate average daily views
avg_daily_count_mci <- mean(views_df_mci$count)
avg_daily_uniques_mci <- mean(views_df_mci$uniques)

# Create a plot with both count and uniques for MCI
p5 <- ggplot(views_df_mci, aes(x = date)) +
  geom_line(aes(y = count, color = "Total Views"), size = 1) +
  geom_point(aes(y = count, color = "Total Views"), size = 2) +
  geom_line(aes(y = uniques, color = "Unique Visitors"), size = 1) +
  geom_point(aes(y = uniques, color = "Unique Visitors"), size = 2) +
  geom_hline(aes(yintercept = avg_daily_count_mci, linetype = "Avg Total Views"), 
             color = "#2E86AB", alpha = 0.7, size = 0.8) +
  geom_hline(aes(yintercept = avg_daily_uniques_mci, linetype = "Avg Unique Visitors"), 
             color = "#A23B72", alpha = 0.7, size = 0.8) +
  scale_color_manual(values = c("Total Views" = "#2E86AB", 
                                 "Unique Visitors" = "#A23B72"),
                     labels = c(paste0("Total Views (Cumulative: ", data_mci$count, ")"),
                               paste0("Unique Visitors (Cumulative: ", data_mci$uniques, ")"))) +
  scale_linetype_manual(name = "Averages",
                        values = c("Avg Total Views" = "dashed",
                                  "Avg Unique Visitors" = "dashed"),
                        labels = c(paste0("Avg Total Views (", round(avg_daily_count_mci, 1), ")"),
                                  paste0("Avg Unique Visitors (", round(avg_daily_uniques_mci, 1), ")"))) +
  labs(title = "MCI Repository Views Over Time",
       subtitle = paste0("Total: ", data_mci$count, " views from ", 
                        data_mci$uniques, " unique visitors"),
       x = "Date",
       y = "Number of Views",
       color = "Metric") +
  theme_minimal() +
  theme(legend.position = "bottom",
        plot.title = element_text(size = 14, face = "bold"),
        plot.subtitle = element_text(size = 10))

# Save the plot
ggsave("mci_views.png", p5, width = 10, height = 6, dpi = 300)

# Create a second plot showing daily growth rate for MCI
views_df_mci <- views_df_mci %>%
  arrange(date) %>%
  mutate(count_change = count - lag(count, default = 0),
         unique_change = uniques - lag(uniques, default = 0))

p6 <- ggplot(views_df_mci, aes(x = date)) +
  geom_col(aes(y = count_change, fill = "Daily Total Views Change")) +
  geom_line(aes(y = unique_change, color = "Daily Unique Visitors Change"), 
            size = 1) +
  geom_point(aes(y = unique_change, color = "Daily Unique Visitors Change"), 
             size = 2) +
  scale_fill_manual(values = c("Daily Total Views Change" = "#A7C7E7")) +
  scale_color_manual(values = c("Daily Unique Visitors Change" = "#FF6B35")) +
  labs(title = "MCI Repository - Daily Changes",
       x = "Date",
       y = "Change in Views/Visitors",
       fill = "",
       color = "") +
  theme_minimal() +
  theme(legend.position = "bottom",
        plot.title = element_text(size = 14, face = "bold"))

# Save the second plot
ggsave("mci_changes.png", p6, width = 10, height = 6, dpi = 300)

# Print summary statistics for MCI
cat("\n=== MCI Repository Statistics Summary ===\n")
cat(sprintf("Total Views: %d\n", data_mci$count))
cat(sprintf("Unique Visitors: %d\n", data_mci$uniques))
cat(sprintf("Date Range: %s to %s\n", 
            min(views_df_mci$date), max(views_df_mci$date)))
cat(sprintf("Average Daily Views: %.1f\n", mean(views_df_mci$count)))
cat(sprintf("Average Daily Unique Visitors: %.1f\n", mean(views_df_mci$uniques)))
cat(sprintf("Peak Daily Views: %d (on %s)\n", 
            max(views_df_mci$count), 
            views_df_mci$date[which.max(views_df_mci$count)]))
cat(sprintf("Peak Daily Unique Visitors: %d (on %s)\n", 
            max(views_df_mci$uniques), 
            views_df_mci$date[which.max(views_df_mci$uniques)]))

cat("\nPlots saved as:\n")
cat("  - mci_views.png\n")
cat("  - mci_changes.png\n")
