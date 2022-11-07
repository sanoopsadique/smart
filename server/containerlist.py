import os

container = [1,2,3]
containerlist = []

for item in container:
    containerlist.append(os.popen("docker run -dt sanoopsadique/al-py:latest").read())

print(containerlist)

for item in containerlist:
    os.system("docker stop "+item)
    os.system("docker rm "+item)
