## 📖 Descrição
Este projeto se trata de um pequeno fluxo de extração, transformação e carga (ETL) que extrai e categoriza dados do conhecido website
de tecnologia Hacker News e carrega os dados em um banco de dados MongoDB.

### 💻 Tecnologias
- Python
- Pandas
- BeautifulSoup
- MongoDB

### ⚙️ O que o script faz
O script realiza um scraping nas front page e news page do website HackerNews, transforma os dados organizando-os em top 10 threads por
quantidade de votos, top 10 threads por quantidade de comentários e top 10 threads mais recentes, sempre mostrando também o título
e os primeiros 5 comentários de cada thread, após a transformação, carrega os dados em um banco MongoDB.

### 🚀 Como rodar o script
Clone o projeto em uma pasta de sua escolha e rode docker compose up na pasta raiz do projeto. Passo a passo mais detalhado a seguir:
Abra um terminal em alguma pasta de sua escolha e execute os seguintes comandos:

git clone https://github.com/Matheuszin502/HackerNewsBot.git

cd HackerNewsBot

docker compose up -d

Agora basta esperar o banco de dados inciar e o processo de web scraping terminar e acessar a GUI do MongoDB em http://localhost:8081/
para poder ver os dados carregados. O username e senha estão como admin e password.

Exemplos de como se parece no final:

<img width="1168" height="682" alt="Captura de tela 2026-05-08 184603" src="https://github.com/user-attachments/assets/640dbce5-713e-4e32-b6a6-5a7cf3d1a63e" />

<img width="1197" height="593" alt="Captura de tela 2026-05-08 184816" src="https://github.com/user-attachments/assets/3e2c987d-599d-4d49-9dc1-1ccca688b1a8" />

Para acompanhar o tempo que falta para é uma alternativa acompanhar os logs, para isto faça o passo a passo:

Execute o comando: docker container ls, e copie o id do container hackernewsbot-pipeline

Agora execute o comando: docker logs {id do container}
