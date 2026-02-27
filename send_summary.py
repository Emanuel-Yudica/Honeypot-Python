import os
import smtplib
import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv

def dict_to_html_table(title, data_dict, max_items):
    """Convierte un diccionario en una tabla HTML ordenada."""
    sorted_items = sorted(data_dict.items(), key=lambda x: x[1], reverse=True)[:max_items]
    
    rows = ""
    for key, value in sorted_items:
        rows += f"""
        <tr>
            <td style="border:1px solid #ddd; padding:8px;">{key}</td>
            <td style="border:1px solid #ddd; padding:8px; text-align:center;">{value}</td>
        </tr>
        """

    return f"""
    <h3 style="font-family: Arial, sans-serif; color: #333;">{title}</h3>
    <table style="border-collapse: collapse; width: 80%; font-family: Arial, sans-serif;">
        <thead>
            <tr style="background-color:#f2f2f2; border:1px solid #ddd;">
                <th style="padding:12px; text-align:left;">Elemento</th>
                <th style="padding:12px; text-align:center;">Intentos</th>
            </tr>
        </thead>
        <tbody>
            {rows}
        </tbody>
    </table>
    <br>
    """

def generate_full_html(passwords_dict, rutas_dict, top_n, ips_unicas=None, start_time=None, end_time=None):
    passwords_table = dict_to_html_table(f"Top {len(passwords_dict)} Contraseñas SSH", passwords_dict, top_n)
    rutas_table = dict_to_html_table(f"Top {len(rutas_dict)} Rutas HTTP", rutas_dict, top_n)
    
    ips_html = ""
    # Verificamos que ips_unicas exista y sea una lista/set antes de iterar
    if ips_unicas and hasattr(ips_unicas, "__iter__"):
        ips_list = "".join([f"<li>{ip}</li>" for ip in sorted(ips_unicas)])
        ips_html = f"<h3>IPs Detectadas</h3><ul>{ips_list}</ul>"
    else:
        ips_html = "<h3>IPs Detectadas</h3><p>No se registraron conexiones.</p>"

    return f"""
    <html>
      <body style="font-family: sans-serif; padding: 20px;">
        <h2 style="color: #d9534f; border-bottom: 2px solid #d9534f; padding-bottom: 10px;">
            Resumen de Actividad - Honeypot
        </h2>
        <p><strong>Hora de inicio:</strong> {start_time}</p>
        <p><strong>Hora de finalización:</strong> {end_time}</p>
        <hr>
        {ips_html}
        {passwords_table}
        {rutas_table}
        <p style="font-size: 0.8em; color: #777; margin-top: 30px;">Generado automáticamente por el Sistema Honeypot.</p>
      </body>
    </html>
    """
def save_to_html_file(html_content,filename=None):
    """Guarda el contenido HTML en un archivo físico."""
    date = datetime.date.today()
    if filename is None:
        filename = f"summary_data_{date}.html"

    try:
        with open(filename, "w", encoding="utf-8") as f:
            f.write(html_content)
        print(f"Resumen guardado correctamente en: {filename}")
        return filename
    except Exception as e:
        print(f"Error al guardar archivo HTML: {e}")
        return None

def send_email(subject, recipients, html_body):
    """Envía el correo usando el HTML ya generado."""
    try:
        load_dotenv()
        sender = os.getenv("EMAIL_USER")
        password = os.getenv("EMAIL_PASSWORD")
        
        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"] = sender
        msg["To"] = ", ".join(recipients) if isinstance(recipients, list) else recipients

        # Adjuntar versión HTML
        msg.attach(MIMEText(html_body, "html", "utf-8"))

        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp_server:
            smtp_server.login(sender, password)
            smtp_server.sendmail(sender, recipients, msg.as_string())

        print("Correo enviado correctamente.")
        return True
    except Exception as e:
        print(f"Error enviando correo: {e}")
        return False