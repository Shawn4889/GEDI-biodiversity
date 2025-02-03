# ------------------------------------------------------------------------------------------------ #
# How to Access the LP DAAC Data Pool with R
# The following R code example demonstrates how to configure a connection to download data from an
# Earthdata Login enabled server, specifically the LP DAAC Data Pool.
# ------------------------------------------------------------------------------------------------ #
# Author: Cole Krehbiel
# Last Updated: 11/14/2019
# Collaborator: Xiaoxuan
# ------------------------------------------------------------------------------------------------ #
# Check for required packages, install if not previously installed

# Load necessary packages into R
library(getPass)
library(httr)
# ---------------------------------SET UP ENVIRONMENT--------------------------------------------- #
# IMPORTANT: Update the line below if you want to download to a different directory (ex: "c:/data/")
dl_dir <- "E:\\Kenya\\GEDI"                                 # Set dir to download files to
out_dir <- file.path(dl_dir)

site_files<- list.files(out_dir)
for (i in 1:1){
  download_list <- file.path(out_dir,site_files[i])
  print(download_list)
  
  setwd(dl_dir)                                                # Set the working dir to the dl_dir
  usr <- file.path(dl_dir)                  # Retrieve home dir (for netrc file)
  if (usr == "") {usr = dl_dir}                    # If no user profile exists, use home
  netrc <- file.path(usr,'.netrc', fsep = .Platform$file.sep)  # Path to netrc file
  
  # ------------------------------------CREATE .NETRC FILE------------------------------------------ #
  # If you already have a .netrc file with your Earthdata Login credentials stored in your home
  # directory, this portion will be skipped. Otherwise you will be prompted for your NASA Earthdata
  # Login Username/Password and a netrc file will be created to store your credentials (in home dir)
  if (file.exists(netrc) == FALSE || grepl("urs.earthdata.nasa.gov", readLines(netrc)) == FALSE) {
    netrc_conn <- file(netrc)
    
    # User will be prompted for NASA Earthdata Login Username and Password below
    writeLines(c("machine urs.earthdata.nasa.gov",
                 sprintf("login %s", getPass(msg = "xxl164030")),
                 sprintf("password %s", getPass(msg = "Lxx47944889"))), netrc_conn)
    close(netrc_conn)
  }
  
  # ---------------------------CONNECT TO DATA POOL AND DOWNLOAD FILES------------------------------ #
  # Below, define either a single link to a file for download, a list of links, or a text file
  # containing links to the desired files to download. For a text file, there should be 1 file link
  # listed per line. Here we show examples of each of the three ways to download files.
  # **IMPORTANT: be sure to update the links for the specific files you are interested in downloading.
  
  # 1. Single file (this is just an example link, replace with your desired file to download):
  files <- readLines(download_list, warn = FALSE)
  files <- files[!grepl(".sha256", files)]
  # Loop through all files
  
  for (i in 1:length(files)) {
    try({ 
      filename <-  tail(strsplit(files[i], '/')[[1]], n = 1) # Keep original filename
      out<-file.path(out_dir,filename)
      if (!(file.exists(out))){
        
        # Write file to disk (authenticating with netrc) using the current directory/filename
        response <- GET(files[i],write_disk(out, overwrite = TRUE), progress(),
                        config(netrc = TRUE, netrc_file = netrc), set_cookies("LC" = "cookies"))
        
        # Check to see if file downloaded correctly
        if (response$status_code == 200) {
          print(sprintf("%s downloaded at %s", filename, dl_dir))
        } else {
          print(sprintf("%s not downloaded. Verify that your username and password are correct in %s", filename, netrc))
        }
      }
      else {
        print(paste0("File exist...",out))
      }
    })
  }
}




