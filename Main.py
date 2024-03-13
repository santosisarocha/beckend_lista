import http.server
import socketserver
import os
from http.server import SimpleHTTPRequestHandler
from urllib.parse import parse_qs, urlparse
import hashlib
import content

import content as content

from database import conectar

conexao = conectar()


class MyHandler(SimpleHTTPRequestHandler):
    def list_directory(self, path):
        try:
            f = open(os.path.join(path, 'text.html'), 'r')
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            self.wfile.write(f.read().encode('utf-8'))
            f.close()
            return None
        except FileNotFoundError:
            pass
        return super().list_directory(path)

    def do_GET(self):
        if self.path == '/login':
            try:
                with open(os.path.join(os.getcwd(), 'login.html'), 'r') as login_file:
                    content = login_file.read()
                self.send_response(200)
                self.send_header("Location", "/turmas")
                self.end_headers()
                self.wfile.write(content.encode('utf-8'))
            except FileNotFoundError:
                self.send_error(404, "File not found")

        elif self.path == '/login_failed':
            self.send_response(200)
            self.send_header("Content-type", "text/html; charset=utf-8")
            self.end_headers()

            with open(os.path.join(os.getcwd(), 'login.html'), 'r', encoding='utf-8') as login_file:
                content = login_file.read()

            mensagem = "Login e/ou senha incorreta. Tente novamente."
            content = content.replace('<!-- Mensagem de erro aqui -->',
                                      f'<div class="error-message">{mensagem}</div>')
            self.wfile.write(content.encode('utf-8'))

        elif self.path.startswith('/cadastro'):
            query_params = parse_qs(urlparse(self.path).query)
            login = query_params.get('login', [''])[0]
            senha = query_params.get('senha', [''])[0]

            welcome_message = f"Olá {login}, bem-vindo! Me parece que você é novo por aqui! Complete seu cadastro."

            self.send_response(200)
            self.send_header("Content-type", "text/html; charset=utf-8")
            self.end_headers()

            with open(os.path.join(os.getcwd(), 'cadastro.html'), 'r', encoding='utf-8') as cadastro_file:
                content = cadastro_file.read()

            content = content.replace('{login}', login)
            content = content.replace('{senha}', senha)
            content = content.replace('{welcome_message}', welcome_message)

            self.wfile.write(content.encode('utf-8'))

            return


        elif self.path.startswith('/turmas'):

            query_params = parse_qs(urlparse(self.path).query)
            codigo = query_params.get('codigo', [''])[0]
            descricao = query_params.get('descricao', [''])[0]

            self.send_response(200)
            self.send_header("Content-type", "text/html; charset=utf-8")
            self.end_headers()

            with open(os.path.join(os.getcwd(), 'cadastro_turmas.html'), 'r', encoding='utf-8') as cadastro_turmas_file:
                content = cadastro_turmas_file.read()
            content = content.replace('{codigo}', codigo)
            content = content.replace('{descricao}', descricao)

            self.wfile.write(content.encode('utf-8'))
            return

        elif self.path.startswith('/turma_professor'):

            query_params = parse_qs(urlparse(self.path).query)
            codigo = query_params.get('codigo', [''])[0]
            codigo1 = query_params.get('codigo1', [''])[0]

            self.send_response(200)
            self.send_header("Content-type", "text/html; charset=utf-8")
            self.end_headers()

            with open(os.path.join(os.getcwd(), 'turma_login.html'), 'r', encoding='utf-8') as turma_login_file:
                content = turma_login_file.read()
            content = content.replace('{codigo}', codigo)
            content = content.replace('{codigo1}', codigo1)

            self.wfile.write(content.encode('utf-8'))
            return
        elif self.path.startswith('/atividades'):
            query_params = parse_qs(urlparse(self.path).query)
            codigo1 = query_params.get('codigo1', [''])[0]
            descricao1 = query_params.get('descricao1', [''])[0]

            self.send_response(200)
            self.send_header("Content-type", "text/html; charset=utf-8")
            self.end_headers()

            with open(os.path.join(os.getcwd(), 'cadastro_atividades.html'), 'r', encoding='utf-8') as cadastro_atividades_file:
                content = cadastro_atividades_file.read()
            content = content.replace('{codigo1}', codigo1)
            content = content.replace('{descricao1}', descricao1)


            self.wfile.write(content.encode('utf-8'))
            return

        elif self.path.startswith('/home'):
            query_params = parse_qs(urlparse(self.path).query)
            id_professor = query_params.get('id_professor', [''])[0]
            turma = query_params.get('turma', [''])[0]
            atividade = query_params.get('atividade', [''])[0]


            self.send_response(200)
            self.send_header("Content-type", "text/html; charset=utf-8")
            self.end_headers()

            with open(os.path.join(os.getcwd(), 'home.html'), 'r', encoding='utf-8') as home_file:
                content = home_file.read()
            content = content.replace(f'{id_professor}', id_professor)
            content = content.replace(f'{turma}', turma)
            content = content.replace(f'{atividade}', atividade)


            self.wfile.write(content.encode('utf-8'))
            return


        else:
            super().do_GET()

    def usuario_existente(self, login, senha):
        cursor = conexao.cursor()
        cursor.execute("SELECT senha FROM dados_login WHERE login = %s" , (login,) )
        resultado = cursor.fetchone()
        cursor.close()
        if resultado:
            senha_hash = hashlib.sha256(senha.encode('utf-8')).hexdigest()
            return senha_hash == resultado[0]
        return False

    def adicionar_usuario(self, login, senha, nome):
        cursor = conexao.cursor()
        senha_hash = hashlib.sha256(senha.encode('utf-8')).hexdigest()
        cursor.execute("INSERT INTO dados_login (login, senha, nome) VALUES (%s, %s, %s)", (login, senha_hash, nome))
        conexao.commit()
        cursor.close()


    def remover_ultima_linha(self, arquivo):

        print("A última linha será excluida.")
        with open(arquivo, 'r', encoding='utf-8') as file:
            lines = file.readlines()
        with open(arquivo, 'w', encoding='utf-8') as file:
            file.writelines(lines[:-1])

    def extrair_dados_login(self, form_data):
        with open('dados_registro.txt', 'r', encoding='utf-8') as file:
            lines = file.readlines()
        if lines:
            ultimo_email = lines[-1].split(';')[0]
            return ultimo_email
        else:
            return form_data.get('email', [''])[0]

    def extrair_dados_turma(self, form_data):
        with open('dados_registroturmas.txt', 'r', encoding='utf-8') as file:
            lines = file.readlines()
        if lines:
            ultimo_codigo = lines[-1].split(';')[0]
            return ultimo_codigo
        else:
            return form_data.get('codigo', [''])[0]

    def do_POST(self):
        if self.path == "/enviar_login":
            content_length = int(self.headers['Content-Length'])
            body = self.rfile.read(content_length).decode("utf-8")
            form_data = parse_qs(body, keep_blank_values=True)

            print("Dados do Formulário:")
            print("Email:", form_data.get('email', [''])[0])
            print("Senha:", form_data.get('senha', [''])[0])

            login = form_data.get('email', [''])[0]
            senha = form_data.get('senha', [''])[0]

            if self.usuario_existente(login, senha):
                self.send_response(200)

                self.send_header("Content-type", "text/html; charset=utf-8")
                self.end_headers()
                mensagem = f"Usuario {login} Logado com sucesso"
                self.wfile.write(mensagem.encode('utf-8'))
                cursor = conexao.cursor()
                cursor.execute("INSERT INTO turmas (registro) VALUES (%s)", (login,))
                with open('dados_registro.txt', 'a', encoding='utf-8') as file:
                    file.write(f"{login};{senha}\n")


                conexao.commit()

                cursor.close()

            else:

                if any(line.startswith(f"{login};") for line in open('dados_login.txt', 'r', encoding='utf-8')):
                    self.send_response(302)
                    self.send_header('Location', '/login_failed')
                    self.end_headers()
                    return
                else:
                    self.adicionar_usuario(login, senha, nome='None')

                self.send_response(302)
                self.send_header('Location', '/cadastro?login={login}&senha={senha}')
                self.end_headers()

                return

        elif self.path.startswith('/confirmar_cadastro'):

            content_length = int(self.headers['Content-Length'])
            body = self.rfile.read(content_length).decode('utf-8')
            form_data = parse_qs(body, keep_blank_values=True)

            login = form_data.get('email', [''])[0]
            senha = form_data.get('senha', [''])[0]
            nome = form_data.get('nome', [''])[0]

            self.adicionar_usuario(login, senha, nome)


            with open(os.path.join(os.getcwd(), 'msg_sucesso.html'), 'rb') as file:
                content = file.read().decode('utf-8')

            with open('dados_registro.txt', 'a', encoding='utf-8') as file:
                file.write(f"{login};{senha}\n")

            content = content.replace('{login}', login)
            content = content.replace('{nome}', nome)

            self.remover_ultima_linha('registro')
            self.send_response(200)
            self.send_header('Location', '/turmas')
            self.end_headers()
            self.wfile.write("Registro recebido!".encode('utf-8'))



        elif self.path.startswith('/cad_turma'):
            content_length = int(self.headers['Content-Length'])
            body = self.rfile.read(content_length).decode('utf-8')
            forms_data = parse_qs(body, keep_blank_values=True)


            codigo = forms_data.get('codigo', [''])[0]
            descricao_turma = forms_data.get('descricao', [''])[0]
            email = self.extrair_dados_login(forms_data)

            cursor = conexao.cursor()
            cursor.execute("INSERT INTO turmas (descricao) VALUES (%s)", (descricao_turma,))

            conexao.commit()

            cursor.close()

            print("nome: " + codigo)
            print("nome: " + descricao_turma)




            self.send_response(302)
            self.send_header('Location', '/atividades')
            self.end_headers()


        elif self.path.startswith('/login_turma'):
            content_length = int(self.headers['Content-Length'])
            body = self.rfile.read(content_length).decode('utf-8')
            forms_data = parse_qs(body, keep_blank_values=True)


            codigo = forms_data.get('codigo', [''])[0]
            codigo1 = forms_data.get('codigo1', [''])[0]


            cursor = conexao.cursor()
            cursor.execute("INSERT INTO turmas_professor (id_professor, id_turma) VALUES (%s, %s)", (codigo,codigo1))

            conexao.commit()

            cursor.close()

            print("id: " + codigo)
            print("id: " + codigo1)


            self.send_response(302)
            self.send_header('Location', '/atividades')
            self.end_headers()

        elif self.path.startswith('/home'):
            content_length = int(self.headers['Content-Length'])
            body = self.rfile.read(content_length).decode('utf-8')
            forms_data = parse_qs(body, keep_blank_values=True)

            id_professor = forms_data.get('id_professor', [''])[0]

            cursor = conexao.cursor()
            cursor.execute(
                "SELECT turmas.descricao FROM turmas_professor INNER JOIN turmas ON turmas_professor.id_turma = turmas.id_turma WHERE id_professor = %s",
                [id_professor])

            results = cursor.fetchall()
            turma_nome = ', '.join(row[0] for row in results) if results else 'Nenhuma turma encontrada'

            cursor.close()

            self.send_response(200)
            self.send_header("Content-type", "text/html; charset=utf-8")
            self.end_headers()

            with open(os.path.join(os.getcwd(), 'home.html'), 'r', encoding='utf-8') as home_file:
                content = home_file.read()

            content = content.replace('{id_professor}', id_professor)
            content = content.replace('{turma_nome}', turma_nome)

            self.wfile.write(content.encode('utf-8'))

        elif self.path.startswith('/cad_atividades'):
            content_length = int(self.headers['Content-Length'])
            body = self.rfile.read(content_length).decode('utf-8')
            forms_data = parse_qs(body, keep_blank_values=True)

            codigo1 = forms_data.get('codigo1', [''])[0]
            descricao1 = forms_data.get('descricao1', [''])[0]
            codigo = self.extrair_dados_turma(forms_data)

            cursor = conexao.cursor()
            cursor.execute("INSERT INTO atividades (descricao) VALUES (%s)", (descricao1,))

            conexao.commit()

            cursor.close()

            print("codigo: " + codigo1)
            print("deescricao: " + descricao1)
            with open('dados_atividade.txt', 'a', encoding='utf-8') as file:
                file.write(f"{codigo1};{descricao1}\n")
            with open('turma_atividade.txt', 'a', encoding='utf-8') as file:
                file.write(f"{codigo};{codigo1}\n")

            cursor = conexao.cursor()
            cursor.execute("SELECT login FROM atividade_turma WHERE login = %s", (codigo, codigo1))
            resultado = cursor.fetchone()

            self.send_response(302)
            self.send_header('Location', '/cad_turma_success.html')
            self.end_headers()





        else:
            super(MyHandler, self).do_POST()



endereco_ip = "0.0.0.0"  # pode escolher qualquer endereço de ip e colocar ali nas aspas
porta = 8000

with socketserver.TCPServer((endereco_ip, porta), MyHandler) as httpd:
    print(f"Servidor iniciando na porta {endereco_ip}:{porta}")
    httpd.serve_forever()
