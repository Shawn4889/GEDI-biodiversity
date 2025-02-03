#Xiaoxuan Li 
library(tools) 
library(ggplot2)
library(ggpointdensity)
library(viridis)
library(ggcorrplot)
library(ggpmisc)
library(dplyr)
library(tidyverse) 
library(readxl)
library(grid)
library(mltools)
library(Metrics)
library(devtools)
library(ggsignif)
library(corrplot)
library(psych)
library(xlsx)
library(car)
library(MASS)
library(ggrepel)
library(data.table)
library(lmtest)
library(ggpubr)
library(tidyr)
library(stats)
library(caret)
library(randomForest)

#table merge
dir <- "F:\\GEDI\\Result_Luther\\Result_11132024\\GEDI\\GEDI_sel.csv"
Data = read.csv(dir,header=T)
df_mean <- Data %>%
  group_by(Site) %>%
  summarise(across(everything(), mean, na.rm = TRUE))

# Display the result
print(df_mean)
write.csv(df_mean, file = "F:\\GEDI\\Result_Luther\\Result_11132024\\GEDI\\GEDI_sel_mean.csv")



# ------------------------------------------------------------------------------------------------ #
#rfe
dir = "E:\\GEDI\\Result_Luther\\Result\\Biodiversity0206.xlsx"
Data = read_excel(dir, sheet = "Biodiversity")
Data <- subset(Data, select = -c(Site,AA))
list <- 0
for(i in 1:100){
  control <- rfeControl(functions = rfFuncs, 
                        method = "cv", 
                        number = 5)
  results <- rfe(data.frame(Data[,17:36]), 
                 as.matrix(Data[,"AP"]), 
                 rfeControl = control)
  list[[i]] <- results$optVariables[1]
}
table(list)



##randomforest method 
dir = "E:\\GEDI\\Result_Luther\\Result\\Biodiversity0206.xlsx"
Data = read_excel(dir, sheet = "Biodiversity")
Data <- subset(Data, select = -c(Site,AA))
list_top <- list()
for (i in 1:100){
  rf <- randomForest(SR ~ ., 
                     data = Data[,c(2,18:37)],ntree = 501,importance=TRUE, mtry = 4)
  #varImpPlot(rf)
  #importance(rf)
  a<- varImp(rf)
  a <- cbind(var = rownames(a), a)
  a <- a[order(-a$Overall),]
  a <- head(a$var, 5)
  list_top <- append(list_top,a)
}

summary_top <- table(unlist(list_top))
summary_top



##caret method 
dir = "E:\\GEDI\\Result_Luther\\Result\\Biodiversity0206.xlsx"
Data = read_excel(dir, sheet = "Biodiversity")
Data <- subset(Data, select = -c(Site,SR))
list_top <- list()
list_r2 <- list()
list_rmse <- list()
for (i in 1:100){
  repeat_cv <- trainControl(method='cv', number=5)
  rf <- train(
    AA ~ .,
    data=Data[,c(2,18:37)], 
    method='rf', 
    ntree=501,
    tuneGrid = expand.grid(.mtry=c(4)) ,
    trControl=repeat_cv)
  a<- varImp(rf)
  a<- a$importance
  a <- cbind(var = rownames(a), a)
  a <- a[order(-a$Overall),]
  a <- head(a$var, 5)
  list_top <- append(list_top,a)
  list_r2 <- append(list_r2,rf$results[,3])
  list_rmse <- append(list_rmse,rf$results[,2])
}

table(unlist(list_top))
mean(unlist(list_r2))
sd(unlist(list_r2))
mean(unlist(list_rmse))
sd(unlist(list_rmse))

# ------------------------------------------------------------------------------------------------ #
#L2B vs. L2A RH98 
dir = "E:\\GEDI\\Result_Luther\\Result\\Biodiversity0206.xlsx"
Data = read_excel(dir, sheet = "Biodiversity")
Data <- Data[Data$Type != "NA",]

p1<- ggplot(Data, aes(x = RH_98 , y = PAVD, color = Type, group = Type)) +
  theme_bw()+
  geom_point(size = 3)+
  geom_line(size = 1)+
  coord_flip()+
  labs(y="GEDI PAVD", 
       x="GEDI RH98 (m)",
       color='Habitat Types')+
  theme(legend.position="none")+
  theme(text=element_text(size=30))+
  theme(plot.title = element_text(hjust = 0.5))

p2<- ggplot(Data, aes(x = RH_98 , y = PAI, color = Local, group = Local)) +
  theme_bw()+
  geom_point(size = 3)+
  geom_line(size = 1)+
  coord_flip()+
  labs(y="GEDI PAI (m2/m-2)", 
       x="GEDI RH98 (m)",
       color='Habitat Types')+
  theme(legend.position="none")+
  theme(text=element_text(size=30))+
  theme(plot.title = element_text(hjust = 0.5))

p3<- ggplot(Data, aes(x = RH_98 , y = Cover, color = Local, group = Local)) +
  theme_bw()+
  geom_point(size = 3)+
  geom_line(size = 1)+
  coord_flip()+
  labs(y="GEDI Cover (%)", 
       x="GEDI RH98 (m)",
       color='Habitat Types')+
  theme(legend.position="none")+
  theme(text=element_text(size=30))+
  theme(plot.title = element_text(hjust = 0.5))


p4<- ggplot(Data, aes(x = RH_98 , y = FHD, color = Local, group = Local)) +
  theme_bw()+
  geom_point(size = 3)+
  geom_line(size = 1)+
  coord_flip()+
  labs(y="GEDI FHD", 
       x="GEDI RH98 (m)",
       color='Habitat Types')+
  theme(legend.position="none")+
  theme(text=element_text(size=30))+
  theme(plot.title = element_text(hjust = 0.5))


p5<- ggplot(Data, aes(x = RH_98 , y = AGBD, color = Local, group = Local)) +
  theme_bw()+
  geom_point(size = 3)+
  geom_line(size = 1)+
  coord_flip()+
  labs(y="GEDI AGBD (Mg/ha)", 
       x="GEDI RH98 (m)",
       color='Habitat Types')+
  theme(legend.position=c(1.5,0.5))+
  theme(text=element_text(size=30))+
  theme(plot.title = element_text(hjust = 0.5))


ggarrange(p1,p2,p3,p4,p5, nrow=2, ncol= 3)





#merge L2 and L4A to one excel 
# ------------------------------------------------------------------------------------------------ #
# 25m CHM 2018 vs 2012
dir <- "E:\\GEDI\\Result_Luther\\Basic_GEDI\\GEDI_Amazon_01272024.csv"
Data_index = read.csv(dir)

dir <- "E:\\GEDI\\Result_Luther\\Basic_GEDI\\GEDI_Amazon_biomass_01272024.csv"
Data = read.csv(dir)
Data = subset(Data, select=-c(2,3))

Data_index <- merge(Data_index, Data, by.x = "shot_number", by.y = "shot_number")

write.table(Data_index,file='E:\\GEDI\\Result_Luther\\Basic_GEDI\\Merge.csv',
            sep = ",",col.names=TRUE,row.names=F)



# ------------------------------------------------------------------------------------------------ #
dir <- "E:\\GEDI\\Result_Luther\\Result\\Biodiversity.csv"
Data_index = read.csv(dir)

cor(Data_index[,-1])
col <- colorRampPalette(c("#BB4444", "#EE9988", "#FFFFFF", "#77AADD", "#4477AA"))
