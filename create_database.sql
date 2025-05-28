DROP DATABASE IF EXISTS space_u;
CREATE DATABASE space_u;
USE space_u;

CREATE TABLE address
(
  address_id INT NOT NULL AUTO_INCREMENT, -- to automatycznie przydziela id pokolei od 1, 2, itd
  planet_id  INT NOT NULL,
  city       VARCHAR(255),
  street     VARCHAR(255),
  PRIMARY KEY (address_id)
) COMMENT 'information about address of cust and emp';

CREATE TABLE customer
(
  customer_id    INT NOT NULL AUTO_INCREMENT,
  first_name     VARCHAR(255),
  last_name      VARCHAR(255),
  phone          VARCHAR(50),
  relative_phone VARCHAR(50),
  address_id     INT NOT NULL,
  PRIMARY KEY (customer_id)
);

CREATE TABLE employee
(
  employee_id    INT NOT NULL AUTO_INCREMENT COMMENT 'id of employee',
  profession_id    INT NOT NULL,
  first_name     VARCHAR(255),
  last_name      VARCHAR(255),
  address_id     INT NOT NULL,
  phone          VARCHAR(50),
  relative_phone VARCHAR(50),
  PRIMARY KEY (employee_id)
) COMMENT 'basic data of employees';

CREATE TABLE flight
(
  flight_id INT  NOT NULL AUTO_INCREMENT,
  ship_id   INT  NOT NULL,
  offer_id  INT  NOT NULL,
  departure DATE NULL     COMMENT 'date of leaving planet',
  PRIMARY KEY (flight_id)
) COMMENT 'information about past, present and future trips';

CREATE TABLE flight_customer
(
  flight_id   INT                                  NOT NULL,
  customer_id INT                                  NOT NULL,
  class       ENUM('class_A', 'class_B','class_C'),
  PRIMARY KEY (flight_id, customer_id)
);

CREATE TABLE flight_employee
(
  flight_id   INT NOT NULL,
  employee_id INT NOT NULL COMMENT 'id of employee',
  PRIMARY KEY (flight_id, employee_id)
) COMMENT 'crewmembers of specific flight';

CREATE TABLE licence
(
  licence_id INT NOT NULL AUTO_INCREMENT,
  licence    VARCHAR(255),
  duration   INT,
  model_id   INT NOT NULL,
  PRIMARY KEY (licence_id)
);

CREATE TABLE licence_employee
(
  employee_id  INT  NOT NULL COMMENT 'id of employee',
  licence_id   INT  NOT NULL,
  last_renewal DATE,
  PRIMARY KEY (employee_id, licence_id)
);

CREATE TABLE model
(
  model_id       INT NOT NULL AUTO_INCREMENT,
  preserve_cost  DECIMAL(12,2),
  fuel_per_start DECIMAL(10,2),
  speed          FLOAT,
  class_A_seats  INT COMMENT 'number of seats',
  class_B_seats  INT,
  class_C_seats  INT,
  PRIMARY KEY (model_id)
) COMMENT 'of ship';

CREATE TABLE offer
(
  offer_id    INT     NOT NULL AUTO_INCREMENT,
  model_id    INT     NOT NULL,
  flight_from INT     NOT NULL,
  flight_to   INT     NOT NULL                                                   COMMENT 'destination',
  type        ENUM('TOURIST_SIGHTSEEING', 'LUXURY_CRUISE', 'CELEBRATION_FLIGHT') COMMENT 'type of trip',
  duration    FLOAT                                                              COMMENT 'in destination',
  class_A     DECIMAL(15,2)                                                      COMMENT 'price',
  class_B     DECIMAL(15,2)                                                      COMMENT 'price',
  class_C     DECIMAL(15,2)                                                      COMMENT 'price',
  extra_cost  DECIMAL(15,2) NOT NULL                                             COMMENT 'for us',
  PRIMARY KEY (offer_id)
) COMMENT 'info on offers';

CREATE TABLE planet
(
  planet_id      INT NOT NULL AUTO_INCREMENT,
  star_system_id INT NOT NULL,
  type           VARCHAR(255),
  orbit_radius   FLOAT,
  name           VARCHAR(255),
  PRIMARY KEY (planet_id)
);

CREATE TABLE profession
(
  profession_id INT NOT NULL AUTO_INCREMENT,
  profession    VARCHAR(255),
  pension     INT,
  PRIMARY KEY (profession_id)
);

CREATE TABLE requirement
(
  profession_id INT NOT NULL,
  licence_id  INT NOT NULL,
  PRIMARY KEY (profession_id, licence_id)
);

CREATE TABLE ship
(
  ship_id       INT     NOT NULL AUTO_INCREMENT,
  model_id      INT     NOT NULL,
  ship_price    DECIMAL(15,2),
  purchase_date DATE,
  PRIMARY KEY (ship_id)
) COMMENT 'information about ships';

CREATE TABLE star
(
  star_id        INT     NOT NULL AUTO_INCREMENT,
  star_system_id INT     NOT NULL,
  type           VARCHAR(255),
  name           VARCHAR(255),
  PRIMARY KEY (star_id)
);

