import mysql.connector 
from datetime import datetime, timedelta
import random
import decimal
from faker import Faker
import math

fake = Faker()

## trzeba zaisntalować mariadb server z internetu zeby odpalic lokalnie
## polączyć się z mysql
#Connection name* - localmariadb
# Database* - mysql
#Username* #root i port taki jaki przy instalacji mariadb 
#reszta domyslnie

#pip install mysql-connector-python faker (to sa dwie potrzebne biblioteki)


# cursor robi cos takiego ze mozna zapisywac zapytania sqlowe ale robić %s jako zmienne pythonowe
# --- Configuration ---
DB_CONFIG = {
    'host': 'localhost',
    'port': 3307,   # default: 3306
    'user': 'root',       # Replace with your MariaDB username
    'password': 'Maja',   # Replace with your MariaDB password
    'database': 'space_u'
}

START_DATE = datetime.now() - timedelta(days=6 * 365) #liczone w dniach ludzkich (6 lat)
END_DATE = datetime.now() #teraz

#hiperparametry
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

INTER_SYSTEM_TRAVEL_SCALE_FACTOR = 1.0 #jezeli koordynaty systemow slonecznych i orbit planet sa w innych jednostkach to tu mozna zmienaic skale

NUM_PROFESSIONS = 8 # tego nie zmieniamy (chyba że wprowadzimy nowe profesje)

def get_random_date(start_date_obj=START_DATE, end_date_obj=END_DATE):
    start_date_val = start_date_obj.date() if isinstance(start_date_obj, datetime) else start_date_obj #typy danych
    end_date_val = end_date_obj.date() if isinstance(end_date_obj, datetime) else end_date_obj #ustala typy danych

    if start_date_val > end_date_val: 
        return start_date_val 
    
    time_between_dates = end_date_val - start_date_val
    days_between_dates = time_between_dates.days
    if days_between_dates <= 0:
        return start_date_val

    random_number_of_days = random.randrange(days_between_dates + 1) 
    calculated_random_date = start_date_val + timedelta(days=random_number_of_days) #timedelta wspiera operacje na danych date
    
    return calculated_random_date

def polar_to_cartesian(radius, angle_degrees):
    angle_radians = math.radians(angle_degrees)
    x = radius * math.cos(angle_radians)
    y = radius * math.sin(angle_radians)
    return x, y #to do ukladow gwiezdnych

