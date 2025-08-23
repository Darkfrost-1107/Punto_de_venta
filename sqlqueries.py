import os
import sqlite3
from sqlite3 import Error
from kivy.utils import platform

class QueriesSQLite:
    def use_path(path):
        if platform == 'android':
            from android.storage import app_storage_path
            db_path = os.path.join(app_storage_path(), path)
        else:
            # Para Windows/Linux/Mac
            db_path = path
        return db_path

    def create_connection(path):
        # Obtener ruta correcta según la plataforma
        db_path = QueriesSQLite.use_path(path)

        connection = None
        try:
            connection = sqlite3.connect(db_path)
            print("Connection to SQLite DB successful")
        except Error as e:
            print(f"The error '{e}' occurred")

        return connection

    # added return
    def execute_query(connection, query, data_tuple):
        cursor = connection.cursor()
        try:
            cursor.execute(query, data_tuple)
            connection.commit()
            print("Query executed successfully")
            return cursor.lastrowid
        except Error as e:
            print(f"The error '{e}' occurred")

    # added data_tuple
    def execute_read_query(connection, query, data_tuple=()):
        cursor = connection.cursor()
        result = None
        try:
            cursor.execute(query, data_tuple)
            result = cursor.fetchall()
            return result
        except Error as e:
            print(f"The error '{e}' occurred")

    # esto es nuevo
    def create_tables():
        connection = QueriesSQLite.create_connection("pdvDB.sqlite")

        tabla_productos = """
        CREATE TABLE IF NOT EXISTS productos(
         codigo TEXT PRIMARY KEY, 
         nombre TEXT NOT NULL, 
         precio REAL NOT NULL, 
         cantidad INTEGER NOT NULL
        );
        """

        tabla_usuarios = """
        CREATE TABLE IF NOT EXISTS usuarios(
         username TEXT PRIMARY KEY, 
         nombre TEXT NOT NULL, 
         password TEXT NOT NULL,
         tipo TEXT NOT NULL
        );
        """

        tabla_ventas = """
        CREATE TABLE IF NOT EXISTS ventas(
         id INTEGER PRIMARY KEY, 
         total REAL NOT NULL, 
         fecha TIMESTAMP,
         username TEXT  NOT NULL, 
         FOREIGN KEY(username) REFERENCES usuarios(username)
        );
        """

        tabla_ventas_detalle = """
        CREATE TABLE IF NOT EXISTS ventas_detalle(
         id INTEGER PRIMARY KEY, 
         id_venta TEXT NOT NULL, 
         precio REAL NOT NULL,
         producto TEXT NOT NULL,
         cantidad INTEGER NOT NULL,
         FOREIGN KEY(id_venta) REFERENCES ventas(id),
         FOREIGN KEY(producto) REFERENCES productos(codigo)
        );
        """

        tabla_compras = """
        CREATE TABLE compras (
        id INTEGER PRIMARY KEY,               -- Identificador único de la compra
        total REAL NOT NULL,                  -- Monto total de la compra
        fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP,  -- Fecha y hora de la compra
        proveedor TEXT NOT NULL,              -- Nombre del proveedor
        observacion TEXT                      -- Observaciones adicionales sobre la compra
        );
        """

        tabla_compras_detalle = """
        CREATE TABLE compras_detalle (
        id INTEGER PRIMARY KEY,               -- Identificador único del detalle
        id_compra INTEGER NOT NULL,           -- Identificador de la compra
        producto TEXT NOT NULL,               -- Código del producto adquirido
        precio REAL NOT NULL,                 -- Precio unitario del producto en la compra
        cantidad INTEGER NOT NULL,            -- Cantidad adquirida del producto
        FOREIGN KEY (id_compra) REFERENCES compras (id),
        FOREIGN KEY (producto) REFERENCES productos (codigo)
        );
        """

        QueriesSQLite.execute_query(connection, tabla_productos, tuple()) 
        QueriesSQLite.execute_query(connection, tabla_usuarios, tuple()) 
        QueriesSQLite.execute_query(connection, tabla_ventas, tuple()) 
        QueriesSQLite.execute_query(connection, tabla_ventas_detalle, tuple())
        QueriesSQLite.execute_query(connection, tabla_compras, tuple())
        QueriesSQLite.execute_query(connection, tabla_compras_detalle, tuple())

    def drop_tables():
        connection = QueriesSQLite.create_connection("pdvDB.sqlite")

        eliminar_tablas = """
        DROP TABLE IF EXISTS compras_detalle;
        DROP TABLE IF EXISTS compras;
        DROP TABLE IF EXISTS ventas_detalle;
        DROP TABLE IF EXISTS ventas;
        DROP TABLE IF EXISTS usuarios;
        DROP TABLE IF EXISTS productos;
        """
        
        try:
            QueriesSQLite.execute_query(connection, eliminar_tablas, tuple())
            print("Todas las tablas han sido eliminadas correctamente.")
        except Exception as e:
            print(f"Error al eliminar las tablas: {e}")




