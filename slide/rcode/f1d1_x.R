
f1d1_x <- function(x) 1/(1-x)

x <- 0.5

f1d1_x(x)

# Mclaurin

f1d1_xmc <- function(x,n) {
  1 + sum(x)
}