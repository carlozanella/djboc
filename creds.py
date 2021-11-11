import sys,json,os,getpass

if os.path.exists("creds.json"):
    print("creds.json already exists. Delete and run again!")
    sys.exit(1)

j = {'email': input("Email: "),
     'password' : getpass.getpass(prompt="Password: ")}
with open("creds.json","w") as f:
    f.write(json.dumps(j,indent=1))
sys.exit(0)
