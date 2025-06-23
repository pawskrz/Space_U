import mysql.connector 
from datetime import datetime, timedelta
import random
import decimal
from faker import Faker
import math

fake = Faker()

### Instrukcja połączenia: ###

# Należy zainstalować MariaDB Server z internetu zeby odpalic lokalnie
# polączyć się z mysql
# Connection name* - localmariadb
# Database* - mysql
# Username* #root i port taki jaki przy instalacji mariadb 
# reszta domyslnie

DB_CONFIG = {
    'host': 'localhost',
    'port': 3307,   # default: 3306
    'user': 'elond',       
    'password': 'root',   
    'database': 'space_u'
}

START_DATE = datetime.now() - timedelta(days=6 * 365) 
END_DATE = datetime.now() 

# Hiperparametry
NUM_STAR_SYSTEMS = 4 
NUM_STARS_PER_SYSTEM_RANGE = (1, 2)
NUM_PLANETS_PER_STAR_RANGE = (2, 5)
NUM_ADDRESSES_PER_PLANET = 30
NUM_MODELS = 5
NUM_LICENCES_PER_MODEL_RANGE = (1, 2)
NUM_GENERAL_LICENCES = 3
NUM_EMPLOYEES = 500
NUM_SHIPS_PER_MODEL_RANGE = (1, 9)
NUM_CUSTOMERS = 10000
NUM_OFFERS = 40
NUM_FLIGHTS_PER_OFFER_CONCEPTUAL_TRIP = 5
NUM_YEAR_FUEL_ENTRIES = 6

INTER_SYSTEM_TRAVEL_SCALE_FACTOR = 1.0

NUM_PROFESSIONS = 8 # tego nie zmieniamy, chyba że zmienimy dostępne profesje

def get_random_date(start_date_obj=START_DATE, end_date_obj=END_DATE):
    start_date_val = start_date_obj.date() if isinstance(start_date_obj, datetime) else start_date_obj 
    end_date_val = end_date_obj.date() if isinstance(end_date_obj, datetime) else end_date_obj 

    if start_date_val > end_date_val: 
        return start_date_val 
    
    time_between_dates = end_date_val - start_date_val
    days_between_dates = time_between_dates.days
    if days_between_dates <= 0:
        return start_date_val

    random_number_of_days = random.randrange(days_between_dates + 1) 
    calculated_random_date = start_date_val + timedelta(days=random_number_of_days) 
    
    return calculated_random_date

def polar_to_cartesian(radius, angle_degrees):
    angle_radians = math.radians(angle_degrees)
    x = radius * math.cos(angle_radians)
    y = radius * math.sin(angle_radians)
    return x, y 

