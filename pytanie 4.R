
# ----------------------------- Pytanie 4 -----------------------------------

# Sprawdź, po których wycieczkach klienci wracają na kolejne, a po których mają
# dość i więcej ich nie widzicie. Czy są takie, które być może powinny zniknąć 
# z oferty?

# ----------------------------------------------------------------------------

query <- paste(
  "SELECT DISTINCT customer_id",
  "FROM flight_customer",
  "INNER JOIN flight USING (flight_id)"
)

wracaja <- rep(0,40)
nie_wracaja <- rep(0,40)

df <- dbGetQuery(con, query)

klienci <- as.numeric(df$customer_id)
n<- length(klienci)

for (i in 1:n){
  id <- klienci[i]
  
  query <- paste(
    "SELECT *",
    "FROM flight_customer",
    "INNER JOIN flight USING (flight_id)",
    "WHERE customer_id LIKE", as.character(id)
  )
 
  df <- dbGetQuery(con, query)
  
  if (length(df$flight_id)==1){
    nie_wracaja[df$offer_id[1]] <- nie_wracaja[df$offer_id[1]] + 1
  }
  if (length(df$flight_id)>1){
    for ( j in 1:(length(df$offer_id)-1) ){
      wracaja[df$offer_id[j]] <- wracaja[df$offer_id[j]] + 1
    }
    nie_wracaja[df$offer_id[length(df$offer_id)]] <- 
      nie_wracaja[df$offer_id[length(df$offer_id)]]+1
  }
}

query <- "SELECT * 
          from flight"

df <- dbGetQuery(con, query)

liczba_wystapien <- table(df$offer_id)

id <- as.numeric(names(liczba_wystapien))
id <- unlist(id) 

wspolczynnik_powrotu <- c()
for (i in id){
  wspolczynnik <- wracaja[i]/(wracaja[i]+nie_wracaja[i])
  wspolczynnik_powrotu <- c(wspolczynnik_powrotu, wspolczynnik)
}

wspolczynnik_niepowrotu <- 1 - wspolczynnik_powrotu

dane <- data.frame(
  offer_id = rep(id, each = 2),
  status = rep(c("wracają", "nie wracają"), times = length(id)),
  procent = as.vector(rbind(wspolczynnik_powrotu, wspolczynnik_niepowrotu))
)

library(ggplot2)

ggplot(dane, aes(x = factor(offer_id), y = procent, fill = status)) +
  geom_bar(stat = "identity", position = "dodge") +
  labs(title = "Procent klientów wracających i niewracających po wycieczce",
       x = "Numer wycieczki (offer_id)",
       y = "Procent") +
  scale_fill_manual(values = c("wracają" = "forestgreen", "nie wracają" = "firebrick")) +
  theme_minimal()
