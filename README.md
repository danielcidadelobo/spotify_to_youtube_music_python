Conversor de Playlists do Spotify para YouTube Music

Este projeto permite transferir playlists do Spotify para o YouTube Music automaticamente.

## Requisitos

Antes de utilizar o programa, certifique-se de que tem os seguintes itens instalados no seu sistema:

- Python 3.8 ou superior** ([Download](https://www.python.org/downloads/))
- Pip (normalmente já vem instalado com o Python)
- Git ([Download](https://git-scm.com/downloads))

Instalação

1. Clone este repositório:
   ```bash
   git clone git@github.com:SEU_USUARIO/spotify_to_youtube_music_python.git
   cd spotify_to_youtube_music_python
   ```

2. Instale as dependências necessárias:
   ```bash
   pip install -r requirements.txt
   ```

## 🔑 Obter Credenciais do Spotify e YouTube

### 1. **Obter Credenciais do Spotify**

1. Aceda ao [Painel de Desenvolvedor do Spotify](https://developer.spotify.com/dashboard/).
2. Crie uma nova aplicação e obtenha o **Client ID** e o **Client Secret**.
3. Insira estes dados quando o programa pedir na primeira execução do programa.

### 2. **Obter Credenciais da API do YouTube**

1. Aceda ao [Google Cloud Console](https://console.cloud.google.com/).
2. Ative a API **YouTube Data v3**.
3. Crie credenciais do tipo "OAuth 2.0" e descarregue o ficheiro `client_secret.json`.
4. Coloque esse ficheiro na pasta do projeto.

## ▶️ Como Utilizar

1. Execute o programa.
2. O programa pedirá para inserir a **URL da playlist do Spotify**.
3. Escolha se deseja criar uma nova playlist no YouTube ou adicionar músicas a uma existente.
4. O programa fará a transferência automática das músicas.

⚠ **Nota:** A API do Google tem um limite de utilização diário. Se ultrapassar o limite, terá de aguardar 24 horas para continuar.

## 🛠 Módulos Necessários

O programa usa os seguintes módulos:
- `spotipy` (Para interagir com a API do Spotify)
- `google-auth` e `google-auth-oauthlib` (Para autenticação com a API do YouTube)
- `googleapiclient` (Para enviar requisições à API do YouTube)
- `tqdm` (Para barra de progresso durante a transferência)

Estes módulos são instalados automaticamente ao executar `pip install -r requirements.txt`.

## 📄 Licença

Este projeto está licenciado sob a [Creative Commons Attribution-NoDerivatives 4.0](https://creativecommons.org/licenses/by-nd/4.0/).

