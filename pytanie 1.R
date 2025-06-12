

# ----------------------------- Pytanie 1 -----------------------------------

# Znajdź najpopularniejsze oferty, porównaj koszta i zyski, 
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
bilety <- c(class_A = df$class_A[1], 
            class_B = df$class_B[1], 
            class_C = df$class_C[1])
extra_cost <- df$extra_cost[1]

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

df$class <- as.character(df$class)

df$price <- bilety[df$class]

zyski <- sum(df$price * as.numeric(df$count), na.rm = TRUE)

#------------------- koszty
koszty <- 0


ile <- unname(najpopularniejsze_liczba_wystapien)[j]

koszty <- extra_cost * ile

query <- paste(
  "SELECT *",
  "FROM model",
  "WHERE model_id LIKE", model
)

df <- dbGetQuery(con, query)
paliwo_start <- df$fuel_per_start[1]

query <- paste(
  "SELECT *",
  "FROM flight f",
  "JOIN year_fuel fp",
  "ON YEAR(f.departure) = YEAR(fp.year)+1",
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




