import psycopg2 as pg2
# Define SQL queries to create tables if they don't exist
customers_table_query = """
CREATE TABLE IF NOT EXISTS customers(
    customer_id SERIAL PRIMARY KEY,
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL UNIQUE,
    village VARCHAR(100) NOT NULL,
    phone VARCHAR(20) NOT NULL UNIQUE,
    gmail VARCHAR(100) NOT NULL UNIQUE
)
"""

measurements_table_query = """
CREATE TABLE IF NOT EXISTS measurements(
    customer_id INTEGER REFERENCES customers(customer_id) ON DELETE CASCADE,
    chest VARCHAR(10),
    waist VARCHAR(10),
    hips VARCHAR(10),
    shoulder_width VARCHAR(10),
    sleeve_length VARCHAR(10),
    arm_hole VARCHAR(10),
    neck_size VARCHAR(10),
    collar_size VARCHAR(10),
    inseam VARCHAR(10),
    outseam VARCHAR(10),
    thigh VARCHAR(10),
    knee VARCHAR(10),
    ankle VARCHAR(10),
    height VARCHAR(10),
    UNIQUE(customer_id)
)
"""

products_table_query = """
CREATE TABLE IF NOT EXISTS products(
    product_id SERIAL PRIMARY KEY,
    customer_id INTEGER REFERENCES customers(customer_id) ON DELETE CASCADE,
    product_name VARCHAR(30) NOT NULL,
    garment_drop_off TIMESTAMP NOT NULL,
    requested_pick_up_date VARCHAR(20) NOT NULL,
    garment_pick_up TIMESTAMP
)
"""

payments_table_query = """
CREATE TABLE IF NOT EXISTS payments(
    payment_id VARCHAR(30) PRIMARY KEY,
    customer_id INTEGER REFERENCES customers(customer_id) ON DELETE CASCADE,
    amount INTEGER NOT NULL,
    payment_date TIMESTAMP NOT NULL,
    total_amount INTEGER NOT NULL,
    advance_amount INTEGER,
    due_amount INTEGER
)
"""