def calculate_flight_duration(from_planet_id, to_planet_id, model_id, cursor): 
    try:
        cursor.execute("SELECT star_system_id, orbit_radius FROM planet WHERE planet_id = %s", (from_planet_id,))
        from_planet_data = cursor.fetchone() 
        if not from_planet_data:
            print(f"Warning: Data for from_planet_id {from_planet_id} not found. Using default duration.")
            return timedelta(days=random.randint(1, 10)) 
        from_planet_ss_id, from_planet_orbit_r = from_planet_data 
        from_planet_orbit_r = float(from_planet_orbit_r) if from_planet_orbit_r else 0.0 

        cursor.execute("SELECT star_system_id, orbit_radius FROM planet WHERE planet_id = %s", (to_planet_id,)) 
        to_planet_data = cursor.fetchone()
        if not to_planet_data:
            print(f"Warning: Data for to_planet_id {to_planet_id} not found. Using default duration.")
            return timedelta(days=random.randint(1, 10))
        to_planet_ss_id, to_planet_orbit_r = to_planet_data
        to_planet_orbit_r = float(to_planet_orbit_r) if to_planet_orbit_r else 0.0

        cursor.execute("SELECT speed FROM model WHERE model_id = %s", (model_id,)) 
        model_data = cursor.fetchone()
        if not model_data or not model_data[0] or float(model_data[0]) <= 0:
            print(f"Warning: Speed for model_id {model_id} not found or invalid. Using default duration.")
            return timedelta(days=random.randint(3, 15))
        model_speed = float(model_data[0])

        distance = 0.0

        if from_planet_ss_id == to_planet_ss_id:
            distance = abs(from_planet_orbit_r - to_planet_orbit_r)
            if distance < 0.1 : 
                 distance += 0.1

        else:
            cursor.execute("SELECT coor_radius, coor_angle FROM star_system WHERE star_system_id = %s", (from_planet_ss_id,))
            from_ss_data = cursor.fetchone()
            cursor.execute("SELECT coor_radius, coor_angle FROM star_system WHERE star_system_id = %s", (to_planet_ss_id,))
            to_ss_data = cursor.fetchone()

            if not from_ss_data or not to_ss_data:
                print("Warning: Star system coordinate data missing. Using larger default duration.")
                return timedelta(days=random.randint(10, 30))

            from_ss_r, from_ss_angle = (float(from_ss_data[0]), float(from_ss_data[1])) if from_ss_data[0] and from_ss_data[1] else (0,0)
            to_ss_r, to_ss_angle = (float(to_ss_data[0]), float(to_ss_data[1])) if to_ss_data[0] and to_ss_data[1] else (0,0)

            x1, y1 = polar_to_cartesian(from_ss_r, from_ss_angle)
            x2, y2 = polar_to_cartesian(to_ss_r, to_ss_angle)
            
            distance_between_systems = math.hypot(x2 - x1, y2 - y1) * INTER_SYSTEM_TRAVEL_SCALE_FACTOR
            

            distance = distance_between_systems + from_planet_orbit_r + to_planet_orbit_r


        if model_speed > 0:
            duration_days = distance / model_speed
        else:
            duration_days = random.randint(5, 20)  

        return timedelta(days=duration_days)

    except Exception as e:
        return timedelta(days=random.randint(1, 10)) 

def alien_name(syllables=3):
    vowels = "aeiouyx"
    consonants = "qwrtypsdfghjklzxcvbnm"
    special = "`~-#@-"
    is_special = False
    name = ""
    current_is_vowel = random.choice([True, False])
    for _ in range(syllables * 2):
        if not is_special:
            if random.random() < 0.1:
                name += random.choice(special)
                is_special = True
        if current_is_vowel:
            name += random.choice(consonants)
        else:
            name += random.choice(vowels)
        current_is_vowel = not current_is_vowel
    return name.capitalize() 


def alien_planet_name(): 
    return fake.unique.word().capitalize() + random.choice(["ia", "os", " Prime", " IV", " I", " II", " X", " Secundus"])


def alien_star_name(): 
    prefixes = ["Sol", "Luna", "Stella", "Nova", "Lux", "Ignis", "Astrum", "Coeli", "Sidus"]
    suffixes = [" Major", " Minor", " Prime", " Regis", " Caelus"]

    name = ""
    name += random.choice(prefixes)

    if random.random() < 0.7:
        name += random.choice(suffixes)
    
    if random.random() < 0.3:
        designations = [" I", " II", " III", " IV", " V", " Alpha", " Beta", " Gamma"]
        name += random.choice(designations)
        
    return name

def is_resource_available(resource_id, proposed_start, proposed_end, schedule_dict):
    if resource_id not in schedule_dict:
        return True  
    for busy_start, busy_end in schedule_dict[resource_id]:
        if (busy_start < proposed_end) and (busy_end > proposed_start):
            return False
    return True 

planet_cities_tracker = {} # {planet_id: set_of_city_names}
ship_schedules = {}  # {ship_id: [(start_date, end_date_of_trip), ...]}
employee_schedules = {} # {employee_id: [(start_date, end_date_of_trip), ...]}
customer_schedules = {} # {customer_id: [(start_date, end_date_of_trip), ...]}

