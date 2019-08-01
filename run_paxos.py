import docker


dockerClient = docker.from_env()


# Setup the master container
master_container = dockerClient.containers.run(image= "pmaster", 
            detach=True,
            ports={7087: None})

master_container.reload()

master_ip = master_container.attrs['NetworkSettings']['Networks']['bridge']['IPAddress']
master_port = master_container.attrs['NetworkSettings']['Ports']['7087/tcp'][0]['HostPort']

print("master_ip ", master_ip)
print("master_port", master_port)

N = 3
#Setup the server containers 
server_containers = [] 
server_ips = []
peer_ports = []
manager_ports = []

for i in range(N): 
    cont = dockerClient.containers.run(image='pserver',
    detach = True, 
    ports={7070:None, 8070:None}, 
    tty = True, 
    command =  'sh', 
    volumes = {'/home/xusheng/codes/epaxos/logs': {'bind': '/logs', 'mode':'rw'}})

    server_containers.append(cont)

    cont.reload()
    ip = cont.attrs['NetworkSettings']['Networks']['bridge']['IPAddress']   
    server_ips.append(ip)

    peer_port = cont.attrs['NetworkSettings']['Ports']['7070/tcp'][0]['HostPort']
    manager_port = cont.attrs['NetworkSettings']['Ports']['8070/tcp'][0]['HostPort']
     
    peer_ports.append(peer_port)
    manager_ports.append(manager_port)
    
    print ("started server container %d, ip = %s, peer_port = %s, manager_ports = %s" % (i, ip, peer_port, manager_port)) 


    command = 'sh -c \'/app/bin/paxos-server -maddr %s -mport %s -addr %s -peerEPort %s -managerEPort %s >/logs/server%d.log 2>&1\'' % (master_ip, master_port, ip, peer_port, manager_port, i)
    print("Exec command is [%s]" % command)
    ret = cont.exec_run(cmd = command,
        stdout = False, 
        stderr = False, 
        detach = True) 
    print(ret)

# master_container.kill() 