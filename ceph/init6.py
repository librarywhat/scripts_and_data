import os
os.system("pip3 install -U paramiko")

import json
import time
from io import StringIO

import paramiko

import signal
from contextlib import contextmanager

class TimeoutException(Exception):
    pass

@contextmanager
def time_limit(seconds):
    def signal_handler(signum, frame):
        raise TimeoutException("Timed out!")
    signal.signal(signal.SIGALRM, signal_handler)
    signal.alarm(seconds)
    try:
        yield
    finally:
        signal.alarm(0)
  
class SSHManager:
    def __init__(self, params: dict):
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(
            hostname=params["ipv4_address"],
            port=22,
            username=params["username"],
            password=params["password"],
        )
        self.ssh = ssh
        self.name = params["name"]
        self.ip: str = params["internal_address"]

    def execute(self, command, timeout=30):
        command = f"{command}"
        result = ""
        error = ""
        exit_code = -1
        
        try:
            with time_limit(timeout):
                stdin, stdout, stderr = self.ssh.exec_command(command)
                print(f"|{self.name}|, executed command: {command}")
                result = "\n".join(stdout.readlines())
    
                try:
                    error_output = "\n".join(stderr.readlines())
                    if error_output:
                        error = "error: " + error_output
                except:
                    pass
    
                exit_code = stdout.channel.recv_exit_status()
    
                print(
                    f"|{self.name}|, {result[:100]} , code: {exit_code}, {error}"
                )
                
        except TimeoutException:
            print(f"|{self.name}|, TIMEOUT after {timeout} seconds for command: {command}")
            result = "TIMEOUT"
            error = f"Command timed out after {timeout} seconds"
            
        except Exception as e:
            print(f"|{self.name}|, Error: {str(e)}")
            result = "ERROR"
            error = f"Exception: {str(e)}"
        
        return result

    def execute_with_code(self, command):
        command = f'sudo su -c "{command}"'
        stdin, stdout, stderr = self.ssh.exec_command(command)
        result = "\n".join(stdout.readlines())
        print(result)
        print(f"|{self.name}|, executed command: {command}")
        result = str(stdout.channel.recv_exit_status())
        print(f"|{self.name}|, {result}")
        return result

    def disconnect(self):
        self.ssh.close()

class RootSSHManager(SSHManager):
    def __init__(self, params: dict):
        k = paramiko.RSAKey.from_private_key_file(".ssh/id_rsa")

        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(
            hostname=params["ipv4_address"],
            port=22,
            username="root",
            pkey=k,
        )
        self.ssh = ssh
        self.name = params["name"]
        self.ip: str = params["internal_address"]

    def execute_with_code(self, command):
        stdin, stdout, stderr = self.ssh.exec_command(command)
        result = "\n".join(stdout.readlines())
        print(result)
        print(f"|{self.name}|, executed command: {command}")
        result = str(stdout.channel.recv_exit_status())
        print(f"|{self.name}|, {result}")
        return result