if __name__=="__main__":
    from datetime import datetime, timedelta
    connection = QueriesSQLite.create_connection("pdvDB.sqlite")


    fecha1= datetime.today()-timedelta(days=5)
    neuva_data=(fecha1, 4)
    actualizar = """
    UPDATE
      ventas
    SET
      fecha=?
    WHERE
      id = ?
    """

    QueriesSQLite.execute_query(connection, actualizar, neuva_data)

    select_ventas = "SELECT * from ventas"
    ventas = QueriesSQLite.execute_read_query(connection, select_ventas)
    if ventas:
        for venta in ventas:
            print("type:", type(venta), "venta:",venta)


    select_ventas_detalle = "SELECT * from ventas_detalle"
    ventas_detalle = QueriesSQLite.execute_read_query(connection, select_ventas_detalle)
    if ventas_detalle:
        for venta in ventas_detalle:
            print("type:", type(venta), "venta:",venta)

    # crear_producto = """
    # INSERT INTO
    #   productos (codigo, nombre, precio, cantidad)
    # VALUES
    #     ('111', 'leche 1l', 20.0, 20),
    #     ('222', 'cereal 500g', 50.5, 15), 
    #     ('333', 'yogurt 1L', 25.0, 10),
    #     ('444', 'helado 2L', 80.0, 20),
    #     ('555', 'alimento para perro 20kg', 750.0, 5),
    #     ('666', 'shampoo', 100.0, 25),
    #     ('777', 'papel higiénico 4 rollos', 35.5, 30),
    #     ('888', 'jabón para trastes', 65.0, 5)
    # """
    # QueriesSQLite.execute_query(connection, crear_producto, tuple()) 

    # select_products = "SELECT * from productos"
    # productos = QueriesSQLite.execute_read_query(connection, select_products)
    # for producto in productos:
    #     print(producto)


    # usuario_tuple=('test', 'Persona 1', '123', 'admin')
    # crear_usuario = """
    # INSERT INTO
    #   usuarios (username, nombre, password, tipo)
    # VALUES
    #     (?,?,?,?);
    # """
    # QueriesSQLite.execute_query(connection, crear_usuario, usuario_tuple) 


    # select_users = "SELECT * from usuarios"
    # usuarios = QueriesSQLite.execute_read_query(connection, select_users)
    # for usuario in usuarios:
    #     print("type:", type(usuario), "usuario:",usuario)

    # neuva_data=('Persona 55', '123', 'admin', 'persona1')
    # actualizar = """
    # UPDATE
    #   usuarios
    # SET
    #   nombre=?, password=?, tipo = ?
    # WHERE
    #   username = ?
    # """
    # QueriesSQLite.execute_query(connection, actualizar, neuva_data)

    # select_users = "SELECT * from usuarios"
    # usuarios = QueriesSQLite.execute_read_query(connection, select_users)
    # for usuario in usuarios:
    #     print("type:", type(usuario), "usuario:",usuario)



    # select_products = "SELECT * from productos"
    # productos = QueriesSQLite.execute_read_query(connection, select_products)
    # for producto in productos:
    #     print(producto)

    # select_users = "SELECT * from usuarios"
    # usuarios = QueriesSQLite.execute_read_query(connection, select_users)
    # for usuario in usuarios:
    #     print("type:", type(usuario), "usuario:",usuario)

    # producto_a_borrar=('888',)
    # borrar = """DELETE from productos where codigo = ?"""
    # QueriesSQLite.execute_query(connection, borrar, producto_a_borrar)

    # select_products = "SELECT * from productos"
    # productos = QueriesSQLite.execute_read_query(connection, select_products)
    # for producto in productos:
    #     print(producto)

