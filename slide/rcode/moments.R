fmo <- function(x, r, a) 1/length(x)*sum((x-a)^r)


x=c(56,62,68,71,65,59,74,67,70,63)

fmo(x, 2, mean(x))

