import os

container = [1,2,3]
containerlist = []

for item in container:
    os.popen("docker run -dt --name "+item+" sanoopsadique/al-py:latest")

print(containerlist)

for item in container:
    os.system("docker stop "+item)
    os.system("docker rm "+item)
