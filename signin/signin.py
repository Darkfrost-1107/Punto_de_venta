from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.lang import Builder

from .auth_service import AuthService  # Importamos el módulo de autenticación

Builder.load_file('signin/signin.kv')

class SigninWindow(BoxLayout):
    def __init__(self, poner_usuario_callback, **kwargs):
        super().__init__(**kwargs)
        self.poner_usuario = poner_usuario_callback

    def verificar_usuario(self, username, password):
        if username == '' or password == '':
            self.ids.signin_notificacion.text = 'Falta nombre de usuario y/o contraseña'
            return

        # Llamamos al servicio de autenticación
        usuario, error = AuthService.verificar_usuario(username, password)

        if error:
            self.ids.signin_notificacion.text = error
        else:
            self.ids.username.text = ''
            self.ids.password.text = ''
            self.ids.signin_notificacion.text = ''
            if usuario['tipo'] == 'trabajador':
                self.parent.parent.current = 'scrn_ventas'
            elif usuario['tipo'] == 'admin':
                self.parent.parent.current = 'scrn_compras'
            else:
                self.parent.parent.current = 'scrn_admin'
            self.poner_usuario(usuario)
            print(f"Cambiando a la vista: {self.parent.parent.current}")


class SigninApp(App):
    def build(self):
        return SigninWindow()

if __name__ == "__main__":
    SigninApp().run()