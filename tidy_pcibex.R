#!/usr/bin/env Rscript

# R-base version
# Set working directory to source file l

this_dir <- function(directory)
  setwd( file.path(getwd(), directory) )

# setwd("/Users/pamelafuhrmeister/Documents/Work/Postdoc/SFB/Reliability_paper/audio_recordings_preprocessing/2023_01_17_6/")

# User-defined function to read in PCIbex Farm results files
read.pcibex <- function(filepath, auto.colnames=TRUE, fun.col=function(col,cols){cols[cols==col]<-paste(col,"Ibex",sep=".");return(cols)}) {
  n.cols <- max(count.fields(filepath,sep=",",quote=NULL),na.rm=TRUE)
  if (auto.colnames){
    cols <- c()
    con <- file(filepath, "r")
    while ( TRUE ) {
      line <- readLines(con, n = 1, warn=FALSE)
      if ( length(line) == 0) {
        break
      }
      m <- regmatches(line,regexec("^# (\\d+)\\. (.+)\\.$",line))[[1]]
      if (length(m) == 3) {
        index <- as.numeric(m[2])
        value <- m[3]
        if (is.function(fun.col)){
          cols <- fun.col(value,cols)
        }
        cols[index] <- value
        if (index == n.cols){
          break
        }
      }
    }
    close(con)
    return(read.csv(filepath, comment.char="#", header=FALSE, col.names=cols))
  }
  else{
    return(read.csv(filepath, comment.char="#", header=FALSE, col.names=seq(1:n.cols)))
  }
}


# Read in results file
results <- read.pcibex("results.csv")

#Save to csv
write.csv(results,"my_results.csv", row.names = FALSE)

library(tidyverse)

tidied_results <- results %>%
  filter(PennElementType == "TextInput" | PennElementType == "DropDown") %>%
  filter(Parameter != "First") %>%
  # filter(PennElementName != "feedback") %>%
  select(Results.reception.time, MD5.hash.of.participant.s.IP.address, PennElementName, Value) %>%
  pivot_wider(names_from = PennElementName, values_from = Value)

write.csv(tidied_results, "tidy.csv")


