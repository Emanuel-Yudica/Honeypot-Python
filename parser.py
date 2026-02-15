import json
def parser(q):
    while True:
        line = q.get()
        server=line["server"]
        if server == "SSH":
            filename="ssh_log.json"
            save_to_file(line,filename)
        elif server == "HTTP":
            filename="http_log.json"
            save_to_file(line,filename)
        else:
            print("Conexion desconocida")

def save_to_file(data,filename):
    with open(filename, "a") as f:
        json.dump(data, f)
        f.write("\n")
    
        
