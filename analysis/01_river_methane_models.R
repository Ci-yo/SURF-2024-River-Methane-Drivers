# Base-R analysis of geographic and hydrological methane-flux drivers.
# Run from the repository root: Rscript analysis/01_river_methane_models.R

dir.create("results", showWarnings = FALSE)
dat <- read.csv("data/grime_curated.csv", check.names = FALSE)
flux <- dat$Diffusive_CH4_Flux_Mean
positive <- is.finite(flux) & flux > 0
limits <- quantile(flux[positive], c(0.05, 0.95), na.rm = TRUE)
clean <- dat[positive & flux >= limits[1] & flux <= limits[2], ]
clean$log_flux <- log(clean$Diffusive_CH4_Flux_Mean)
clean$log_elevation <- log1p(clean$Elevation_m)
clean$log_slope <- log1p(clean$Slope_m_per_m)
clean$log_basin <- log1p(clean$Basin_size_km2)

models <- list(
  geography = lm(log_flux ~ Latitude + Longitude + log_elevation, data = clean),
  river_network = lm(log_flux ~ log_slope + Strahler_order + log_basin, data = clean)
)

tidy_coefs <- function(name, model) {
  tab <- coef(summary(model))
  data.frame(model = name, term = rownames(tab), estimate = tab[, 1],
             std_error = tab[, 2], statistic = tab[, 3], p_value = tab[, 4],
             row.names = NULL)
}
coefs <- do.call(rbind, Map(tidy_coefs, names(models), models))
write.csv(coefs, "results/model_coefficients.csv", row.names = FALSE)

diagnostics <- data.frame(
  model = names(models),
  n = sapply(models, nobs),
  r_squared = sapply(models, function(m) summary(m)$r.squared),
  adjusted_r_squared = sapply(models, function(m) summary(m)$adj.r.squared)
)
write.csv(diagnostics, "results/model_diagnostics.csv", row.names = FALSE)
print(diagnostics)
