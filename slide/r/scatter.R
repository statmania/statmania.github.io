x1 <- c(10,15, 21, 25, 30)
y1 <- c(8, 13, 18, 23, 28)

plot(x1, y1, pch = 19)

x2 <- c(10, 10, 15, 21, 21, 25, 25, 30)
y2 <- c(8, 12, 17, 18, 23, 20, 26, 32)

plot(x2, y2, pch = 19)

x3 <- c(10, 10, 15, 21, 21, 25, 25, 30)
y3 <- x3 + rnorm(8, 20, 1)

plot(x3, y3, pch = 19)

plot(x2, 30-x2, pch = 19)

x4 <- sample(100, 50)
y4 <- sample(100, 50)

plot(x4, y4, pch = 19)

par(mfrow = c(2,2))
dev.off()

# Set up plotting area (2x2 grid)
par(mfrow = c(2, 2))

# Set seed for reproducibility
set.seed(123)

# Sample size
n <- 100

# 1. Very strong positive correlation (r ~ 0.98)
x1 <- rnorm(n, mean = 50, sd = 10)
y1 <- 30 + 1.2 * x1 + rnorm(n, mean = 0, sd = 3)
plot(x1, y1, main = "Very Strong Positive (r ≈ 0.98)", 
     xlab = "X", ylab = "Y", pch = 19, col = "blue")

# 2. Moderate positive (r ≈ 0.92) – still strong but realistic
x2 <- rnorm(n, mean = 50, sd = 10)
y2 <- 25 + 0.9 * x2 + rnorm(n, mean = 0, sd = 5)
plot(x2, y2, main = "Strong Positive (r ≈ 0.92)", 
     xlab = "X", ylab = "Y", pch = 19, col = "green")

# 3. Very strong negative correlation (r ≈ -0.97)
x3 <- rnorm(n, mean = 50, sd = 10)
y3 <- 100 - 1.1 * x3 + rnorm(n, mean = 0, sd = 3.5)
plot(x3, y3, main = "Very Strong Negative (r ≈ -0.97)", 
     xlab = "X", ylab = "Y", pch = 19, col = "red")

# 4. Near perfect correlation (r ≈ 0.99)
x4 <- rnorm(n, mean = 50, sd = 10)
y4 <- 10 + 1.5 * x4 + rnorm(n, mean = 0, sd = 1.5)
plot(x4, y4, main = "Near Perfect (r ≈ 0.99)", 
     xlab = "X", ylab = "Y", pch = 19, col = "purple")

# Display correlation coefficients
cat("Correlation coefficients:\n")
cat("1. Very strong positive:", round(cor(x1, y1), 4), "\n")
cat("2. Strong positive:", round(cor(x2, y2), 4), "\n")
cat("3. Very strong negative:", round(cor(x3, y3), 4), "\n")
cat("4. Near perfect positive:", round(cor(x4, y4), 4), "\n")

library(ggplot2)
library(patchwork)

# Create a single data frame with all datasets
df_all <- data.frame(
  x = c(x1, x2, x3, x4),
  y = c(y1, y2, y3, y4),
  type = rep(c("A", "B", "C", "D"), each = n)
)

# Create plots using facet_wrap
p <- ggplot(df_all, aes(x = x, y = y)) +
  geom_point() +
  facet_wrap(~ type, ncol = 2) +
#  theme_minimal() +
  labs(title = "", x= "", y = "")

print(p)
