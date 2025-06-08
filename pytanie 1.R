

# ----------------------------- Pytanie 1 -----------------------------------

# Znajdź najpopularniejsze rodzaje wypraw, porównaj koszta i zyski, 
# czy są opłacalne?

# ----------------------------------------------------------------------------

query <- "SELECT * 
          from flight"

df <- dbGetQuery(con, query)

liczba_wystapien <- table(df$offer_id)
# zliczamy ile jest wystąpień każdej wycieczki

najpopularniejsze_liczba_wystapien <- liczba_wystapien[liczba_wystapien > max(liczba_wystapien)-2]
# wybieramy te, które wystąpiły najczęściej

najpopularniejsze_id <- as.numeric(names(najpopularniejsze_liczba_wystapien))
najpopularniejsze_id <- unlist(najpopularniejsze_id) 
# wektor z offer_id najpopularniejszych wypraw

kolumna_zyski <- c()
kolumna_koszty <- c()
kolumna_wyprawa <- c()
najpopularniejsze_id
n <- length(najpopularniejsze_id)

for (j in 1:n){

i <- najpopularniejsze_id[j]
kolumna_wyprawa <- c(kolumna_wyprawa, i)
query <- paste(
"SELECT *",
"from flight_customer",
  "INNER JOIN flight USING (flight_id)",
  "INNER JOIN offer USING (offer_id)",
"WHERE offer_id LIKE", as.character(i)
)

df <- dbGetQuery(con, query)

model <- df$model_id[1]
bilety <- c(df$class_A, df$class_B, df$class_C) #kolejno klasa A, B, C
extra_cost <- df$extra_cost[1]
duration <- df$duration[1]
flight_from <- df$flight_from[1]
flight_to <- df$flight_to[1]

#------------------- zyski 
zyski <- 0


query <- paste(
  "SELECT class, COUNT(*) AS count",
  "FROM flight_customer",
  "INNER JOIN flight USING (flight_id)",
  "INNER JOIN offer USING (offer_id)",
  "WHERE offer_id LIKE", as.character(i),
  "GROUP BY class"
)

df <- dbGetQuery(con, query)

zyski <- bilety[1] * as.numeric(df$count[1]) +
  bilety[2] * as.numeric(df$count[2]) +
  bilety[3] * as.numeric(df$count[3])

#------------------- koszty
koszty <- 0


ile <- unname(najpopularniejsze_liczba_wystapien)[j]

koszty <- extra_cost * ile

query <- paste(
  "SELECT *",
  "FROM planet",
  "INNER JOIN star_system USING (star_system_id)",
  "WHERE planet_id LIKE", as.character(flight_from),
  "OR planet_id LIKE", as.character(flight_to)
)

df <- dbGetQuery(con, query)

odleglosc <- (df$coor_radius[1])^2 +
  (df$coor_radius[2])^2 - 
  2* df$coor_radius[1]*df$coor_radius[2]*cos(df$coor_angle[1]-df$coor_angle[2])
odleglosc <- odleglosc ^(1/2)

query <- paste(
  "SELECT *",
  "FROM model",
  "WHERE model_id LIKE", model
)

df <- dbGetQuery(con, query)
paliwo_start <- df$fuel_per_start[1]

query <- paste(
  "SELECT *",
  "FROM year_fuel"
)

df <- dbGetQuery(con, query)
paliwo <- data.frame(
  year= c(2019, 2020, 2021, 2022, 2023, 2024),
  koszty_paliwa = df$price
)

query <- paste(
  "SELECT EXTRACT(YEAR FROM departure) AS year, COUNT(*) AS count",
  "FROM flight_customer",
  "INNER JOIN flight USING (flight_id)",
  "INNER JOIN offer USING (offer_id)",
  "WHERE offer_id LIKE", as.character(i),
  "GROUP BY EXTRACT(YEAR FROM departure)",
  "ORDER BY year"
)

df <- dbGetQuery(con, query)

tabela<-merge(df,paliwo,by="year")

query <- paste(
  "SELECT *",
  "FROM flight f",
  "JOIN (",
    "SELECT yf.year, yf.price, f2.departure",
    "FROM year_fuel yf",
    "JOIN flight f2 ON yf.year <= f2.departure",
    "WHERE NOT EXISTS (",
        "SELECT 1",
        "FROM year_fuel y2",
        "WHERE y2.year <= f2.departure AND y2.year > yf.year))",
  "y ON y.departure = f.departure",
  "INNER JOIN offer USING (offer_id)",
  "WHERE offer_id LIKE", as.character(i)
)

df <- dbGetQuery(con, query)

koszty <- koszty + 2*sum(df$price)*paliwo_start

kolumna_zyski <- c(kolumna_zyski, zyski)
kolumna_koszty <- c(kolumna_koszty, koszty)
}

podsumowanie <- data.frame(wycieczka = kolumna_wyprawa, zyski=kolumna_zyski,
                           koszty = kolumna_koszty,
                           "zysk dla firmy"=round(kolumna_zyski-kolumna_koszty,2))




