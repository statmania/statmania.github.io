# Normal Curve

set.seed(25)
x = round(rnorm(10000, 70, 10))
hist(x, prob = TRUE, main = "Histogram & Density Curve",
     xlab = "") 
lines(density(x), col = "red")

# Seat belts data

# Number of drivers killed

sb <- as.data.frame(Seatbelts)
hist(sb$DriversKilled, probability = TRUE, col = "grey", 
     xlab = "# Killed", ylab = "Probability", 
     main = "Number of Drivers killed in UK Accidents in 1969-84")
lines(density(sb$DriversKilled), col = "blue")


# Normal distribution

set.seed(100)
marks <- rnorm(300, mean = 60, sd = 12)
hist(marks, breaks = 12, probability = TRUE, xlim = c(20,100))
lines(density(marks))


# Plot only the density curve
plot(density(marks), main = "Density Plot of Marks", col = "black", lwd = 2)

# Skewed Curve

set.seed(5)

# Right skew

xright <- rbeta(100000,1,100)*1000
hist(xright, prob = TRUE, ylim = c(0,0.1), main = "Histogram & Density Curve")
lines(density(xright), col = "red")

# Left skew

xleft <- rbeta(100000,100,1)*100
hist(xleft, prob = TRUE, main = "Histogram & Density Curve")
lines(density(xleft), col = "red")


# Plot Beta

x = seq(0, 1, length=100)

#create plot of Beta distribution with shape parameters 2 and 10
plot(x, dbeta(x, 2, 10), type='l')



