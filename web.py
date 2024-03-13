import http.server
import socketserver
import os
from http.server import SimpleHTTPRequestHandler
from urllib.parse import parse_qs, urlparse
import hashlib


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


        else:
            super().do_GET()

    def usuario_existente(self, login, senha):
        with open('dados_login.txt', 'r', encoding='utf-8') as file:
            for line in file:
                if line.strip():
                    stored_login, stored_senha_hash, stored_nome = line.strip().split(';')
                    if login == stored_login:
                        print("Login informado foi localizado.")
                        print("senha: " + senha)
                        print(" senha_armazenada: " + senha)
                        senha_hash = hashlib.sha256(senha.encode('utf-8')).hexdigest()
                        return senha_hash == stored_senha_hash
        return False

    def adicionar_usuario(self, login, senha, nome):
        senha_hash = hashlib.sha256(senha.encode('utf-8')).hexdigest()
        with open('dados_login.txt', 'a', encoding='utf-8') as file:
            file.write(f"{login};{senha_hash}; {nome}\n")



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
            form_data = parse_qs(body)

            print("Dados do Formulário:")
            print("Email:", form_data.get('email', [''])[0])
            print("Senha:", form_data.get('senha', [''])[0])

            login = form_data.get('email', [''])[0]
            senha = form_data.get('senha', [''])[0]

            if self.usuario_existente(login, senha):
                with open('dados_registro.txt', 'a', encoding='utf-8') as file:
                    file.write(f"{login};{senha}\n")
                self.send_response(302)
                self.send_header('Location', '/turmas')
                self.end_headers()

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

            senha_hash = hashlib.sha256(senha.encode('utf-8')).hexdigest()

            print("nome: " + nome)

            if self.usuario_existente(login, senha):
                with open('dados_login.txt', 'r', encoding='utf-8') as file:
                    lines = file.readlines()

                with open('dados_login.txt', 'w', encoding='utf-8')as file:
                    for line in lines:
                        stored_login, stored_senha, stored_nome = line.strip().split(';')
                        if login == stored_login and senha_hash == stored_senha:
                            line = f"{login};{senha_hash};{nome}\n"
                        file.write(line)
                if self.usuario_existente(login, senha):
                    with open('dados_registro.txt', 'a', encoding='utf-8') as file:
                        file.write(f"{login};{senha}\n")



                self.send_response(302)
                self.send_header('Location', '/turmas')
                self.end_headers()
                self.wfile.write("Registro recebido!".encode('utf-8'))


            else:
                self.remover_ultima_linha('dados_login.txt')
                self.send_response(302)
                self.send_header('Content-type', 'text/html; charset=utf-8')
                self.end_headers()
                self.wfile.write("Senha não confere. Retome e tente novamente.".encode('utf-8'))

        elif self.path.startswith('/cad_turma'):
            content_length = int(self.headers['Content-Length'])
            body = self.rfile.read(content_length).decode('utf-8')
            forms_data = parse_qs(body, keep_blank_values=True)
            codigo = forms_data.get('codigo', [''])[0]
            descricao = forms_data.get('descricao', [''])[0]
            email = self.extrair_dados_login(forms_data)
            print("nome: " + codigo)
            print("nome: " + descricao)
            with open('dados_login_turma.txt', 'a', encoding='utf-8') as file:
                file.write(f"{codigo};{codigo}\n")
            with open('login_turma.txt', 'a', encoding='utf-8') as file:
                file.write(f"{codigo};{email}\n")
            with open('dados_registroturmas.txt', 'a', encoding='utf-8') as file:
                file.write(f"{codigo}")

            self.send_response(302)
            self.send_header('Location', '/atividades')
            self.end_headers()

        elif self.path.startswith('/cad_atividades'):
            content_length = int(self.headers['Content-Length'])
            body = self.rfile.read(content_length).decode('utf-8')
            forms_data = parse_qs(body, keep_blank_values=True)
            codigo1 = forms_data.get('codigo1', [''])[0]
            descricao1 = forms_data.get('descricao1', [''])[0]
            codigo = self.extrair_dados_turma(forms_data)
            print("codigo: " + codigo1)
            print("deescricao: " + descricao1)
            with open('dados_atividade.txt', 'a', encoding='utf-8') as file:
                file.write(f"{codigo1};{descricao1}\n")
            with open('turma_atividade.txt', 'a', encoding='utf-8') as file:
                file.write(f"{codigo};{codigo1}\n")

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
