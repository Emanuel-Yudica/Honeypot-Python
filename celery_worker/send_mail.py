import smtplib
from email.mime.text import MIMEText


# ip=["192.168.1.50", "192.168.1.51", "192.168.1.52","192.168.1.53"]
def send_email(subject, body, recipients):
    # crear mensaje
    sender="grupoc198@gmail.com"
    password="dwaf cjkd lfjg fhqj"
    msg = MIMEText(body)
    msg['Subject'] = subject
    msg['From'] = sender
    msg['To'] = ', '.join(recipients)

    # conectar a Gmail SMTP y enviar
    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp_server:
        smtp_server.login(sender, password)
        smtp_server.sendmail(sender, recipients, msg.as_string())

    return True



# send_email(
#     subject="Alerta de seguridad",
#     body=f"Se han detectado {len(ip)} IPs conectadas a la máquina de Honeypot en la ultima hora\n{ip}",
#     recipients=["emanuelyudica2@gmail.com"],
# )
