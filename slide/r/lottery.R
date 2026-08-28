House <- c("Shahjalal (R),", "Surma", "Titumir")

sample(House, 1)

## Lottery prize

lotdf <- data.frame(Prize=1:10, Freq = 1:10,
                    Price = c(10000, 5000, ))
sum(lotdf$Freq)

