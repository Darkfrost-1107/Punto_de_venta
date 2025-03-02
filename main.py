from kivy.app import App
from kivy.uix.boxlayout import BoxLayout

from sqlqueries import QueriesSQLite
from signin.signin import SigninWindow
from admin.admin import AdminWindow
from ventas.ventas import VentasWindow
from recibo import GeneradorRecibos
from gdrive import GDriveAPI
#from compras.compras import ComprasWindow

from datetime import datetime
import atexit

# agregado queriessqlite.create_tables()
class MainWindow(BoxLayout):
	QueriesSQLite.create_tables()
	def __init__(self, **kwargs):
		super().__init__(*kwargs)
		self.admin_widget=AdminWindow()
		self.ventas_widget=VentasWindow(self.admin_widget.actualizar_productos)
		#self.compras_widget=ComprasWindow(self.admin_widget.actualizar_productos)
		self.signin_widget=SigninWindow(self.ventas_widget.poner_usuario)
		self.ids.scrn_signin.add_widget(self.signin_widget)
		self.ids.scrn_ventas.add_widget(self.ventas_widget)
		#self.ids.scrn_compras.add_widget(self.compras_widget)
		self.ids.scrn_admin.add_widget(self.admin_widget)

class MainApp(App):
	def build(self):
		return MainWindow()

def backup_database():
	"""Backup the database and show a popup with the result."""
	gdrive = GDriveAPI()
	fecha_hora_actual = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
	backup_file_id = gdrive.backup(local_file='pdvDB.sqlite', remote_name=f'pdvDB_backup_{fecha_hora_actual}.sqlite', folder_name='Punto de Venta (Respaldos)')
	print('')
	if backup_file_id:
		print("Backup Successful", f"Backup file ID: {backup_file_id}")
	else:
		print("Backup Failed", "Failed to backup the database.")
	print('')

def restore_database():
	"""Restore the database and show a popup with the result."""
	gdrive = GDriveAPI()
	restored = gdrive.restore(local_file='pdvDB.sqlite',  remote_name='pdvDB_backup', folder_name='Punto de Venta (Respaldos)')
	print('')
	if restored:
		print("Restore Successful", "Database restored successfully!")
	else:
		print("Restore Failed", "Failed to restore the database.")
	print('')

if __name__=="__main__":
	#QueriesSQLite.drop_tables()
	restore_database()

	MainApp().run()

	atexit.register(backup_database)