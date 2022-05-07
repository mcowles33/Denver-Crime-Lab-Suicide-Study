##Pemutation Tests for Independence Using a Chi-Square Test Statistic

#load libraries
library(epitools)

#Set a seed to replicate results
set.seed(25)

#Input data found in python script  
A <- matrix(nrow=2, byrow=T, c(1508, 373, 201, 5, 9, 53, 310, 739,540, 108, 37, 2, 4, 12, 192, 289),
            dimnames=list(c("M","F"),c("CD","CS",",C","DA","H","I","NA","O"))) 

B <- matrix(nrow=3, byrow=T, c(1673, 326, 179, 5, 5, 40, 269, 791,314, 148, 59, 2, 8, 24, 203, 195,61, 7, 0, 0, 0, 1, 30, 42), 
             dimnames=list(c("L","D","M"), c("CD","CS",",C","DA","H","I","NA","O")))

C <- matrix(nrow=3, byrow=T, c(1666, 310, 175, 6, 8, 56, 437, 847,177, 87, 35, 0, 3, 0, 26, 86,101, 52, 19, 1, 1, 5, 21, 46), 
            dimnames=list(c("C","H","A"), c("CD","CS",",C","DA","H","I","NA","O")))

D <- matrix(nrow=3, byrow=T, c(257, 78, 34, 2, 5, 22, 178, 166,27, 43, 16, 0, 2, 0, 9, 17,18, 19, 6, 0, 1, 1, 10, 8), 
            dimnames=list(c("CD","HD","AD"), c("CD","CS",",C","DA","H","I","NA","O")))

E <- matrix(nrow=3, byrow=T, c(1362, 230, 141, 4, 3, 33, 235, 647,145, 43, 19, 0, 1, 0, 14, 64,74, 29, 13, 1, 0, 4, 8, 35), 
            dimnames=list(c("CL","HL","AL"), c("CD","CS",",C","DA","H","I","NA","O")))

F <- matrix(nrow=2, byrow=T, c(74, 29, 13, 1, 0, 4, 8, 35,154, 32, 8, 0, 2, 5, 111, 98), 
            dimnames=list(c("MD","FD"), c("CD","CS",",C","DA","H","I","NA","O")))

G <- matrix(nrow=2, byrow=T, c(1287, 250, 150, 3, 3, 33, 188, 600,386, 76, 29, 2, 2, 7, 81, 191), 
            dimnames=list(c("ML","FL"), c("CD","CS",",C","DA","H","I","NA","O")))

#Find expected cell counts
datas <- c("A","B","C","D","E","F","G")
for (data in datas)
{
  i <- get(data)
  exp <- outer(rowSums(i),colSums(i))/sum(i)
  print(exp)
}

#Keep cell counts from data with expected values larger than 5
AA <- matrix(nrow=2, byrow=T, c(1508, 373, 201, 53, 310, 739,540, 108, 37, 12, 192, 289),
            dimnames=list(c("M","F"),c("CD","CS","C","I","NA","O"))) 

BB <- matrix(nrow=3, byrow=T, c(1673, 326, 179, 269, 791,314, 148, 59, 203, 195,61, 7, 0, 30, 42), 
            dimnames=list(c("L","D","M"), c("CD","CS","C","NA","O")))

CC <- matrix(nrow=3, byrow=T, c(1666, 310, 175, 437, 847,177, 87, 35, 26, 86,101, 52, 19, 21, 46), 
            dimnames=list(c("C","H","A"), c("CD","CS","C","NA","O")))

DD <- matrix(nrow=3, byrow=T, c(257, 78, 178, 166,27, 43, 9, 17,18, 19, 10, 8), 
            dimnames=list(c("CD","HD","AD"), c("CD","CS","NA","O")))

EE <- matrix(nrow=3, byrow=T, c(1362, 230, 141, 235, 647,145, 43, 19, 14, 64,74, 29, 13, 8, 35), 
            dimnames=list(c("CL","HL","AL"), c("CD","CS","C","NA","O")))

FF <- matrix(nrow=2, byrow=T, c(74, 29, 13, 8, 35,154, 32, 8, 111, 98), 
            dimnames=list(c("MD","FD"), c("CD","CS",",C","NA","O")))

GG <- matrix(nrow=2, byrow=T, c(1287, 250, 150, 33, 188, 600,386, 76, 29, 7, 81, 191), 
            dimnames=list(c("ML","FL"), c("CD","CS",",C","I","NA","O")))

# Define a function to do the chisquare test
chisq<-function(Obs)
{ #Obs is the observed contingency table
  Expected <- outer(rowSums(Obs),colSums(Obs))/sum(Obs)
  sum((Obs-Expected)^2/Expected)
}

ctables <- c("AA","BB","CC","DD","EE","FF","GG")
for (table in ctables)
{
  #Compute observed statistic
  i <- get(table)
  observed <- chisq(i)
  print(paste0("Observed Statistic = ", observed))
 
  #Permutation test
  #Expand the contingency table to individual level data on which we can run permutations
  dat <- expand.table(i)

  dem <- dat[,1]         #set first column as the demographic data
  drug <- dat[,2]        #set second column as the drug group data
  B <- 10^5-1            #set number of times to repeat this process
  result <- numeric(B)   #space to save the random differences

  #Permutations 
  for(i in 1:B)
  {
    dem.permuted <- sample(dem)
    perm.table <- table(dem.permuted, drug)
    result[i] <- chisq(perm.table)
  }
  
  #Plot
  hist(result, xlab = expression(C), main="Permutation distribution for chi-square statistic")
  abline(v = observed, col = "blue", lty=5)
  
  #Compute P-value from the permutation distribution
  print(paste0("P-Value from permutation = ",(sum(result >= observed)+1)/(B + 1))) 
  
}
