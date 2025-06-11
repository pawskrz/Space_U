# ----------------------------- Pytanie 2 -----------------------------------

# Znajdź najpopularniejszy rodzaj wycieczki, porównaj koszta i zyski, 
# czy są opłacalne?

# ----------------------------------------------------------------------------

query <- "SELECT type, COUNT(*) AS count
          from flight
          INNER JOIN offer USING (offer_id)
          GROUP BY type
          ORDER BY count DESC"

rodzaje <- dbGetQuery(con, query)

kolumna_zyski <- c()
kolumna_koszty <- c()
kolumna_rodzaj <- c()

for (k in 1:3){
rodzaj <- rodzaje$type[k]

kolumna_rodzaj <- c(kolumna_rodzaj, rodzaj)

query <- paste(
  "SELECT *",
  "FROM flight",
  "INNER JOIN offer USING (offer_id)",
  "WHERE type LIKE", paste0("'", as.character(rodzaj), "'")
)

df <- dbGetQuery(con, query)

liczba_wystapien <- table(df$offer_id)
liczba_wystapien

oferty_id <- as.numeric(names(liczba_wystapien))
oferty_id <- unlist(oferty_id)

zyski <- 0
koszty <- 0

n <- length(oferty_id)

for (j in 1:n){
  
  i <- oferty_id[j]
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
  
  ile <- unname(liczba_wystapien)[j]
  
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
  
}

kolumna_zyski <- c(kolumna_zyski, zyski)
kolumna_koszty <- c(kolumna_koszty, koszty)

}

podsumowanie <- data.frame(rodzaj=kolumna_rodzaj,
                           przychody=kolumna_zyski,
                           koszty = kolumna_koszty,
                           "dochody/straty"=round(kolumna_zyski-kolumna_koszty,2))