CREATE TABLE star_system
(
  star_system_id INT     NOT NULL AUTO_INCREMENT,
  coor_angle     FLOAT,
  coor_radius    FLOAT,
  PRIMARY KEY (star_system_id)
);

CREATE TABLE technical_flights
(
  tech_flight_id INT  NOT NULL AUTO_INCREMENT,
  ship_id        INT  NOT NULL,
  employee_id    INT  NOT NULL COMMENT 'id of employee',
  flight_from    INT  NOT NULL COMMENT 'planet_id',
  flight_to      INT  NOT NULL COMMENT 'planet_id',
  departure      DATE,
  PRIMARY KEY (tech_flight_id)
);

CREATE TABLE year_fuel
(
  year  DATE ,
  price DECIMAL(15,2)    
) COMMENT 'cost of fuel per year';

ALTER TABLE requirement
  ADD CONSTRAINT FK_profession_TO_requirement
    FOREIGN KEY (profession_id)
    REFERENCES profession (profession_id);

ALTER TABLE requirement
  ADD CONSTRAINT FK_licence_TO_requirement
    FOREIGN KEY (licence_id)
    REFERENCES licence (licence_id);

ALTER TABLE employee
  ADD CONSTRAINT FK_profession_TO_employee
    FOREIGN KEY (profession_id)
    REFERENCES profession (profession_id);

ALTER TABLE licence_employee
  ADD CONSTRAINT FK_employee_TO_licence_employee
    FOREIGN KEY (employee_id)
    REFERENCES employee (employee_id);

ALTER TABLE licence_employee
  ADD CONSTRAINT FK_licence_TO_licence_employee
    FOREIGN KEY (licence_id)
    REFERENCES licence (licence_id);

ALTER TABLE licence
  ADD CONSTRAINT FK_model_TO_licence
    FOREIGN KEY (model_id)
    REFERENCES model (model_id);

ALTER TABLE ship
  ADD CONSTRAINT FK_model_TO_ship
    FOREIGN KEY (model_id)
    REFERENCES model (model_id);

ALTER TABLE star
  ADD CONSTRAINT FK_star_system_TO_star
    FOREIGN KEY (star_system_id)
    REFERENCES star_system (star_system_id);

ALTER TABLE planet
  ADD CONSTRAINT FK_star_system_TO_planet
    FOREIGN KEY (star_system_id)
    REFERENCES star_system (star_system_id);

ALTER TABLE offer
  ADD CONSTRAINT FK_planet_TO_offer
    FOREIGN KEY (flight_from)
    REFERENCES planet (planet_id);

ALTER TABLE offer
  ADD CONSTRAINT FK_planet_TO_offer1
    FOREIGN KEY (flight_to)
    REFERENCES planet (planet_id);

ALTER TABLE offer
  ADD CONSTRAINT FK_model_TO_offer
    FOREIGN KEY (model_id)
    REFERENCES model (model_id);

ALTER TABLE flight
  ADD CONSTRAINT FK_offer_TO_flight
    FOREIGN KEY (offer_id)
    REFERENCES offer (offer_id);

ALTER TABLE flight_customer
  ADD CONSTRAINT FK_flight_TO_flight_customer
    FOREIGN KEY (flight_id)
    REFERENCES flight (flight_id);

ALTER TABLE flight_customer
  ADD CONSTRAINT FK_customer_TO_flight_customer
    FOREIGN KEY (customer_id)
    REFERENCES customer (customer_id);

ALTER TABLE customer
  ADD CONSTRAINT FK_address_TO_customer
    FOREIGN KEY (address_id)
    REFERENCES address (address_id);

ALTER TABLE flight_employee
  ADD CONSTRAINT FK_employee_TO_flight_employee
    FOREIGN KEY (employee_id)
    REFERENCES employee (employee_id);

ALTER TABLE flight_employee
  ADD CONSTRAINT FK_flight_TO_flight_employee
    FOREIGN KEY (flight_id)
    REFERENCES flight (flight_id);

ALTER TABLE address
  ADD CONSTRAINT FK_planet_TO_address
    FOREIGN KEY (planet_id)
    REFERENCES planet (planet_id);

ALTER TABLE employee
  ADD CONSTRAINT FK_address_TO_employee
    FOREIGN KEY (address_id)
    REFERENCES address (address_id);

ALTER TABLE flight
  ADD CONSTRAINT FK_ship_TO_flight
    FOREIGN KEY (ship_id)
    REFERENCES ship (ship_id);

ALTER TABLE technical_flights
  ADD CONSTRAINT FK_ship_TO_technical_flights
    FOREIGN KEY (ship_id)
    REFERENCES ship (ship_id);

ALTER TABLE technical_flights
  ADD CONSTRAINT FK_planet_TO_technical_flights
    FOREIGN KEY (flight_from)
    REFERENCES planet (planet_id);

ALTER TABLE technical_flights
  ADD CONSTRAINT FK_planet_TO_technical_flights1
    FOREIGN KEY (flight_to)
    REFERENCES planet (planet_id);

ALTER TABLE technical_flights
  ADD CONSTRAINT FK_employee_TO_technical_flights
    FOREIGN KEY (employee_id)
    REFERENCES employee (employee_id);
