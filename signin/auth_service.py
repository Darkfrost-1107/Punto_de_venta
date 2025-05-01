from sqlqueries import QueriesSQLite

class AuthService:
    @staticmethod
    def verificar_usuario(username, password):
        connection = QueriesSQLite.create_connection("pdvDB.sqlite")
        users = QueriesSQLite.execute_read_query(connection, "SELECT * FROM usuarios")

        if not users:
            # Si no hay usuarios, creamos el primer usuario
            usuario_tuple = ('usuario', 'Usuario Inicio', '123', 'admin')
            crear_usuario = "INSERT INTO usuarios (username, nombre, password, tipo) VALUES (?, ?, ?, ?);"
            QueriesSQLite.execute_query(connection, crear_usuario, usuario_tuple)
            return None, 'Se creó el primer usuario. Usuario: usuario, Contraseña: 123'

        for user in users:
            if user[0] == username:
                if user[2] == password:
                    return {
                        'nombre': user[1],
                        'username': user[0],
                        'tipo': user[3]
                    }, None
                else:
                    return None, 'Usuario o contraseña incorrecta'

        return None, 'Usuario o contraseña incorrecta'