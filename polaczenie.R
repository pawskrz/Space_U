library(RMariaDB)

#polaczenie z baza danych

con <- dbConnect(RMariaDB::MariaDB(),
                 dbname = "space_u",
                 username = "root",
                 password = "maja",
                 port = 3306,
                 host = "localhost")
