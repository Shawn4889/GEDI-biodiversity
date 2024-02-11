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

#variable selection
dir = "E:\\GEDI\\Result_Luther\\Result\\Biodiversity0206.xlsx"
Data = read_excel(dir, sheet = "Biodiversity")
Data <- subset(Data, select = -c(Site,SR))
rf <- randomForest(AA ~ ., 
                   data = Data[,c(1,17:36)],ntree = 100,importance=TRUE, nodesize = 20)
importance(rf)
varImpPlot(rf)
varImp(rf)


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
