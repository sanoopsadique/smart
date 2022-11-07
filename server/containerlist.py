import os

container = [1,2,3]
containerlist = []

for item in container:
    containerlist.append(os.popen("docker run -dtp sanoopsadique/al-py:latest").read())

print(containerlist)