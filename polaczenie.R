library(RMariaDB)

#polaczenie z baza danych

con <- dbConnect(RMariaDB::MariaDB(),
                 dbname = "space_u",
                 username = "root",
                 password = "maja",
                 port = 3306,
                 host = "localhost")

#tworzenie ramek danych

query <- "SELECT * FROM address"
address <- dbGetQuery(con, query)

query <- "SELECT * FROM customer"
customer <- dbGetQuery(con, query)

query <- "SELECT * FROM employee"
employee <- dbGetQuery(con, query)

query <- "SELECT * FROM flight"
flight <- dbGetQuery(con, query)

query <- "SELECT * FROM flight_customer"
flight_customer <- dbGetQuery(con, query)

query <- "SELECT * FROM flight_employee"
flight_employee <- dbGetQuery(con, query)

query <- "SELECT * FROM licence"
licence <- dbGetQuery(con, query)

query <- "SELECT * FROM licence_employee"
licence_employee <- dbGetQuery(con, query)

query <- "SELECT * FROM model"
model <- dbGetQuery(con, query)

query <- "SELECT * FROM offer"
offer <- dbGetQuery(con, query)

query <- "SELECT * FROM planet"
planet <- dbGetQuery(con, query)

query <- "SELECT * FROM profession"
profession <- dbGetQuery(con, query)

query <- "SELECT * FROM requirement"
requirement <- dbGetQuery(con, query)

query <- "SELECT * FROM ship"
ship <- dbGetQuery(con, query)

query <- "SELECT * FROM star"
star <- dbGetQuery(con, query)

query <- "SELECT * FROM star_system"
star_system <- dbGetQuery(con, query)

query <- "SELECT * FROM technical_flights"
technical_flights <- dbGetQuery(con, query)

query <- "SELECT * FROM year_fuel"
year_fuel <- dbGetQuery(con, query)
