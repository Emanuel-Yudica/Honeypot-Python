def parser(q):
    while True:
        line = q.get()
        if line['server'] == "SSH":
            print("Conexion ssh")
        if line['server'] == "HTTP":
            print("Conexion http")
        else:
            print("Conexion desconocida")
        
