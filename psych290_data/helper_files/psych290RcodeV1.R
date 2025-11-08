# these are the dependencies you need to have installed. 
# if necessary, install with install.packages("ggthemes") etc

require(ggthemes)
library(grid)
library(ggthemes)
library(reshape2)


################# DLATK FEATURE TABLE formatting magic


## This takes in a DLATK FEATURE TABLE and output in wide-format, with 0s where there should be zero.
## you get the feature table with df <- dbGetQuery(db_connection, "Select....")
importFeat <- function(df){
  #install.packages("reshape2")
  library(reshape2)
  df.molten <- melt(df, id.vars=c("group_id", "feat"), measure.vars="group_norm")
  df.recast <- dcast(df.molten, group_id ~ ...)
  df.recast.clean <- df.recast
  #clean NAs to zeros
  df.recast.clean[is.na(df.recast.clean)] <- 0
  #strip "_group_norm" from var names
  names(df.recast.clean) <- sub("_group_norm","",names(df.recast.clean))
  df.recast.clean_length = length(df.recast.clean)
  names(df.recast.clean)[2:df.recast.clean_length] <- sub("[$]","_",names(df.recast.clean)[2:df.recast.clean_length])
  return(df.recast.clean)
}


## this will take in a topic FEATURE TABLE and output it in wide-format, with 0s where there should be 0s
## the only difference is that it appends a "T" to the column names, as numbers aren't suitable column headings in R
importFeatTopics <- function(df){
  #reshape table\
  #install.packages("reshape2")
  library(reshape2)
  df.molten <- melt(df, id.vars=c("group_id", "feat"), measure.vars="group_norm")
  df.recast <- dcast(df.molten, group_id ~ ...)
  df.recast.clean <- df.recast
  #clean NAs to zeros
  df.recast.clean[is.na(df.recast.clean)] <- 0
  #strip "_group_norm" from var names
  names(df.recast.clean) <- sub("_group_norm","",names(df.recast.clean))
  df.recast.clean_length = length(df.recast.clean)
  names(df.recast.clean) <- sub("_group_norm","",names(df.recast.clean))
  names(df.recast.clean)[2:df.recast.clean_length] <- paste0("T",names(df.recast.clean)[2:df.recast.clean_length])
  return(df.recast.clean)
}


################### GGPLOT FORMATTING MAGIC

## add this to any ggplot to make it look amazing out of the box! e.g., qplot(someVar) + themePublication() -- BAMM!!
theme_Publication <- function(base_size=14, base_family="helvetica") {
  library(grid)
  library(ggthemes)
  (theme_foundation(base_size=base_size, base_family=base_family)
    + theme(plot.title = element_text(face = "bold",
                                      size = rel(1.2), hjust = 0.5),
            text = element_text(),
            panel.background = element_rect(colour = NA),
            plot.background = element_rect(colour = NA),
            panel.border = element_rect(colour = NA),
            axis.title = element_text(face = "bold",size = rel(1)),
            axis.title.y = element_text(angle=90,vjust =2),
            axis.title.x = element_text(vjust = -0.2),
            axis.text = element_text(), 
            axis.line = element_line(colour="black"),
            axis.ticks = element_line(),
            panel.grid.major = element_line(colour="#f0f0f0"),
            panel.grid.minor = element_blank(),
            legend.key = element_rect(colour = NA),
            legend.position = "bottom",
            legend.direction = "horizontal",
            legend.key.size= unit(0.2, "cm"),
            legend.margin = unit(0, "cm"),
            legend.title = element_text(face="italic"),
            plot.margin=unit(c(10,5,5,5),"mm"),
            strip.background=element_rect(colour="#f0f0f0",fill="#f0f0f0"),
            strip.text = element_text(face="bold")
    ))
  
}

## same as above, but leaves the legend untouched. sometimes you don't want to format the legend from the default. 
#only applies to plots that have legends. 
theme_Publication_leaveLegend <- function(base_size=14, base_family="helvetica") {
  library(grid)
  library(ggthemes)
  (theme_foundation(base_size=base_size, base_family=base_family)
    + theme(plot.title = element_text(face = "bold",
                                      size = rel(1.2), hjust = 0.5),
            text = element_text(),
            panel.background = element_rect(colour = NA),
            plot.background = element_rect(colour = NA),
            panel.border = element_rect(colour = NA),
            axis.title = element_text(face = "bold",size = rel(1)),
            axis.title.y = element_text(angle=90,vjust =2),
            axis.title.x = element_text(vjust = -0.2),
            axis.text = element_text(), 
            axis.line = element_line(colour="black"),
            axis.ticks = element_line(),
            panel.grid.major = element_line(colour="#f0f0f0"),
            panel.grid.minor = element_blank(),
            # legend.key = element_rect(colour = NA),
            # legend.position = "bottom",
            # legend.direction = "horizontal",
            # legend.key.size= unit(0.2, "cm"),
            # legend.margin = unit(0, "cm"),
            # legend.title = element_text(face="italic"),
            plot.margin=unit(c(10,5,5,5),"mm"),
            strip.background=element_rect(colour="#f0f0f0",fill="#f0f0f0"),
            strip.text = element_text(face="bold")
    ))
  
}

############################## Nice johannes functions to quickly quick the tires on a dataframe, with increasing detail (median, avg...)
## if checkDf3 fails (the most detail), use checkDf2, and so forth. 