### główny generator ###
def populate_data():
    conn = None
    try:
        conn = mysql.connector.connect(**DB_CONFIG) 
        cursor = conn.cursor()
        print("Successfully connected to MariaDB.")

        print("Attempting to clear existing data from tables...")
        try:
            cursor.execute("SET FOREIGN_KEY_CHECKS = 0;")
            cursor.execute(f"SELECT table_name FROM information_schema.tables WHERE table_schema = '{DB_CONFIG['database']}';") 
            tables_to_clear = [table[0] for table in cursor.fetchall()] 
            if tables_to_clear:
                for table_name in tables_to_clear:
                    print(f"Clearing table: `{table_name}`")
                    try:
                        cursor.execute(f"TRUNCATE TABLE `{table_name}`; ")
                    except mysql.connector.Error as trunc_err:
                        print(f"  TRUNCATE TABLE `{table_name}` failed: {trunc_err}. Attempting DELETE FROM...")
                        try:
                            cursor.execute(f"DELETE FROM `{table_name}`;") 
                        except mysql.connector.Error as del_err:
                            print(f"  DELETE FROM `{table_name}` also failed: {del_err}")
            cursor.execute("SET FOREIGN_KEY_CHECKS = 1;") 
            conn.commit()
            print("Data clearing attempt complete.")
        except mysql.connector.Error as clear_err:
            print(f"An error occurred during data clearing: {clear_err}")
        

        # --- generowanie systemow gwiezdnych  ---
        print("Generating Star Systems...")
        star_system_ids = []
        for _ in range(NUM_STAR_SYSTEMS):
            cursor.execute("""
                INSERT INTO star_system (coor_angle, coor_radius) VALUES (%s, %s)
            """, (round(random.uniform(0, 360), 2), round(random.uniform(100, 1000), 2))) 
            star_system_ids.append(cursor.lastrowid) 
        conn.commit()


        # --- gwiazdy ---
        print("Generating Stars...")
        star_ids = []
        for ss_id in star_system_ids:
            for _ in range(random.randint(*NUM_STARS_PER_SYSTEM_RANGE)):
                cursor.execute("""
                    INSERT INTO star (star_system_id, type, name) VALUES (%s, %s, %s)
                """, (ss_id, random.choice(["G-type", "Red Dwarf", "Blue Giant"]), alien_star_name()))
                star_ids.append(cursor.lastrowid)
        conn.commit()

        # --- planety ---
        print("Generating Planets...")
        planet_ids = []
        for ss_id in star_system_ids:
            for _ in range(random.randint(*NUM_PLANETS_PER_STAR_RANGE)):
                cursor.execute("""
                    INSERT INTO planet (star_system_id, type, orbit_radius, name) VALUES (%s, %s, %s, %s)
                """, (ss_id, random.choice(["Terrestrial", "Gas Giant", "Desert", "Oceanic"]),
                      round(random.uniform(0.5, 20), 2), alien_planet_name()))
                planet_id = cursor.lastrowid
                planet_ids.append(planet_id)
                planet_cities_tracker[planet_id] = set() 
        conn.commit()
        if not planet_ids:
            print("No planets generated, cannot continue meaningful data population.")
            return

        # --- adresy ---
        print("Generating Addresses...")
        address_ids = []
        for _ in range(len(planet_ids) * NUM_ADDRESSES_PER_PLANET):
            chosen_planet_id = random.choice(planet_ids)
            city_name = fake.city() 
            while city_name in planet_cities_tracker[chosen_planet_id]:
                city_name = fake.city() 
            planet_cities_tracker[chosen_planet_id].add(city_name)
            
            cursor.execute("""
                INSERT INTO address (planet_id, city, street) VALUES (%s, %s, %s)
            """, (chosen_planet_id, city_name, fake.street_name()))
            address_ids.append(cursor.lastrowid)
        conn.commit()
        if not address_ids:
            print("No addresses generated.")

        # --- zawody ---
        print("Generating Professions...")
        profession_ids = []
        pos_names = ["Captain", "Navigator", "Engineer", "Medic", "Cargo Master", "Envoy", "Scout Lead", "Chief Scientist"]
        for name in pos_names[:NUM_PROFESSIONS]:
            cursor.execute("""
                INSERT INTO profession (profession, pension) VALUES (%s, %s)
            """, (name, random.randint(40000, 120000))) #simoleonów
            profession_ids.append(cursor.lastrowid)
        conn.commit()
        if not profession_ids:
            print("No professions generated.")
            return 


        # --- modele --- 
        print("Generating Models...")
        model_ids = []
        for _ in range(NUM_MODELS):
            cursor.execute("""
                INSERT INTO model (preserve_cost, fuel_per_start, speed, class_A_seats, class_B_seats, class_C_seats)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (decimal.Decimal(random.randrange(10000, 50000))/100,
                  decimal.Decimal(random.randrange(500, 2000))/100, 
                  round(random.uniform(100, 200), 2),
                  random.randint(2, 8), random.randint(10, 30), random.randint(30, 100)))
            model_ids.append(cursor.lastrowid)
        conn.commit()
        if not model_ids:
            print("No models generated.")
            return

        # --- licencje ---
        print("Generating Licences...")
        licence_ids = []
        for model_id_for_lic in model_ids:
            for _ in range(random.randint(*NUM_LICENCES_PER_MODEL_RANGE)):  
                cursor.execute("""
                    INSERT INTO licence (licence, duration, model_id) VALUES (%s, %s, %s)
                """, (f"Type {chr(65+random.randint(0,4))}-{random.randint(1,5)} Cert for Model {model_id_for_lic}",
                      random.randint(5,10) * 365, model_id_for_lic)) 
                licence_ids.append(cursor.lastrowid)
        conn.commit()
        if not licence_ids: print("Warning: No specific licences generated.")

        # --- pracownicy ---
        print("Generating Employees, Licence Mappings, Requirements...")
        employee_ids = []
        for _ in range(NUM_EMPLOYEES):
            if not address_ids or not profession_ids: break
            chosen_profession_id = random.choice(profession_ids)
            cursor.execute("""
                INSERT INTO employee (profession_id, first_name, last_name, address_id, phone, relative_phone)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (chosen_profession_id, fake.first_name(), alien_name(2),
                  random.choice(address_ids), fake.phone_number(), fake.phone_number()))
            emp_id = cursor.lastrowid
            employee_ids.append(emp_id)

            if licence_ids:
                num_emp_lics = random.randint(0, min(3, len(licence_ids))) 
                for lic_id in random.sample(licence_ids, num_emp_lics):
                    cursor.execute("""
                        INSERT INTO licence_employee (employee_id, licence_id, last_renewal)
                        VALUES (%s, %s, %s)
                    """, (emp_id, lic_id, get_random_date(START_DATE, END_DATE - timedelta(days=30)))) 
            
            if random.random() < 0.3 and licence_ids: 
                req_lic_id = random.choice(licence_ids)
                try:
                    cursor.execute("INSERT INTO requirement (profession_id, licence_id) VALUES (%s, %s)",
                                   (chosen_profession_id, req_lic_id))
                except mysql.connector.IntegrityError: pass 
                
        #add zuckerberg
        print("Adding special employee: Mark Zuckerberg...")
        cursor.execute("""
                INSERT INTO employee (profession_id, first_name, last_name, address_id, phone, relative_phone)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (random.choice(profession_ids), "Mark", "Zuckerberg",
                  random.choice(address_ids), fake.phone_number(), fake.phone_number()))
        emp_id = cursor.lastrowid
        
        cursor.execute("""
                        INSERT INTO licence_employee (employee_id, licence_id, last_renewal)
                        VALUES (%s, %s, %s)
                    """, (emp_id, random.choice(licence_ids), get_random_date(START_DATE, END_DATE - timedelta(days=30))))
        conn.commit()
        if not employee_ids: print("Warning: No employees generated.")

        # --- generowanie statkow ---
        print("Generating Ships...")
        ship_ids = []
        ship_creation_details_list = []

        INITIAL_FLEET_PURCHASE_WINDOW_START = START_DATE 
        INITIAL_FLEET_PURCHASE_WINDOW_END = START_DATE + timedelta(days=30) 

        LATER_ACQUISITION_PURCHASE_WINDOW_START = INITIAL_FLEET_PURCHASE_WINDOW_END + timedelta(days=1)
        LATER_ACQUISITION_PURCHASE_WINDOW_END = max(LATER_ACQUISITION_PURCHASE_WINDOW_START, END_DATE - timedelta(days=720)) 
        MAX_INITIAL_SHIPS_PER_MODEL_TYPE = random.randint(1, 2)

        if model_ids and planet_ids:
            for model_id_for_ship in model_ids:
                num_ships_of_this_model_to_generate = random.randint(*NUM_SHIPS_PER_MODEL_RANGE) 
                
                for i in range(num_ships_of_this_model_to_generate):
                    is_initial_fleet_ship = (i < MAX_INITIAL_SHIPS_PER_MODEL_TYPE) 

                    if is_initial_fleet_ship:
                        if INITIAL_FLEET_PURCHASE_WINDOW_START <= INITIAL_FLEET_PURCHASE_WINDOW_END:
                            purchase_date = get_random_date(INITIAL_FLEET_PURCHASE_WINDOW_START, INITIAL_FLEET_PURCHASE_WINDOW_END) 
                        else:
                            purchase_date = START_DATE 
                    else:
                        if LATER_ACQUISITION_PURCHASE_WINDOW_START <= LATER_ACQUISITION_PURCHASE_WINDOW_END:
                            purchase_date = get_random_date(LATER_ACQUISITION_PURCHASE_WINDOW_START, LATER_ACQUISITION_PURCHASE_WINDOW_END)
                        else:
                            purchase_date = get_random_date(INITIAL_FLEET_PURCHASE_WINDOW_START, INITIAL_FLEET_PURCHASE_WINDOW_END)
                    
                    cursor.execute("""
                        INSERT INTO ship (model_id, ship_price, purchase_date) VALUES (%s, %s, %s)
                    """, (model_id_for_ship, decimal.Decimal(random.randrange(2500000, 25000000))/100,
                          purchase_date))
                    ship_id = cursor.lastrowid
                    ship_ids.append(ship_id) 
                    
                    ship_initial_location = random.choice(planet_ids) 
                    ship_creation_details_list.append({
                        'id': ship_id,
                        'purchase_date': purchase_date,
                        'initial_planet_id': ship_initial_location
                    })
            conn.commit() 

        if not ship_ids:
            print("No ships generated. Further flight-related data population might be limited or fail.")
            return 
        
        print(f"Generated {len(ship_ids)} ships in total.")

        ship_current_status = {}
        for ship_details in ship_creation_details_list:
            ship_current_status[ship_details['id']] = {
                'location_planet_id': ship_details['initial_planet_id'],
                'available_date': ship_details['purchase_date'] 
            } 

        # --- customerzy ---
        print("Generating Customers...")
        customer_ids = []
        for _ in range(NUM_CUSTOMERS):
            if not address_ids: break
            cursor.execute("""
                INSERT INTO customer (first_name, last_name, phone, relative_phone, address_id)
                VALUES (%s, %s, %s, %s, %s)
            """, (fake.first_name(), alien_name(3), fake.phone_number(), fake.phone_number(), random.choice(address_ids)))
            customer_ids.append(cursor.lastrowid)
        conn.commit()
        if not customer_ids: print("Warning: No customers generated.")

        # --- oferty ---
        print("Generating Offers...")
        offer_ids = []
        if model_ids and len(planet_ids) >= 2:
            for _ in range(NUM_OFFERS):
                from_planet, to_planet = random.sample(planet_ids, 2)
                cursor.execute("""
                    INSERT INTO offer (model_id, flight_from, flight_to, type, duration, class_A, class_B, class_C, extra_cost)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                """, (random.choice(model_ids), from_planet, to_planet,
                      random.choice(['TOURIST_SIGHTSEEING', 'LUXURY_CRUISE', 'CELEBRATION_FLIGHT']),
                      round(random.uniform(3, 30),1),
                      decimal.Decimal(random.randrange(100000, 200000))/100, 
                      decimal.Decimal(random.randrange(50000, 100000))/100, 
                      decimal.Decimal(random.randrange(10000, 50000))/100,
                      decimal.Decimal(random.randrange(1000, 100000))/100)) 
                offer_ids.append(cursor.lastrowid)
        conn.commit()
        if not offer_ids:
            print("No offers generated, cannot create flights.")
            return

        # --- loty ---
        print("Generating Customer Flights (with integrated Technical Repositioning)...")
        if not (offer_ids and ship_ids and customer_ids and employee_ids and planet_ids):
            print("Missing core data (offers, ships, customers, employees, or planets). Skipping flight generation.")
            return 
        else:
            for offer_id_for_flight in offer_ids:
                cursor.execute("SELECT model_id, duration, flight_from, flight_to FROM offer WHERE offer_id = %s", (offer_id_for_flight,))
                offer_details = cursor.fetchone() 
                if not offer_details: continue
                
                offer_model_id, duration_at_dest_days, customer_departure_planet_id, customer_dest_planet_id = offer_details
                duration_at_dest_td = timedelta(days=float(duration_at_dest_days)) 

                cursor.execute("SELECT class_A_seats, class_B_seats, class_C_seats FROM model WHERE model_id = %s", (offer_model_id,))
                model_seat_data = cursor.fetchone() 
                if not model_seat_data: continue
                class_A_capacity, class_B_capacity, class_C_capacity = model_seat_data
                model_total_capacity = class_A_capacity + class_B_capacity + class_C_capacity 

                cursor.execute("SELECT ship_id FROM ship WHERE model_id = %s", (offer_model_id,))
                all_suitable_ships_for_model = [item[0] for item in cursor.fetchall()] 
                if not all_suitable_ships_for_model: continue
                
                random.shuffle(all_suitable_ships_for_model) 

                scheduled_trips_for_this_offer_count = 0
                for _ in range(NUM_FLIGHTS_PER_OFFER_CONCEPTUAL_TRIP): 
                    tech_flight_scheduled_this_attempt = False
                    if scheduled_trips_for_this_offer_count >= NUM_FLIGHTS_PER_OFFER_CONCEPTUAL_TRIP : break 

                    chosen_ship_id_for_trip = None 
                    
                    customer_flight_leg_duration_td = calculate_flight_duration(
                                customer_departure_planet_id,
                                customer_dest_planet_id,
                                offer_model_id,
                                cursor
                            ) 
                    
                    customer_round_trip_operational_duration = (2 * customer_flight_leg_duration_td) + duration_at_dest_td 

                    for current_ship_candidate_id in all_suitable_ships_for_model:
                        ship_initial_loc_id = ship_current_status[current_ship_candidate_id]['location_planet_id']
                        ship_free_from_date = ship_current_status[current_ship_candidate_id]['available_date'] 
                        
                        tech_flight_departure_actual = None
                        tech_flight_arrival_actual = None
                        tech_pilot_assigned = None
                        
                        earliest_start_for_customer_flight = ship_free_from_date

                       
                        if ship_initial_loc_id != customer_departure_planet_id: 

                            tech_flight_duration_td = calculate_flight_duration(
                                        ship_initial_loc_id,
                                        customer_departure_planet_id,
                                        offer_model_id,
                                        cursor 
                                    )  

                            ship_free_from_date_val = ship_free_from_date.date() if isinstance(ship_free_from_date, datetime) else ship_free_from_date 

                            min_tech_departure_date = ship_free_from_date_val + timedelta(days=random.randint(0, 2)) 
                            
                            end_date_val_for_calc = END_DATE.date() if isinstance(END_DATE, datetime) else END_DATE 
                            max_tech_departure_date = end_date_val_for_calc - tech_flight_duration_td - customer_round_trip_operational_duration - timedelta(days=2) 

                            if min_tech_departure_date > max_tech_departure_date:
                                continue

                            potential_tech_departure = get_random_date(min_tech_departure_date, max_tech_departure_date) 
                            potential_tech_arrival = potential_tech_departure + tech_flight_duration_td 
                            
                            if potential_tech_arrival + customer_round_trip_operational_duration + timedelta(days=1) > end_date_val_for_calc:
                                continue

                            if is_resource_available(current_ship_candidate_id, potential_tech_departure, potential_tech_arrival, ship_schedules):
                                available_pilots_for_tech = [emp_id for emp_id in employee_ids if is_resource_available(emp_id, potential_tech_departure, potential_tech_arrival, employee_schedules)]
                                if available_pilots_for_tech:
                                    tech_pilot_assigned = random.choice(available_pilots_for_tech) 
                                    tech_flight_departure_actual = potential_tech_departure 
                                    tech_flight_arrival_actual = potential_tech_arrival
                                    earliest_start_for_customer_flight = tech_flight_arrival_actual + timedelta(days=random.randint(0,1))
                                    
                                    tech_flight_scheduled_this_attempt = True 
                                else:
                                    continue 
                            else:
                                continue 
                        
                        min_customer_outbound_departure = earliest_start_for_customer_flight
                        max_customer_outbound_departure = END_DATE - customer_round_trip_operational_duration - timedelta(days=1)

                        if min_customer_outbound_departure > max_customer_outbound_departure.date():
                            continue 

                        outbound_departure_date = get_random_date(min_customer_outbound_departure, max_customer_outbound_departure) 
                        arrival_at_dest_date = outbound_departure_date + customer_flight_leg_duration_td 
                        return_departure_date = arrival_at_dest_date + duration_at_dest_td 
                        trip_completion_date = return_departure_date + customer_flight_leg_duration_td 


                        if not is_resource_available(current_ship_candidate_id, outbound_departure_date, trip_completion_date, ship_schedules):
                            continue

                        current_trip_booked_seats = {'class_A': 0, 'class_B': 0, 'class_C': 0}
                        model_class_caps = {'class_A': class_A_capacity, 'class_B': class_B_capacity, 'class_C': class_C_capacity} 
                        assigned_customers_for_this_trip_details = [] 
                        max_customers_to_book_this_flight = random.randint(1, min(model_total_capacity, len(customer_ids))) 

                        if customer_ids : 
                            potential_customer_candidates = [cid for cid in random.sample(customer_ids, min(len(customer_ids), max_customers_to_book_this_flight + 200)) if is_resource_available(cid, outbound_departure_date, trip_completion_date, customer_schedules)]
                            for cust_id in potential_customer_candidates:
                                if len(assigned_customers_for_this_trip_details) >= max_customers_to_book_this_flight: break 
                                available_classes = [k for k,v in current_trip_booked_seats.items() if v < model_class_caps[k]] 
                                if not available_classes: break 
                                chosen_class = random.choice(available_classes) 
                                assigned_customers_for_this_trip_details.append({'id': cust_id, 'class': chosen_class})
                                current_trip_booked_seats[chosen_class] += 1 
                        
                        num_crew_needed = random.randint(2, min(4, len(employee_ids))) 
                        assigned_crew_final_ids = [] 
                        if employee_ids:
                            potential_crew_candidates = [eid for eid in random.sample(employee_ids, min(len(employee_ids), num_crew_needed + 10)) if is_resource_available(eid, outbound_departure_date, trip_completion_date, employee_schedules)]
                            if len(potential_crew_candidates) >= num_crew_needed:
                                assigned_crew_final_ids = random.sample(potential_crew_candidates, num_crew_needed)
                                
                        
                        chosen_ship_id_for_trip = current_ship_candidate_id 
                        if tech_flight_scheduled_this_attempt and tech_pilot_assigned and tech_flight_departure_actual and tech_flight_arrival_actual:
                            cursor.execute("""
                                INSERT INTO technical_flights (ship_id, employee_id, flight_from, flight_to, departure)
                                VALUES (%s, %s, %s, %s, %s)
                            """, (chosen_ship_id_for_trip, tech_pilot_assigned, ship_initial_loc_id, customer_departure_planet_id, tech_flight_departure_actual))
                            
                            if chosen_ship_id_for_trip not in ship_schedules: ship_schedules[chosen_ship_id_for_trip] = []
                            ship_schedules[chosen_ship_id_for_trip].append((tech_flight_departure_actual, tech_flight_arrival_actual))
                            
                            if tech_pilot_assigned not in employee_schedules: employee_schedules[tech_pilot_assigned] = []
                            employee_schedules[tech_pilot_assigned].append((tech_flight_departure_actual, tech_flight_arrival_actual))



                        cursor.execute("INSERT INTO flight (ship_id, offer_id, departure) VALUES (%s, %s, %s)", (chosen_ship_id_for_trip, offer_id_for_flight, outbound_departure_date))
                        flight_id_outbound = cursor.lastrowid
                        cursor.execute("INSERT INTO flight (ship_id, offer_id, departure) VALUES (%s, %s, %s)", (chosen_ship_id_for_trip, offer_id_for_flight, return_departure_date))
                        flight_id_return = cursor.lastrowid

                        if chosen_ship_id_for_trip not in ship_schedules: ship_schedules[chosen_ship_id_for_trip] = []
                        ship_schedules[chosen_ship_id_for_trip].append((outbound_departure_date, trip_completion_date))
                        
                        ship_current_status[chosen_ship_id_for_trip]['location_planet_id'] = customer_departure_planet_id 
                        ship_current_status[chosen_ship_id_for_trip]['available_date'] = trip_completion_date

                        for booking_info in assigned_customers_for_this_trip_details:
                            cust_id, flight_class = booking_info['id'], booking_info['class']
                            cursor.execute("INSERT INTO flight_customer (flight_id, customer_id, class) VALUES (%s, %s, %s)", (flight_id_outbound, cust_id, flight_class))
                            cursor.execute("INSERT INTO flight_customer (flight_id, customer_id, class) VALUES (%s, %s, %s)", (flight_id_return, cust_id, flight_class))
                            if cust_id not in customer_schedules: customer_schedules[cust_id] = []
                            customer_schedules[cust_id].append((outbound_departure_date, trip_completion_date))
                        
                        for emp_id in assigned_crew_final_ids:
                            cursor.execute("INSERT INTO flight_employee (flight_id, employee_id) VALUES (%s, %s)", (flight_id_outbound, emp_id))
                            cursor.execute("INSERT INTO flight_employee (flight_id, employee_id) VALUES (%s, %s)", (flight_id_return, emp_id))
                            if emp_id not in employee_schedules: employee_schedules[emp_id] = []
                            employee_schedules[emp_id].append((outbound_departure_date, trip_completion_date))

                        scheduled_trips_for_this_offer_count += 1
                        break
            conn.commit()

        # --- roczne ceny paliwa ---
        print("Generating Year Fuel Prices...")
        start_year = START_DATE.year
        end_year = END_DATE.year
        for i in range(start_year, end_year + 1):
            year_date = datetime(i, 1, 1).date() 
            cursor.execute("""
                INSERT INTO year_fuel (year, price) VALUES (%s, %s)
            """, (year_date, decimal.Decimal(random.randrange(100, 500))/100))
        conn.commit()

        print("Data population completed successfully!")

    except mysql.connector.Error as err:
        print(f"Error: {err}")
        if conn and conn.is_connected(): 
            conn.rollback()
            print("Transaction rolled back.")
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()
            print("MariaDB connection is closed.")
if __name__ == '__main__':
    populate_data() 