pw <- c()

for (i in 1:54){
  pw <- c(pw,paste(sample(LETTERS, 1),sample(9,1), 
                   sample(LETTERS, 1),sample(9,1), 
                   sample(LETTERS, 1))
  )
}
pw



write.csv(pw, file = "pw.csv")


paste(sample(c(LETTERS, letters, 0:9), 5), collapse = "")



Lld <- c(LETTERS, letters, 0:9)

pw_matrix <- matrix(sample(Lld, size=1000, replace = TRUE), ncol = 5)

dim(pw_matrix)

## 200 rows of passwords generated, each having 5 columns (characters)

tail(pw_matrix)

pws <- apply(pw_matrix,1,paste,collapse=" ")

# DONE! 

