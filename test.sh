set -x
export GOPATH=/home/xusheng/codes/epaxos
go install paxos-master
go install paxos-server 
go install paxos-client
sleep 1
pkill paxos-server 
pkill paxos-client
pkill paxos-master
sleep 1

bin/paxos-master >master.log 2>&1 &
bin/paxos-server -port 7070 >server0.log 2>&1 &
bin/paxos-server -port 7071 >server1.log 2>&1 &
bin/paxos-server -port 7072 >server2.log 2>&1 &
sleep 10
bin/paxos-client >client.log 2>&1
