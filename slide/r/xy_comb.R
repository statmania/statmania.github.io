x <- c(20, 15, 26, 31, 18)

y <- c(15, 10, 17, 25, 10)

xy <- expand.grid(x,y)

xy

library(dplyr)

xy <- xy %>% mutate(x_y = Var1-Var2) 

sum(xy$x_y)

sum(4*x-6*y)