def calculate_flight_duration(from_planet_id, to_planet_id, model_id, cursor): #oblicza czas lotu na podstawie odleglosci i predkosci
    try:
        cursor.execute("SELECT star_system_id, orbit_radius FROM planet WHERE planet_id = %s", (from_planet_id,)) #bierzemy dane z planety z ktorej wylatujemy
        from_planet_data = cursor.fetchone() #wyciąga wynik z tego cursora co wyzej jest zrobiony
        if not from_planet_data:
            print(f"Warning: Data for from_planet_id {from_planet_id} not found. Using default duration.")
            return timedelta(days=random.randint(1, 10)) #antyerrorowe
        from_planet_ss_id, from_planet_orbit_r = from_planet_data #dane planety (orbita, id systemu gwiezdnego)
        from_planet_orbit_r = float(from_planet_orbit_r) if from_planet_orbit_r else 0.0 #to zamienia na float 

        cursor.execute("SELECT star_system_id, orbit_radius FROM planet WHERE planet_id = %s", (to_planet_id,)) #to nizej to to samo ale dla drugiej planety (destination)
        to_planet_data = cursor.fetchone()
        if not to_planet_data:
            print(f"Warning: Data for to_planet_id {to_planet_id} not found. Using default duration.")
            return timedelta(days=random.randint(1, 10))
        to_planet_ss_id, to_planet_orbit_r = to_planet_data
        to_planet_orbit_r = float(to_planet_orbit_r) if to_planet_orbit_r else 0.0

        cursor.execute("SELECT speed FROM model WHERE model_id = %s", (model_id,)) #tu wybieramy speed z modelu
        model_data = cursor.fetchone()
        if not model_data or not model_data[0] or float(model_data[0]) <= 0:
            print(f"Warning: Speed for model_id {model_id} not found or invalid. Using default duration.")
            return timedelta(days=random.randint(3, 15))
        model_speed = float(model_data[0])

        distance = 0.0

        if from_planet_ss_id == to_planet_ss_id:
            # podroz wewnatrz ukladu
            distance = abs(from_planet_orbit_r - to_planet_orbit_r)
            if distance < 0.1 : # jakby byla mega mala odleglosc to dodajemy mini zeby sie nie zerowalo
                 distance += 0.1

        else:
            # miedzy systemami
            cursor.execute("SELECT coor_radius, coor_angle FROM star_system WHERE star_system_id = %s", (from_planet_ss_id,))
            from_ss_data = cursor.fetchone()
            cursor.execute("SELECT coor_radius, coor_angle FROM star_system WHERE star_system_id = %s", (to_planet_ss_id,))
            to_ss_data = cursor.fetchone()

            if not from_ss_data or not to_ss_data:
                print("Warning: Star system coordinate data missing. Using larger default duration.")
                return timedelta(days=random.randint(10, 30)) #obsluga bledu

            from_ss_r, from_ss_angle = (float(from_ss_data[0]), float(from_ss_data[1])) if from_ss_data[0] and from_ss_data[1] else (0,0)
            to_ss_r, to_ss_angle = (float(to_ss_data[0]), float(to_ss_data[1])) if to_ss_data[0] and to_ss_data[1] else (0,0)

            x1, y1 = polar_to_cartesian(from_ss_r, from_ss_angle)
            x2, y2 = polar_to_cartesian(to_ss_r, to_ss_angle)
            
            distance_between_systems = math.hypot(x2 - x1, y2 - y1) * INTER_SYSTEM_TRAVEL_SCALE_FACTOR
            
            # odleglosc miedzy planetami (miedzy systemami + orbity obu planet)
            #zakladamy ze podrozujemy tylko jak orbity sa ładnie ułożone bo inaczej byloby ciezko xd
            distance = distance_between_systems + from_planet_orbit_r + to_planet_orbit_r


        if model_speed > 0:
            duration_days = distance / model_speed #odleglosc/predkosc
        else:
            duration_days = random.randint(5, 20)  

        return timedelta(days=duration_days)

    except Exception as e:
        return timedelta(days=random.randint(1, 10)) #te wszystkie co returnuja randomowe rzeczy to ogolnie sa antyerrory

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
    return name.capitalize() #nazwisko kosmity xd


def alien_planet_name(): #planety
    return fake.unique.word().capitalize() + random.choice(["ia", "os", " Prime", " IV", " I", " II", " X", " Secundus"])


def alien_star_name(): #gwiazdy
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
#faker to ogolnie taka biblioteka do tych nazw i stroinski mi ją polecał

def is_resource_available(resource_id, proposed_start, proposed_end, schedule_dict):
    if resource_id not in schedule_dict:
        return True  
    for busy_start, busy_end in schedule_dict[resource_id]:
        if (busy_start < proposed_end) and (busy_end > proposed_start):
            return False
    return True #to jest do sprawdzania czy statek/customer/empployee itd są wgl dostępni w danym momencie

planet_cities_tracker = {} # {planet_id: set_of_city_names}
ship_schedules = {}  # {ship_id: [(start_date, end_date_of_trip), ...]}
employee_schedules = {} # {employee_id: [(start_date, end_date_of_trip), ...]}
customer_schedules = {} # {customer_id: [(start_date, end_date_of_trip), ...]}

