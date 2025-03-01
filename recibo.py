from reportlab.lib.units import mm
from reportlab.pdfgen import canvas
from datetime import datetime
import os
import webbrowser

class GeneradorRecibos:
    def __init__(self, folder="recibos", store_name="COMERCIAL EMILY", store_address="Urb. Juan El Bueno A1"):
        """
        Initialize the receipt generator with default store information and folder.
        
        :param folder: Folder where receipts will be saved (default: "recibos").
        :param store_name: Name of the store (default: "COMERCIAL EMILY").
        :param store_address: Address of the store (default: "Urb. Juan El Bueno A1").
        """
        self.folder = folder
        self.store_name = store_name
        self.store_address = store_address

        # Create the folder if it doesn't exist
        if not os.path.exists(self.folder):
            os.makedirs(self.folder)

    def create_receipt(self, items, payment, total, change):
        """
        Generate a receipt PDF with the given items, payment, total, and change.
        
        :param items: List of tuples (article, price, quantity).
        :param payment: Amount paid by the customer.
        :param total: Total amount of the purchase.
        :param change: Change to be returned to the customer.
        :return: Path to the generated PDF file.
        """
        # Generate a unique ticket number based on existing files
        ticket_number = f"{len([name for name in os.listdir(self.folder) if os.path.isfile(os.path.join(self.folder, name))]):05d}"
        filename = os.path.join(self.folder, f'recibo_{datetime.now().strftime("%d%m%y")}_{ticket_number}.pdf')

        # Set the width to 7.5 cm and adjust height dynamically
        width = 75 * mm
        height = (110 + 5 * len(items)) * mm

        # Create the PDF
        c = canvas.Canvas(filename, pagesize=(width, height))
        c.setFont("Helvetica", 10)  # Mindful font

        # Start position for content
        x = 6 * mm  # 1 cm margin
        y = height - 30 * mm  # Start 4 cm from the top

        # Store name (centered)
        c.setFont("Helvetica-Bold", 15)
        c.drawCentredString(width / 2, y, self.store_name.upper())
        y -= 6 * mm

        # Store address (centered)
        c.setFont("Helvetica", 12)
        c.drawCentredString(width / 2, y, self.store_address)
        y -= 8 * mm

        # Date and ticket number
        c.setFont("Helvetica", 10)
        date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        c.drawString(x, y, f"Fecha: {date}")
        y -= 5 * mm
        c.drawString(x, y, f"Recibo #{ticket_number}")
        y -= 7 * mm

        # Table-like information: Article - Price - Quantity - Subtotal
        c.setFont("Courier-Bold", 9)
        c.line(x, y, width - x, y)
        y -= 3 * mm
        c.drawString(x, y,"ARTÍCULO     PRECIO CANT. IMPORTE")
        y -= 1 * mm
        c.line(x, y, width - x, y)
        y -= 4 * mm

        c.setFont("Courier", 7)
        for item in items:
            article, price, quantity = item
            subtotal = price * quantity
            # 1234567890123456 89012345 7890123 567890123
            # 1234567890123456 12345678 1234567 123456789
            # ARTÍCULO           PRECIO   CANT.   IMPORTE
            item_str = ''
            item_str += article[:15].upper().ljust(15) + ' '
            item_str += f"{price:.2f}".rjust(8) + ' '
            item_str += f"{quantity:.2f}".rjust(7) + ' '
            item_str += f"{subtotal:.2f}".rjust(9) + ' '
            c.drawString(x, y, item_str)
            y -= 4 * mm
        
        # Payment
        c.line(x, y, width - x, y)
        y -= 4 * mm
        c.setFont("Helvetica-Bold", 10)
        c.drawString(x + 2 * mm, y, f"PAGO:")
        c.drawString(width - x - len(f"{payment:.2f}") * 1.9 * mm, y, f"{payment:.2f}")
        y -= 5 * mm
        # Total
        c.drawString(x + 2 * mm, y, f"TOTAL:")
        c.drawString(width - x - len(f"{total:.2f}") * 1.9 * mm, y, f"{total:.2f}")
        y -= 5 * mm
        # Change
        c.drawString(x + 2 * mm, y, f"CAMBIO:")
        c.drawString(width - x - len(f"{change:.2f}") * 1.9 * mm, y, f"{change:.2f}")
        y -= 2 * mm
        c.line(x, y, width - x, y)
        y -= 10 * mm

        # Footer messages (centered)
        c.setFont("Helvetica-Bold", 14)
        c.drawCentredString(width / 2, y, "Gracias por su compra")
        y -= 5 * mm
        c.setFont("Helvetica", 10)
        c.drawCentredString(width / 2, y, "No se aceptan devoluciones")

        # Save the PDF
        c.save()

        return filename

    def open_print_dialog(self, filepath):
        """
        Open the PDF file in the default browser.
        
        :param filepath: Path to the PDF file.
        """
        try:
            # Open the PDF file in the default browser
            webbrowser.open(filepath)
        except Exception as e:
            print(f"Error opening PDF: {e}")

def mainRecibo():
    g = GeneradorRecibos()

    items = [
        ['Camiseta', 20.0, 2],
        ['Pantalón', 40.0, 1],
        ['Zapatos', 60.0, 3],
        ['12345678901234567890', 10.0, 5]
    ]
    total = 8
    recibido = 10
    cambio = recibido - total
    
    filename = g.create_receipt(items, recibido, total, cambio)
    g.open_print_dialog(filename)

if __name__=='__main__':
	mainRecibo()