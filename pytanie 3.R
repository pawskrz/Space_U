
# ----------------------------- Pytanie 3 -----------------------------------

# Sporządź wykres liczby obsłużonych klientów w każdym miesiącu działalności firmy,
# czy firma rośnie, czy podupada?

# ----------------------------------------------------------------------------

query <- paste(
  "SELECT",
  "YEAR(departure) AS year,",
  "MONTH(departure) AS month,",
  "COUNT(*) AS count",
  "FROM flight",
  "INNER JOIN flight_customer USING (flight_id)",
  "GROUP BY YEAR(departure), MONTH(departure)",
  "ORDER BY year, month;"
)


df <- dbGetQuery(con, query)

str(df$count)

df$data <- sprintf("%d-%02d", df$year, df$month)

barplot(as.numeric(df$count), names.arg = df$miesiac, las = 2, col = "#B76DE2",
        main = "Liczba obsłużonych klientów w każdym miesiącu działalności firmy",
        ylab = "Liczba klientów")