### główny generator ###
def populate_data():
    conn = None
    try:
        conn = mysql.connector.connect(**DB_CONFIG) #ustalamy połączenie z bazą danych
        cursor = conn.cursor()
        print("Successfully connected to MariaDB.")

        # --- czyszczenie jak cos juz jest zeby mozna bylo odpalac od nowa ---
        print("Attempting to clear existing data from tables...")
        try:
            cursor.execute("SET FOREIGN_KEY_CHECKS = 0;") #wyłączamy sprawdzanie kluczy
            cursor.execute(f"SELECT table_name FROM information_schema.tables WHERE table_schema = '{DB_CONFIG['database']}';") #pobieramy wszystkie tabele
            tables_to_clear = [table[0] for table in cursor.fetchall()] 
            if tables_to_clear:
                for table_name in tables_to_clear:
                    print(f"Clearing table: `{table_name}`")
                    try:
                        cursor.execute(f"TRUNCATE TABLE `{table_name}`; ") #usuwamy dane z tabeli (truncate usuwa dane)
                    except mysql.connector.Error as trunc_err:
                        print(f"  TRUNCATE TABLE `{table_name}` failed: {trunc_err}. Attempting DELETE FROM...")
                        try:
                            cursor.execute(f"DELETE FROM `{table_name}`;") #gdyby truncate nie zadzialal z jakiegos opwodu to po porstu delete
                        except mysql.connector.Error as del_err:
                            print(f"  DELETE FROM `{table_name}` also failed: {del_err}")
            cursor.execute("SET FOREIGN_KEY_CHECKS = 1;") #przywracamy sprawdzanie kluczy
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
            """, (round(random.uniform(0, 360), 2), round(random.uniform(100, 1000), 2))) #wsadzamy randomowe koordynaty, promien od 100 do 1000
            star_system_ids.append(cursor.lastrowid) #to zapisuje id ale w pythonie zeby nie musiec tego ciagle wyciagac z sqla 
        conn.commit()

## ogolnie jednostki odleglosci ktore wybralem dla planet i gwiazd to jednostka astronomiczna (au), to jest równe odleglosci Ziemi od Słońca

        # --- gwiazdy ---
        print("Generating Stars...")
        star_ids = []
        for ss_id in star_system_ids:
            for _ in range(random.randint(*NUM_STARS_PER_SYSTEM_RANGE)):
                cursor.execute("""
                    INSERT INTO star (star_system_id, type, name) VALUES (%s, %s, %s)
                """, (ss_id, random.choice(["G-type", "Red Dwarf", "Blue Giant"]), alien_star_name()))
                star_ids.append(cursor.lastrowid)
        conn.commit() #to samo co wyzej

        # --- planety to samo co wyzej ---
        print("Generating Planets...")
        planet_ids = []
        for ss_id in star_system_ids:
            for _ in range(random.randint(*NUM_PLANETS_PER_STAR_RANGE)):
                cursor.execute("""
                    INSERT INTO planet (star_system_id, type, orbit_radius, name) VALUES (%s, %s, %s, %s)
                """, (ss_id, random.choice(["Terrestrial", "Gas Giant", "Desert", "Oceanic"]),
                      round(random.uniform(0.5, 20), 2), alien_planet_name())) # orbit_radius in AU
                planet_id = cursor.lastrowid
                planet_ids.append(planet_id)
                planet_cities_tracker[planet_id] = set() # Initialize for unique city names
        conn.commit()
        if not planet_ids:
            print("No planets generated, cannot continue meaningful data population.")
            return

        # --- adresy to samo co wyzej ---
        print("Generating Addresses...")
        address_ids = []
        for _ in range(len(planet_ids) * NUM_ADDRESSES_PER_PLANET):
            chosen_planet_id = random.choice(planet_ids)
            city_name = fake.city() #city names z fakera wiec beda faktyczne nazwy
            while city_name in planet_cities_tracker[chosen_planet_id]:
                city_name = fake.city() # to jest ten tracker zeby sie nie powtarzaly nazwy
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
            return #no tez wszystko w sumie to samo co wyzej, 8 zawodow wymyslonych


        # --- modele --- ogolnie wszystko jest tak samo chyba ze bede piasc ze jest inaczej xd
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
            for _ in range(random.randint(*NUM_LICENCES_PER_MODEL_RANGE)): #randomowa liczba licencji dla kazdego modelu w podanym zakresie 
                cursor.execute("""
                    INSERT INTO licence (licence, duration, model_id) VALUES (%s, %s, %s)
                """, (f"Type {chr(65+random.randint(0,4))}-{random.randint(1,5)} Cert for Model {model_id_for_lic}",
                      random.randint(5,10) * 365, model_id_for_lic)) #tu sa jakies takie pierdolki zeby fajnie wygladalo
                licence_ids.append(cursor.lastrowid)
        conn.commit()
        if not licence_ids: print("Warning: No specific licences generated.")


        # --- employees & licence employees & requirements ---
        print("Generating Employees, Licence Mappings, Requirements...")
        employee_ids = []
        for _ in range(NUM_EMPLOYEES):
            if not address_ids or not profession_ids: break
            chosen_profession_id = random.choice(profession_ids) #losowy zawod dla kazdego pracownika
            cursor.execute("""
                INSERT INTO employee (profession_id, first_name, last_name, address_id, phone, relative_phone)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (chosen_profession_id, fake.first_name(), alien_name(2),
                  random.choice(address_ids), fake.phone_number(), fake.phone_number()))
            emp_id = cursor.lastrowid
            employee_ids.append(emp_id)

            if licence_ids:
                num_emp_lics = random.randint(0, min(3, len(licence_ids))) #moze miec od 0 do 3 licencji kazdy pracownik
                for lic_id in random.sample(licence_ids, num_emp_lics):
                    cursor.execute("""
                        INSERT INTO licence_employee (employee_id, licence_id, last_renewal)
                        VALUES (%s, %s, %s)
                    """, (emp_id, lic_id, get_random_date(START_DATE, END_DATE - timedelta(days=30)))) #czas dostania licencji jest od poczatku dzialania firmy do max 30 dni przed dzisijejsym dniem
            
            if random.random() < 0.3 and licence_ids: # 30% szans ze zawód wymaga danej licencji
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

        INITIAL_FLEET_PURCHASE_WINDOW_START = START_DATE #część statków to początkowa flota - te które kupiliśmy przy zakładaniu firmy zeby miec cos od zera
        INITIAL_FLEET_PURCHASE_WINDOW_END = START_DATE + timedelta(days=30) #dajemy sobie 30 dni dzialania firmy na kupienie początkowej floty

        LATER_ACQUISITION_PURCHASE_WINDOW_START = INITIAL_FLEET_PURCHASE_WINDOW_END + timedelta(days=1)
        LATER_ACQUISITION_PURCHASE_WINDOW_END = max(LATER_ACQUISITION_PURCHASE_WINDOW_START, END_DATE - timedelta(days=720)) #a to sa te co kupilismy potem
        #zakladamy ze ostatni statek byl kupiony 2 lata temu zeby tez mogl sobie polatac 
        # 1 albo 2 statki na model kupione w 1 miesiacu dzialania firmy
        MAX_INITIAL_SHIPS_PER_MODEL_TYPE = random.randint(1, 2)

        if model_ids and planet_ids:
            for model_id_for_ship in model_ids:
                num_ships_of_this_model_to_generate = random.randint(*NUM_SHIPS_PER_MODEL_RANGE) #dla kazdeog modelu wybieramy sobie ile mamy wygeneroawc statkow (zakres to hiperpametr)
                
                for i in range(num_ships_of_this_model_to_generate):
                    is_initial_fleet_ship = (i < MAX_INITIAL_SHIPS_PER_MODEL_TYPE) # sprawdzamy czy jest w poczatkowej flocie

                    if is_initial_fleet_ship:
                        if INITIAL_FLEET_PURCHASE_WINDOW_START <= INITIAL_FLEET_PURCHASE_WINDOW_END:
                            purchase_date = get_random_date(INITIAL_FLEET_PURCHASE_WINDOW_START, INITIAL_FLEET_PURCHASE_WINDOW_END) #jezeli jest to wybieramy date na ten 1 miesiac
                        else:
                            purchase_date = START_DATE 
                    else: #jesli nie to generujemy losowa date od (po 1 miesiacu) do (2 lata przed zakonczeniem) 
                        if LATER_ACQUISITION_PURCHASE_WINDOW_START <= LATER_ACQUISITION_PURCHASE_WINDOW_END:
                            purchase_date = get_random_date(LATER_ACQUISITION_PURCHASE_WINDOW_START, LATER_ACQUISITION_PURCHASE_WINDOW_END)
                        else:
                            purchase_date = get_random_date(INITIAL_FLEET_PURCHASE_WINDOW_START, INITIAL_FLEET_PURCHASE_WINDOW_END)
                    
                    cursor.execute("""
                        INSERT INTO ship (model_id, ship_price, purchase_date) VALUES (%s, %s, %s)
                    """, (model_id_for_ship, decimal.Decimal(random.randrange(2500000, 25000000))/100,
                          purchase_date))
                    ship_id = cursor.lastrowid
                    ship_ids.append(ship_id) #to generuje te dane do statkow
                    
                    ship_initial_location = random.choice(planet_ids) 
                    ship_creation_details_list.append({
                        'id': ship_id,
                        'purchase_date': purchase_date,
                        'initial_planet_id': ship_initial_location
                    })
            conn.commit() #to tez

        if not ship_ids:
            print("No ships generated. Further flight-related data population might be limited or fail.")
            return #to na error
        
        print(f"Generated {len(ship_ids)} ships in total.")

        ship_current_status = {}
        for ship_details in ship_creation_details_list:
            ship_current_status[ship_details['id']] = {
                'location_planet_id': ship_details['initial_planet_id'],
                'available_date': ship_details['purchase_date'] 
            } #to zapisuje kiedy statek jets dostepny i gdzie jest dostepny

        # --- kastomerzy ---
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
                      decimal.Decimal(random.randrange(100000, 200000))/100, #ceny losowe (zeby nie bylo ze np. 80% ceny A to cena B, zeby normalizacja dalej byla)
                      decimal.Decimal(random.randrange(50000, 100000))/100, #ale na siebie nie nachodzą żeby nie wyszlo przypadkiem ze klasa A jest tansza od B
                      decimal.Decimal(random.randrange(10000, 50000))/100,
                      decimal.Decimal(random.randrange(1000, 1000000))/100)) #jakis losowy extra cost - moze byc bardzo wysoki i oferta sie nie oplacila, moze byc niski i byla oplacalna
                offer_ids.append(cursor.lastrowid)
        conn.commit()
        if not offer_ids:
            print("No offers generated, cannot create flights.")
            return

        # --- loty.......... ---
        print("Generating Customer Flights (with integrated Technical Repositioning)...")
        if not (offer_ids and ship_ids and customer_ids and employee_ids and planet_ids):
            print("Missing core data (offers, ships, customers, employees, or planets). Skipping flight generation.")
            return #antyerror
        else:
            for offer_id_for_flight in offer_ids: #dla wczesniej wygenerowanych ofert
                cursor.execute("SELECT model_id, duration, flight_from, flight_to FROM offer WHERE offer_id = %s", (offer_id_for_flight,))
                offer_details = cursor.fetchone() #pobieramy sobie dane oferty
                if not offer_details: continue
                
                offer_model_id, duration_at_dest_days, customer_departure_planet_id, customer_dest_planet_id = offer_details
                duration_at_dest_td = timedelta(days=float(duration_at_dest_days)) #zmieniamy se typy

                cursor.execute("SELECT class_A_seats, class_B_seats, class_C_seats FROM model WHERE model_id = %s", (offer_model_id,))
                model_seat_data = cursor.fetchone() #pobieramy dane modelu
                if not model_seat_data: continue
                class_A_capacity, class_B_capacity, class_C_capacity = model_seat_data
                model_total_capacity = class_A_capacity + class_B_capacity + class_C_capacity #tu liczymy ile jest łącznie miejsc dla pasażerów i ile na klase

                cursor.execute("SELECT ship_id FROM ship WHERE model_id = %s", (offer_model_id,))
                all_suitable_ships_for_model = [item[0] for item in cursor.fetchall()] #pobieramy statki ktore mają ten model
                if not all_suitable_ships_for_model: continue
                
                random.shuffle(all_suitable_ships_for_model) # tasujemy sobie zeby byly w losowej kolejnosci

                scheduled_trips_for_this_offer_count = 0
                for _ in range(NUM_FLIGHTS_PER_OFFER_CONCEPTUAL_TRIP): #dla kazdej oferty wybieramy randomowa ilosc lotów na oferte z hiperparemtru
                    tech_flight_scheduled_this_attempt = False
                    if scheduled_trips_for_this_offer_count >= NUM_FLIGHTS_PER_OFFER_CONCEPTUAL_TRIP : break # jak jest wystarczajaco duzo lotow to break pętli

                    chosen_ship_id_for_trip = None #inicjujemy se statek
                    
                    customer_flight_leg_duration_td = calculate_flight_duration(
                                customer_departure_planet_id,
                                customer_dest_planet_id,
                                offer_model_id,
                                cursor
                            ) #liczymy sobie jak dlugo zajmuje LOT z tej funkcji co byla wyzej
                    
                    customer_round_trip_operational_duration = (2 * customer_flight_leg_duration_td) + duration_at_dest_td #dlugosc CALEJ PODROZY

                    for current_ship_candidate_id in all_suitable_ships_for_model:
                        ship_initial_loc_id = ship_current_status[current_ship_candidate_id]['location_planet_id']
                        ship_free_from_date = ship_current_status[current_ship_candidate_id]['available_date'] #szukamy dostępnych statków
                        
                        tech_flight_departure_actual = None
                        tech_flight_arrival_actual = None
                        tech_pilot_assigned = None
                        
                        earliest_start_for_customer_flight = ship_free_from_date #wybieramy kiedy statek bedzie dostepny

                        # 1. sprawdza czy potzrebujemy technical flight do zmiany planety dla statku
                        #technical flights zmieniają lokalizacje statku z jednej planety na drugą przy okazji (i w sumie do tego służą też w tych obliczeniach, bo inaczej to byloby trudne)
                        if ship_initial_loc_id != customer_departure_planet_id: #sprawdzamy czy lokalizacja na ktorej jest statek jest inna od startowej

                            tech_flight_duration_td = calculate_flight_duration(
                                        ship_initial_loc_id,
                                        customer_departure_planet_id,
                                        offer_model_id,
                                        cursor 
                                    )  #jeżeli nie to obliczamy czas trwania przemieszczenia statku

                            ship_free_from_date_val = ship_free_from_date.date() if isinstance(ship_free_from_date, datetime) else ship_free_from_date #typ danych

                            min_tech_departure_date = ship_free_from_date_val + timedelta(days=random.randint(0, 2)) # dodajemy 0-2 dni odkąd statek jest wolny na przygotowanie nowego lotu
                            
                            end_date_val_for_calc = END_DATE.date() if isinstance(END_DATE, datetime) else END_DATE #typ danych
                            max_tech_departure_date = end_date_val_for_calc - tech_flight_duration_td - customer_round_trip_operational_duration - timedelta(days=2) # probujemy sie zmiescic do dzisiaj zeby nie bylo nieskonczonych lotów

                            if min_tech_departure_date > max_tech_departure_date:
                                continue #error

                            potential_tech_departure = get_random_date(min_tech_departure_date, max_tech_departure_date) #wybieramy sobie date z tego zakresu
                            potential_tech_arrival = potential_tech_departure + tech_flight_duration_td #obliczamy kiedy doleci
                            
                            # sprawdza błąd na wypadek jeżeli cała podróż razem z technical flight zakończy się pozniej niz dzisiaj
                            if potential_tech_arrival + customer_round_trip_operational_duration + timedelta(days=1) > end_date_val_for_calc:
                                continue

                            if is_resource_available(current_ship_candidate_id, potential_tech_departure, potential_tech_arrival, ship_schedules):
                                # uzywajac is_resource_available sprawdzamy czy statek jest dostępny. jezeli jest dostepny to szukamy załogi
                                available_pilots_for_tech = [emp_id for emp_id in employee_ids if is_resource_available(emp_id, potential_tech_departure, potential_tech_arrival, employee_schedules)]
                                if available_pilots_for_tech:
                                    tech_pilot_assigned = random.choice(available_pilots_for_tech) #losowy dostępny employee
                                    tech_flight_departure_actual = potential_tech_departure #ustalamy date
                                    tech_flight_arrival_actual = potential_tech_arrival
                                    earliest_start_for_customer_flight = tech_flight_arrival_actual + timedelta(days=random.randint(0,1)) #zapobiegawczy 1 dzien
                                    
                                    tech_flight_scheduled_this_attempt = True #potrzebny tech flight
                                else:
                                    continue 
                            else:
                                continue 
                        
                        # 2. ustalamy departure date biorąc pod uwagę ten technical flight
                        min_customer_outbound_departure = earliest_start_for_customer_flight
                        max_customer_outbound_departure = END_DATE - customer_round_trip_operational_duration - timedelta(days=1)

                        if min_customer_outbound_departure > max_customer_outbound_departure.date():
                            continue # blad

                        outbound_departure_date = get_random_date(min_customer_outbound_departure, max_customer_outbound_departure) #wybiera date kiedy wylatujemy z naszej planety
                        arrival_at_dest_date = outbound_departure_date + customer_flight_leg_duration_td #obliczamy kiedy dolecimy na planete wakacyjna
                        return_departure_date = arrival_at_dest_date + duration_at_dest_td #dzien w ktorym wylatujemy z planety wakacyjnej
                        trip_completion_date = return_departure_date + customer_flight_leg_duration_td  #dzien w ktorym wrocimy juz na planete

                        # sprawdzanie błędu (chyba nie jest potrzebne ale juz boje sie to usuwac zeby sie caly kod nie wysypał)
                        if not is_resource_available(current_ship_candidate_id, outbound_departure_date, trip_completion_date, ship_schedules):
                            continue

                        # szukamy dostepnych customerow i załogi dla tego lotu
                        current_trip_booked_seats = {'class_A': 0, 'class_B': 0, 'class_C': 0}
                        model_class_caps = {'class_A': class_A_capacity, 'class_B': class_B_capacity, 'class_C': class_C_capacity} #sprawdzamy ile model zmiesci ludzi
                        assigned_customers_for_this_trip_details = [] #lista na przechowywanie szczegołów dostępności
                        max_customers_to_book_this_flight = random.randint(1, min(model_total_capacity, len(customer_ids) if customer_ids else 0, 10)) #ile statek zmiesci ludzi
                        #moze byc mniej niz wolnych miejsc albo caly statek - wybiera minimumm

                        if customer_ids : #jesli istnieja customerzy
                            potential_customer_candidates = [cid for cid in random.sample(customer_ids, min(len(customer_ids), max_customers_to_book_this_flight + 20)) if is_resource_available(cid, outbound_departure_date, trip_completion_date, customer_schedules)]
                            #to wybieramy potencjalnych kandydatów z tych którzy są dostępni
                            for cust_id in potential_customer_candidates:
                                if len(assigned_customers_for_this_trip_details) >= max_customers_to_book_this_flight: break #wybieramy az sie skoncza miejsca
                                available_classes = [k for k,v in current_trip_booked_seats.items() if v < model_class_caps[k]] #uzupelnia ktore klasy sa jeszcze dostępne (dla pętli for)
                                if not available_classes: break #nie sprzedaje biletow jesli sie skoncza miejsca
                                chosen_class = random.choice(available_classes) #losowo wybiera klase dla customera 
                                assigned_customers_for_this_trip_details.append({'id': cust_id, 'class': chosen_class})
                                current_trip_booked_seats[chosen_class] += 1 #bookuje kolejne miejsce
                        
                        # --- załoga ---
                        num_crew_needed = random.randint(2, min(4, len(employee_ids) if employee_ids else 0)) #minimum potrzebnej załogi
                        assigned_crew_final_ids = [] #to na potem
                        if employee_ids:
                            potential_crew_candidates = [eid for eid in random.sample(employee_ids, min(len(employee_ids), num_crew_needed + 10)) if is_resource_available(eid, outbound_departure_date, trip_completion_date, employee_schedules)]
                            if len(potential_crew_candidates) >= num_crew_needed:
                                assigned_crew_final_ids = random.sample(potential_crew_candidates, num_crew_needed)
                        
                        chosen_ship_id_for_trip = current_ship_candidate_id #wybiera losowo

                        if tech_flight_scheduled_this_attempt and tech_pilot_assigned and tech_flight_departure_actual and tech_flight_arrival_actual:
                            cursor.execute("""
                                INSERT INTO technical_flights (ship_id, employee_id, flight_from, flight_to, departure)
                                VALUES (%s, %s, %s, %s, %s)
                            """, (chosen_ship_id_for_trip, tech_pilot_assigned, ship_initial_loc_id, customer_departure_planet_id, tech_flight_departure_actual))
                            
                            if chosen_ship_id_for_trip not in ship_schedules: ship_schedules[chosen_ship_id_for_trip] = []
                            ship_schedules[chosen_ship_id_for_trip].append((tech_flight_departure_actual, tech_flight_arrival_actual))
                            
                            if tech_pilot_assigned not in employee_schedules: employee_schedules[tech_pilot_assigned] = []
                            employee_schedules[tech_pilot_assigned].append((tech_flight_departure_actual, tech_flight_arrival_actual))
