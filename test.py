import subprocess
f=subprocess.check_output("hostname -I",stderr=subprocess.STDOUT,shell=True)
print(f.decode())
print(f.decode()=="\n")
print(len(f.decode()))
