import docker
import time



N = 3 # number of replicas
n_reqs = 6000 # number of requests
parallel_instances = 3 # number of on-going reqs for client (i.e., similar to number of connections, but bound to same TCP connection)
leader_only = False  


latencies = [[0, 100, 150],
             [100, 0, 200],
             [150, 200, 0]]


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
    
    print ("[started server] container %d, ip = %s, peer_port = %s, manager_ports = %s" % (i, ip, peer_port, manager_port)) 

tc_commands = []

for i in range(N):

    tc_cmd = ''
    # Clear TC state
    tc_cmd = tc_cmd + 'tc qdisc del dev eth0 root ; '
    # Add the top level prior qdisc, with N bands, 0 (1:1) for default, N for N peers (for simplicity, also add to itself)
    tc_cmd = tc_cmd + 'tc qdisc add dev eth0 root handle 1: prio bands %d priomap 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 ;' % (N+1)

    for j in range (N):
        tc_cmd = tc_cmd + 'tc qdisc add dev eth0 parent 1:%d handle %d: netem delay %dms ; ' % (j+2, j+2, latencies[i][j])

    for j in range (N):
        tc_cmd = tc_cmd + 'tc filter add dev eth0 parent 1: protocol ip pref %d handle ::%d u32 match ip dst %s flowid 1:%d' % ( (j+1) * 10, (j+1) * 10, server_ips[j], j+2)

    print ('TC CMD for server %d: [%s]' % (i, tc_cmd))

    tc_commands.append(tc_cmd)


for i in range(N):

    # tc_command = 'tc qdisc add dev eth0 root netem delay 100ms'
    ret = server_containers[i].exec_run(cmd = tc_commands[i])
    print('TC result:', ret)


    command = 'sh -c \'/app/bin/paxos-server -maddr %s -mport %s -addr %s -peerEPort %s -managerEPort %s -m >/logs/server%d.log 2>&1\'' % (master_ip, 7087, server_ips[i], 7070, 8070, i)
    print("Exec command is [%s]" % command)
    ret = server_containers[i].exec_run(cmd = command,
        stdout = False, 
        stderr = False, 
        detach = True) 

time.sleep(10)




if leader_only :
    client_cmd = '/app/bin/paxos-client -maddr %s -mport %s -r %d -q %d' % (master_ip, 7087, n_reqs//parallel_instances, n_reqs)
else:
    client_cmd = '/app/bin/paxos-client -maddr %s -mport %s -e -r %d -q %d' % (master_ip, 7087, n_reqs//parallel_instances, n_reqs)

client = dockerClient.containers.run(image='pclient', 
    detach = True,
    command = client_cmd
    )
client.reload()
print(client.id)
print("started client")

# master_container.kill() 