#wrzucamy wszystko dobazy danych
                        cursor.execute("INSERT INTO flight (ship_id, offer_id, departure) VALUES (%s, %s, %s)", (chosen_ship_id_for_trip, offer_id_for_flight, outbound_departure_date))
                        flight_id_outbound = cursor.lastrowid
                        cursor.execute("INSERT INTO flight (ship_id, offer_id, departure) VALUES (%s, %s, %s)", (chosen_ship_id_for_trip, offer_id_for_flight, return_departure_date))
                        flight_id_return = cursor.lastrowid

                        if chosen_ship_id_for_trip not in ship_schedules: ship_schedules[chosen_ship_id_for_trip] = []
                        ship_schedules[chosen_ship_id_for_trip].append((outbound_departure_date, trip_completion_date))
                        
                        ship_current_status[chosen_ship_id_for_trip]['location_planet_id'] = customer_departure_planet_id # Returns to home base of offer
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

        # --- roczne ceny paliwa generujemy randomow ---
        print("Generating Year Fuel Prices...")
        current_yr = START_DATE.year
        for i in range(NUM_YEAR_FUEL_ENTRIES):
            year_date_fuel = datetime(current_yr + i, random.randint(1,12), random.randint(1,28)).date()
            cursor.execute("""
                INSERT INTO year_fuel (year, price) VALUES (%s, %s)
            """, (year_date_fuel, decimal.Decimal(random.randrange(100, 500))/100))
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
#tu jeszcze obsługi błędów
if __name__ == '__main__':
    populate_data() 
    #i caly kod skonczony 