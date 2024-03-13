import pandas as pd
usuario = input("digite a usuario:")
senha = input("digite a senha:")


df = pd.DataFrame ({
    "usuario":[usuario],
    "senha":[senha]
})
df.to_csv("notas.txt",index = False)

df = pd.read_csv("notas.txt")
print(df)