## checks a DF for vars that are incomplete (how many NAs?), and not numeric
checkDf <- function(outcome.df){
  #output.df = data.frame(aname=NA, bname=NA)[numeric(0), ]
  mydata = outcome.df
  #names = rep(NA, length(colnames(outcome.df)))
  names = colnames(mydata)
  output.df = data.frame(names)
  na_count = sapply(mydata, function(y) sum(length(which(is.na(y)))))
  output.df$na = data.frame(na_count)
  is_numericy <- sapply(mydata, function(y) sum(length(which(is.numeric(y)))))
  output.df$numeric <- data.frame(is_numericy)
  require(dplyr)
  # output.df %>% mutate_if(is.factor, as.character) -> output.df
  return(output.df)
}

checkDf2 <- function(outcome.df){
  #output.df = data.frame(aname=NA, bname=NA)[numeric(0), ]
  mydata = outcome.df
  #names = rep(NA, length(colnames(outcome.df)))
  names = colnames(mydata)
  output.df = data.frame(names)
  NAs = sapply(mydata, function(y) sum(length(which(is.na(y)))))
  output.df$NAs <- NAs
  numeric <- sapply(mydata, function(y) sum(length(which(is.numeric(y)))))
  output.df$numeric <- numeric
  miny <- sapply(mydata, function(y) min(y, na.rm = T))
  maxy <-  sapply(mydata, function(y) max(y, na.rm = T))
  output.df$min[output.df$numeric==1] <- miny[output.df$numeric==1]
  output.df$min[output.df$numeric==0] <- ""
  output.df$max[output.df$numeric==1] <- maxy[output.df$numeric==1]
  output.df$max[output.df$numeric==0] <- ""
  isZero <- sapply(mydata, function(y) sum(y==0, na.rm = TRUE))
  output.df$zeroes[output.df$numeric==1] <- isZero[output.df$numeric==1]
  output.df$zeroes[output.df$numeric==0] <- ""
  nonNA <- sapply(mydata, function(y) sum(!is.na(y)))
  output.df$nonNA[output.df$numeric==1] <- nonNA[output.df$numeric == 1]
  output.df$nonNA[output.df$numeric==0] <- ""
  unique <- sapply(mydata, function(y) length(unique((y))))
  output.df$unique[output.df$numeric==1] <- unique[output.df$numeric == 1]
  output.df$unique[output.df$numeric==0] <- ""
  require(dplyr)
  # output.df %>% mutate_if(is.factor, as.character) -> output.df
  return(output.df)
}


#also includes means and Sds and medians
# ultraCheckCor(U)
checkDf3 <- function(input.df){
  # consider converting all incoming columsn that are all NA to character
  #output.df = data.frame(aname=NA, bname=NA)[numeric(0), ]
  mydata <- input.df
  #names = rep(NA, length(colnames(outcome.df)))
  colNum <- 1:dim(mydata)[2]
  output.df = data.frame(colNum) ## XX this is a good construct
  row.names(output.df) <- colnames(mydata)
  # NAs
  NAs = sapply(mydata, function(y) sum(length(which(is.na(y))))) # this seems silly
  output.df$NAs <- NAs
  # Numeric 
  numeric <- sapply(mydata, function(y) sum(length(which(is.numeric(y)))))
  output.df$numeric <- numeric
  #min max
  miny <- sapply(mydata, function(y) min(y, na.rm = T))
  maxy <-  sapply(mydata, function(y) max(y, na.rm = T))
  output.df$min[output.df$numeric==1] <- round(as.numeric(miny[output.df$numeric==1]),2)
  output.df$min[output.df$numeric==0] <- NA
  output.df$max[output.df$numeric==1] <- round(as.numeric(maxy[output.df$numeric==1]),2)
  output.df$max[output.df$numeric==0] <- NA
  # more
  isZero <- sapply(mydata, function(y) sum(y==0, na.rm = TRUE))
  output.df$zeroes[output.df$numeric==1] <- isZero[output.df$numeric==1]
  output.df$zeroes[output.df$numeric==0] <- NA
  nonNA <- sapply(mydata, function(y) sum(!is.na(y)))
  output.df$nonNA[output.df$numeric==1] <- nonNA[output.df$numeric == 1]
  output.df$nonNA[output.df$numeric==0] <- NA
  unique <- sapply(mydata, function(y) length(unique((y))))
  output.df$unique[output.df$numeric==1] <- unique[output.df$numeric == 1]
  output.df$unique[output.df$numeric==0] <- NA
  f_mean <- sapply(mydata, function(y) round(mean(y, na.rm = T), digits = 2))
  output.df$mean[output.df$numeric==1] <- f_mean[output.df$numeric == 1]
  output.df$mean[output.df$numeric==0] <- NA
  f_sd <- sapply(mydata, function(y) round(sd(y, na.rm = T),digits = 2))
  output.df$SD[output.df$numeric==1] <- f_sd[output.df$numeric == 1]
  output.df$SD[output.df$numeric==0] <- NA
  f_median <- sapply(mydata, function(y) round(median(y, na.rm = T),3))
  output.df$median[output.df$numeric==1] <- f_median[output.df$numeric == 1]
  output.df$median[output.df$numeric==0] <- NA
  
  # require(dplyr)
  #output.df %>% mutate_if(is.factor, as.character) -> output.df
  return(output.df)
}