# Define a class for managing the database and operations
class TailorMeasure:
    def __init__(self):
        # Database connection parameters
        database_name = "tailormeasure"
        database_params = {
            "dbname": database_name,
            "user": open(r"C:\Users\DELL\Desktop\DatabaseCredentials.txt", "r").readline().split(",")[0],
            "password": open(r"C:\Users\DELL\Desktop\DatabaseCredentials.txt", "r").readline().split(",")[1]
        }

        # Connect to the PostgreSQL database
        self.conn = pg2.connect(**database_params)
        self.cur = self.conn.cursor()
        self.conn.autocommit = True

        # Create necessary tables if they don't exist
        self.cur.execute(customers_table_query)
        self.cur.execute(measurements_table_query)
        self.cur.execute(products_table_query)
        self.cur.execute(payments_table_query)

    def add_customer(self):
        # Function to add a new customer to the database
        first_name = input("Enter first name of the customer: ")
        last_name = input("Enter second name of the customer: ")
        village = input("Enter customer village name: ")
        phone = input("Enter customer phone number: ")
        gmail = input("Enter customer gmail/email: ")

        # Insert customer data into the 'customers' table
        self.cur.execute("""insert into customers(first_name,last_name,phone,village,gmail)
                                    values(%s,%s,%s,%s,%s)""", (first_name, last_name, village, phone, gmail))

        # Insert a corresponding entry into the 'measurements' table
        self.cur.execute("""insert into measurements(customer_id)
                                values((select customer_id from customers where first_name = %s))""", (first_name,))

        # Call methods to add measurements and products for the customer
        self.add_measurements(first_name)
        self.add_product(first_name)

    def show_customers(self):
        # Function to display all customers
        self.cur.execute("""select * from customers order by customer_id""")
        customers = self.cur.fetchall()
        for i in customers:
            print(i[1], i[2])

    def show_customer_measurements(self):
        # Function to display measurements of a specific customer
        name = input("Enter the first_name of the customer that you want to see measurements: ")

        # Retrieve column names for measurements table
        self.cur.execute("""select column_name from information_schema.columns where table_name = 'measurements'
                        order by ordinal_position""")
        measurement_names = [i[0] for i in self.cur.fetchall()][1:]

        # Retrieve customer names
        self.cur.execute("select first_name from customers")
        customer_names = [i[0] for i in self.cur.fetchall()]
        if name not in customer_names:
            return print(f"No customer named {name} is registered.")

        # Retrieve and display measurements for the customer
        self.cur.execute(""" select * from measurements where customer_id =
        (select customer_id from customers where first_name = %s) """, (name,))
        measurements = self.cur.fetchall()
        print(measurements)
        if len(measurements) == 0:
            return print("No measurements added")
        print(f"{name}'s measurements")
        print(measurement_names)
        for i in range(1, len(measurements[0])):
            print(measurement_names[i-1],measurements[0][i])
            if measurements[0][i] is None:
                continue
            print(measurement_names[i-1], ":", measurements[0][i])

    def add_measurements(self, first_name):
        # Function to add measurements for a customer
        self.cur.execute("select first_name from customers")
        customer_names = [i[0] for i in self.cur.fetchall()]
        if first_name not in customer_names:
            return print(f"No customer named {first_name} is registered.")
        print("Add Measurements.")

        # Choose measurement types and input sizes
        measurement_indexes = list(map(int, input("""
    Choose below option
    If you add more than one measurement, give input as comma separated :
            1. chest
            2. waist
            3. hips
            4. shoulder_width
            5. sleeve_length
            6. arm_hole
            7. neck_size
            8. collar_size
            9. inseam
            10. outseam
            11. thigh
            12. knee
            13. ankle
            14. height
    : """).split(",")))

        self.cur.execute("""select column_name from information_schema.columns where table_name = 'measurements'
                        order by ordinal_position""")
        measurement_names = [i[0] for i in self.cur.fetchall()][1:]

        # Input measurement sizes and update the 'measurements' table
        required_measurement_sizes = [input(f"Enter {measurement_names[i - 1]} size: ") for i in measurement_indexes]
        for i in range(len(measurement_indexes)):
            self.cur.execute("""update measurements
                            set {} = {}
            where customer_id = (select customer_id from customers where
            first_name = %s)""".format(measurement_names[measurement_indexes[i] - 1],
                                       required_measurement_sizes[i - 1]), (first_name,))
        print('Measurements added successfully.')

    def delete_customer(self, first_name):
        # Function to delete a customer by first name
        self.cur.execute("select first_name from customers")
        customer_names = [i[0] for i in self.cur.fetchall()]
        if first_name not in customer_names:
            return print(f"No customer named {first_name} is registered.")
        self.cur.execute("""delete from customers where first_name = %s""", (first_name,))

    def add_product(self, first_name):
        # Function to add a product for a customer
        self.cur.execute("select first_name from customers")
        customer_names = [i[0] for i in self.cur.fetchall()]
        if first_name not in customer_names:
            return print(f"No customer named {first_name} is registered.")
        print("Add products.")
        product_name = input("Enter product name: ")
        requested_pick_up_date = input("Enter requested pick up date in format(DD-MM-YYYY) : ")

        # Insert product data into the 'products' table
        self.cur.execute(f"""insert into products(customer_id,product_name,garment_drop_off,requested_pick_up_date) 
                        values((select customer_id from customers where first_name = %s),%s,current_timestamp,%s)""",
                         (first_name, product_name, requested_pick_up_date))
        print("Products added successfully")

    def show_products(self, first_name):
        # Function to display products of a specific customer
        self.cur.execute("select first_name from customers")
        customer_names = [i[0] for i in self.cur.fetchall()]
        if first_name not in customer_names:
            return print(f"No customer named {first_name} is registered.")

        # Retrieve column names for products table
        self.cur.execute("""select column_name from information_schema.columns where table_name = 'products'
                        order by ordinal_position """)
        products_table_columns = [i[0] for i in self.cur.fetchall()]
        print(products_table_columns)

        # Retrieve and display products for the customer
        self.cur.execute(""" select * from products where customer_id = 
        (select customer_id from customers where first_name = %s) order by customer_id""", (first_name,))
        for i in self.cur.fetchall():
            print(i)
            for j in range(len(i)):
                print(f"{products_table_columns[j]} : {i[j]}")


# Create an instance of the TailorMeasure class
Tailor1 = TailorMeasure()

while True:
    print("""Choose one of the below options:
    1. Add Customer
    2. Show Customers
    3. Show Customer Measurements
    4. Add Measurements
    5. Delete Customer
    6. Add Product
    7. Show Products
    8. Exit
    """)
    choice = input("Enter your choice: ")

    if choice == '1':
        Tailor1.add_customer()
    elif choice == '2':
        Tailor1.show_customers()
    elif choice == '3':
        Tailor1.show_customer_measurements()
    elif choice == '4':
        first_name = input("Enter first name of customer that you want to add the measurements: ")
        Tailor1.add_measurements(first_name)
    elif choice == '5':
        first_name = input("Enter first name of customer that you want to delete: ")
        Tailor1.delete_customer(first_name)
    elif choice == '6':
        first_name = input("Enter first name of customer that you want to add the product: ")
        Tailor1.add_product(first_name)
    elif choice == '7':
        first_name = input("Enter first name of customer that you want to see the products: ")
        Tailor1.show_products(first_name)
    elif choice == '8':
        break
    else:
        print("Invalid choice. Please enter a valid option (1-8).")