def worker(server_name: str):
    with open("/root/resource.json", "r", encoding="utf8") as f:
        resources: dict = json.loads(f.read())

    servers = {}

    with open("/root/.ssh/id_rsa.pub", "r", encoding="utf8") as f:
        pub_key = f.read()

    for i in range(1, 6):
        server_params = resources[f"dev9{i}"]
        servers[i] = SSHManager(server_params)
        command = 'sudo sed -i "s/^#PubkeyAuthentication.*/PubkeyAuthentication yes/" /etc/ssh/sshd_config'
        servers[i].execute(command)



        command =f"sudo su -c 'echo \"{pub_key}\" >> /root/.ssh/authorized_keys'"
        servers[i].execute(command)

        servers[i].disconnect()

        servers[i] = RootSSHManager(server_params)

    command = (
        f'hostnamectl set-hostname ceph1 ; echo -e "{servers[1].ip} ceph1.local ceph1\n'
        f"{servers[2].ip} ceph2.local ceph2\n{servers[3].ip} ceph3.local ceph3\n"
        f'{servers[5].ip} client.local client" >> /etc/hosts ; echo "{pub_key}" '
        f'>> /root/.ssh/authorized_keys ; if [[ ! -d "/etc/ceph" ]]; then sudo mkdir -p /etc/ceph;fi ; '
        f'/usr/local/bin/cephadm bootstrap --mon-ip {servers[1].ip} --initial-dashboard-user itclife '
        f"--initial-dashboard-password itclife --dashboard-password-noupdate "

    )
    servers[1].execute(command)


    command = (
        f'hostnamectl set-hostname ceph2 ; echo -e "{servers[1].ip} ceph1.local ceph1\n'
        f"{servers[2].ip} ceph2.local ceph2\n{servers[3].ip} ceph3.local ceph3\n"
        f'{servers[5].ip} client.local client" >> /etc/hosts ; echo "{pub_key}" '
        f">> /root/.ssh/authorized_keys"
    )
    servers[2].execute(command)

    command = (
        f'hostnamectl set-hostname ceph3 ; echo -e "{servers[1].ip} ceph1.local ceph1\n'
        f"{servers[2].ip} ceph2.local ceph2\n{servers[3].ip} ceph3.local ceph3\n"
        f'{servers[5].ip} client.local client" >> /etc/hosts ; echo "{pub_key}" '
        f">> /root/.ssh/authorized_keys"
    )
    servers[3].execute(command)

    command = (
        f'hostnamectl set-hostname ceph4 ; echo -e "{servers[1].ip} ceph1.local ceph1\n'
        f"{servers[2].ip} ceph2.local ceph2\n{servers[3].ip} ceph3.local ceph3\n"
        f'{servers[5].ip} client.local client" >> /etc/hosts ; echo "{pub_key}" '
        f">> /root/.ssh/authorized_keys"
    )
    servers[4].execute(command)

    command = (
        f'hostnamectl set-hostname client ; echo -e "{servers[1].ip} ceph1.local ceph1\n'
        f"{servers[2].ip} ceph2.local ceph2\n{servers[3].ip} ceph3.local ceph3\n"
        f'{servers[5].ip} client.local client" >> /etc/hosts  ; echo "{pub_key}" >> '
        f"/root/.ssh/authorized_keys"
    )
    servers[5].execute(command)

    command = "cat /etc/ceph/ceph.pub"
    ssh_key_help = servers[1].execute(command)

    command = f'echo """{ssh_key_help}""" >> /root/.ssh/authorized_keys'
    for i in [1,2,3,5]:
        servers[i].execute(command)

    command = f"ceph orch host add ceph2 {servers[2].ip}"
    servers[1].execute(command)

    command = f"ceph orch host add ceph3 {servers[3].ip}"
    servers[1].execute(command)

    commands = (
        "ceph orch host label add ceph1 mon",
        "ceph orch host label add ceph2 mon",
        "ceph orch host label add ceph3 mon",
        "ceph orch host label add ceph1 mgr",
        "ceph orch host label add ceph2 mgr",
        "ceph orch host label add ceph3 mgr",
        f'ceph config set mon public_network {servers[1].ip.rsplit(".", 1)[0]}.0/24 ',
        'ceph orch apply mon "ceph1,ceph2,ceph3"',
        'ceph orch apply mgr "ceph1,ceph2,ceph3"',
    )
    for command in commands:
        servers[1].execute(command)

    commands = (
        "ceph orch daemon add osd ceph1:/dev/vdb",
        "ceph orch daemon add osd ceph2:/dev/vdb",
        "ceph orch daemon add osd ceph3:/dev/vdb",
    )

    for command in commands:
        attempt = 1
        while attempt < 5:
            code = servers[1].execute_with_code(command)
            if "0" in str(code):
                break
            attempt += 1

    command = "ceph osd pool create rbd 32 32 ; ceph osd pool set rbd size 3 ; ceph osd pool set rbd min_size 3 ; ceph osd pool application enable rbd rbd; rbd pool init -p rbd"
    servers[1].execute(command)

    command = "rbd create disk01 --size 10M --pool rbd ; ceph config generate-minimal-conf > ceph.conf;"
    servers[1].execute(command)

    command = "cat /etc/ceph/ceph.conf"
    ssh_key_help = servers[1].execute(command)

    command = f'echo """{ssh_key_help}""" >> /etc/ceph/ceph.conf'
    servers[5].execute(command)


    command = "ceph auth get-or-create client.rbd mon 'allow r' osd 'allow class-read object_prefix rbd_children, allow rwx pool=rbd' "
    servers[1].execute(command)

    command = "ceph auth get-or-create client.rbd"
    ssh_key_help = servers[1].execute(command)

    command = f'echo """{ssh_key_help}""" >> /etc/ceph/keyring'
    servers[5].execute(command)

    command = "rbd map --image disk01 --name client.rbd; mkfs.xfs /dev/rbd0 -L cephbd; mkdir /database; mount /dev/rbd0 /database"
    servers[5].execute(command)

    time.sleep(10)

    command="sudo hdparm -Y /dev/vda2"
    servers[3].execute(command)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Process a single string argument.")

    parser.add_argument("server_name", type=str, help="The input string to process")

    args = parser.parse_args()
    time.sleep(60)
    print(f"Input string received: {args.server_name}")
    st = time.monotonic()
    worker(args.server_name)
    with open('file.txt','w') as f:
        f.write(str(time.monotonic()-st))
