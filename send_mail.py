import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv
def dict_to_html_table(title, data_dict, max_items):
    """
    Convierte un diccionario en una tabla HTML ordenada por contador.
    max_items: cantidad máxima de elementos a mostrar (si hay menos, se muestran todos)
    """
    sorted_items = sorted(data_dict.items(), key=lambda x: x[1], reverse=True)[:max_items]

    rows = ""
    for key, value in sorted_items:
        rows += f"""
        <tr>
            <td>{key}</td>
            <td style="text-align:center;">{value}</td>
        </tr>
        """

    table_html = f"""
    <h3>{title}</h3>
    <table style="border-collapse: collapse; width: 60%;">
        <thead>
            <tr style="background-color:#f2f2f2;">
                <th style="border:1px solid #ddd; padding:8px;">Elemento</th>
                <th style="border:1px solid #ddd; padding:8px;">Intentos</th>
            </tr>
        </thead>
        <tbody>
            {rows}
        </tbody>
    </table>
    <br>
    """
    return table_html


def send_email(subject, passwords_dict, rutas_dict, top_n, recipients):
    """
    Envía un correo con tablas HTML de top usuarios y rutas.
    - passwords_dict: {'usuario': contador}
    - rutas_dict: {'ruta': contador}
    - top_n: cantidad de elementos que se quieren mostrar (sin límite)
    - recipients: lista de emails
    """
    try:
       
        load_dotenv()
        sender = os.getenv("EMAIL_USER")
        password = os.getenv("EMAIL_PASSWORD")
        if not password:
            raise ValueError("No se encontró EMAIL_PASSWORD en variables de entorno.")

        # Texto plano
        text_body = "Se detectaron múltiples intentos sospechosos.\n\n"

        text_body += "Top Contraseñas SSH:\n"
        for i, (u, c) in enumerate(sorted(passwords_dict.items(), key=lambda x: x[1], reverse=True)[:top_n]):
            text_body += f"{i+1}. {u} -> {c}\n"

        text_body += "\nTop Rutas HTTP:\n"
        for i, (r, c) in enumerate(sorted(rutas_dict.items(), key=lambda x: x[1], reverse=True)[:top_n]):
            text_body += f"{i+1}. {r} -> {c}\n"

        # HTML
        passwords_table = dict_to_html_table("Top Contraseñas SSH", passwords_dict, top_n)
        rutas_table = dict_to_html_table("Top Rutas HTTP", rutas_dict, top_n)
        
        html_body = f"""
        <html>
          <body>
            <h2 style="color:red;">Resumen honeypot</h2>

            {passwords_table}
            {rutas_table}

          </body>
        </html>
        """

        # Crear mensaje MIME
        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"] = sender
        msg["To"] = ", ".join(recipients)

        msg.attach(MIMEText(text_body, "plain", "utf-8"))
        msg.attach(MIMEText(html_body, "html", "utf-8"))

        # Enviar correo
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp_server:
            smtp_server.login(sender, password)
            smtp_server.sendmail(sender, recipients, msg.as_string())

        print("Correo enviado correctamente.")
        return True

    except Exception as e:
        print(f"Error enviando correo: {e}")
        return False