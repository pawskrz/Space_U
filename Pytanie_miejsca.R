library(RMariaDB)

library(dplyr)
library(tidyr)
library(ggplot2)

con <- dbConnect(RMariaDB::MariaDB(),
                 dbname = "space_u",
                 username = "root",
                 password = "Maja",
                 host = "localhost",
                 port = "3307")


q_models <- "
SELECT
m.model_id AS \"model_id\",
AVG(s.ship_price) + m.preserve_cost*36 AS \"average_price\",
m.class_A_seats AS \"Class_A\",
m.class_B_seats AS \"Class_B\",
m.class_C_seats AS \"Class_C\"
FROM
model m
JOIN
ship s
ON s.model_id = m.model_id
GROUP BY model_id
;
"

t_models <- dbGetQuery(con, q_models)

q_ecess_space <-"
SELECT
  offer_id,
  model_id,
  AVG(class_A_seats - bought_A_seats) AS avg_class_A_remaining,
  AVG(class_B_seats - bought_B_seats) AS avg_class_B_remaining,
  AVG(class_C_seats - bought_C_seats) AS avg_class_C_remaining,
  MAX(bought_A_seats) AS max_A_seats,
  MAX(bought_B_seats) AS max_B_seats,
  MAX(bought_C_seats) AS max_C_seats
FROM (
  SELECT 
    fc.flight_id AS flight_id, 
    f.offer_id AS offer_id,
    m.model_id AS model_id,
    m.class_A_seats AS class_A_seats,
    COUNT(CASE WHEN fc.class = 'class_A' THEN 1 END) AS bought_A_seats,
    m.class_B_seats AS class_B_seats,
    COUNT(CASE WHEN fc.class = 'class_B' THEN 1 END) AS bought_B_seats,
    m.class_C_seats AS class_C_seats,
    COUNT(CASE WHEN fc.class = 'class_C' THEN 1 END) AS bought_C_seats
  FROM flight_customer fc 
  JOIN flight f ON fc.flight_id = f.flight_id
  JOIN offer o ON f.offer_id = o.offer_id
  JOIN model m ON o.model_id = m.model_id
  GROUP BY fc.flight_id, f.offer_id, m.model_id, m.class_A_seats, m.class_B_seats, m.class_C_seats
) AS sub
GROUP BY offer_id;
"
t_excess_space <- dbGetQuery(con, q_ecess_space)

t_excess_space_long <- t_excess_space %>%
  arrange(offer_id) %>%
  mutate(group = ceiling(row_number() / 12)) %>%
  pivot_longer(
    cols = starts_with("avg_class_"),
    names_to = "class",
    values_to = "avg_remaining"
  ) %>%
  mutate(
    class = case_when(
      class == "avg_class_A_remaining" ~ "Class A",
      class == "avg_class_B_remaining" ~ "Class B",
      class == "avg_class_C_remaining" ~ "Class C"
    ),
    offer_id = as.factor(offer_id)
  )


for (i in 1:2) {
  plot_data <- t_excess_space_long %>% filter(group == i)
  
  p <- ggplot(plot_data, aes(x = offer_id, y = avg_remaining, fill = class)) +
    geom_col(position = "dodge") +
    labs(
      title = paste("Średnia liczba zmarnowanych miejsc"),
      x = "ID oferty",
      y = "Średnia liczba zmarnowanych miejsc",
      fill = "Klasa"
    ) +
    theme_minimal() +
    theme(
      axis.text.x = element_text(angle = 45, hjust = 1),
      axis.title.x = element_text(margin = margin(t = 10))
    )
  
  print(p)
}




optimal_ship_offer <- c()
for (offer in 1:nrow(t_excess_space)){
  
  max_A <- t_excess_space$max_A_seats[offer]
  max_B <- t_excess_space$max_B_seats[offer]
  max_C <- t_excess_space$max_C_seats[offer]
  model <- t_excess_space$model_id[offer]
  
  optimal_ship <- 1
  for (ship in 1:nrow(t_models)){
    
    ship_A <- t_models$Class_A[ship]
    ship_B <- t_models$Class_B[ship]
    ship_C <- t_models$Class_C[ship]
    ship_price <- t_models$average_price[ship]
    
    if (max_A <= ship_A && max_B <= ship_B && max_C <= ship_C 
        && ship_price < t_models$average_price[optimal_ship] ){
      
        optimal_ship <- ship
    }
  }
  optimal_ship_offer <- c(optimal_ship_offer, optimal_ship)
  
}


optimised_ships <- data.frame(t_excess_space$offer_id, t_excess_space$model_id, optimal_ship_offer )
colnames(optimised_ships) <- c("Offer Id", "Current model for the offer", "Cheapest model that would accomodate all passengers")

optimised_ships








