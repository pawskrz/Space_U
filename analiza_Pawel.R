#install.packages("RMariaDB")
library("RMariaDB")

#making conenction 
con <- dbConnect(RMariaDB :: MariaDB(),
                 host = "localhost",
                 port = 3306,
                 username = "root",
                 password = "plokijuh",
                 dbname  = "space_u")

#kapitanowie odpowiedniego roku
captains <- dbGetQuery(con,
                     "SELECT P.`year`, flights_count, P.employee_id, first_name, last_name FROM
                     
                      (SELECT COUNT(flight_employee.flight_id) AS flights_count, YEAR(departure) AS `year`, flight_employee.employee_id, first_name, last_name
                      FROM employee INNER JOIN flight_employee
                      ON employee.employee_id=flight_employee.employee_id
                      INNER JOIN profession
                      ON employee.profession_id = profession.profession_id
                      INNER JOIN flight
                      ON flight_employee.flight_id = flight.flight_id
                      WHERE profession LIKE '%captain%'
                      GROUP BY flight_employee.employee_id, `year`) AS P
                      
                      INNER JOIN
                      
                      (SELECT MAX(flights_count) AS max_count, `year` FROM
                      (SELECT COUNT(flight_employee.flight_id) AS flights_count, YEAR(departure) AS `year`, flight_employee.employee_id, first_name, last_name
                      FROM employee INNER JOIN flight_employee
                      ON employee.employee_id=flight_employee.employee_id
                      INNER JOIN profession
                      ON employee.profession_id = profession.profession_id
                      INNER JOIN flight
                      ON flight_employee.flight_id = flight.flight_id
                      WHERE profession LIKE '%captain%'
                      GROUP BY flight_employee.employee_id, `year`) AS K
                      GROUP BY `year`) AS M ON P.`year` = M.`year` AND P.flights_count = M.max_count
                      ORDER BY P.`year`;
                      ")

#najabrdziej dochodowa wycieczka
#brakuje ceny paliwa na 2025, więc gubię loty. Po uzupełnieniu ceny na 2025 będzie zgodność
trips <- dbGetQuery(con, "SELECT T.flight_id, fuel_per_start, price, class_A, class_A_seats,class_B, class_B_seats, class_C_seats, class_C, extra_cost FROM
                    (SELECT flight_id, fuel_per_start, price, class_A, class_B, class_C, extra_cost
                    FROM flight INNER JOIN offer ON offer.offer_id = flight.offer_id
                    INNER JOIN model ON model.model_id = offer.model_id
                    INNER JOIN year_fuel ON YEAR(year_fuel.year) = YEAR(flight.departure)) AS T
                    INNER JOIN 
                    (SELECT flight_id, SUM(IF(class=1, 1, 0)) class_A_seats, SUM(IF(class=2, 1, 0)) class_B_seats, SUM(IF(class=3, 1, 0)) class_C_seats
                    FROM flight_customer
                    GROUP BY flight_id
                    ORDER BY flight_id, class) AS C ON T.flight_id = C.flight_id"  
                    )
trips$cost <- trips$fuel_per_start * trips$price + trips$extra_cost
trips$income <- trips$class_A * trips$class_A_seats + trips$class_B * trips$class_B_seats + trips$class_C * trips$class_C_seats
trips$profit <- trips$income - trips$cost
profit <- data.frame(trips$flight_id, trips$profit)
colnames(profit) <- c("flight_id", "profit")
zi_best_flighto <- profit[which.max(profit$profit), 1:2]
