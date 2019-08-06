import docker
import time

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
print("master container id", master_container.id)
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
    cap_add = ['NET_ADMIN'],
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

    tc_command = 'tc qdisc add dev eth0 root netem delay 100ms'
    ret = cont.exec_run(cmd = tc_command)
    print(ret)


    command = 'sh -c \'/app/bin/paxos-server -maddr %s -mport %s -addr %s -peerEPort %s -managerEPort %s -m true >/logs/server%d.log 2>&1\'' % (master_ip, 7087, ip, 7070, 8070, i)
    print("Exec command is [%s]" % command)
    ret = cont.exec_run(cmd = command,
        stdout = False, 
        stderr = False, 
        detach = True) 

time.sleep(10)

client = dockerClient.containers.run(image='pclient', 
    detach = True, 
    command= '/app/bin/paxos-client -maddr %s -mport %s -e true' % (master_ip, 7087))
client.reload()
print(client.id)
print("started client")

# master_container.kill() 