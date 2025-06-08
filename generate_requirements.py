# generate_requirements.py

with open("requirements_locked.txt", "r", encoding="utf-8") as infile:
    lines = infile.readlines()

packages = [line.split("==")[0] for line in lines if "==" in line]

with open("requirements.txt", "w", encoding="utf-8") as outfile:
    outfile.write("\n".join(packages))

print("requirements.txt wurde erstellt.")
