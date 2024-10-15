import requests
import pandas as pd
from data.teams import teams
from datetime import datetime

# Definindo a URL da API NBA para estatísticas de jogadores
API_URL_STATS = "https://stats.nba.com/stats/playergamelogs"
API_URL_PLAYER_SEARCH = "https://stats.nba.com/stats/commonallplayers"
API_URL_TEAM_GAMELOGS = "https://stats.nba.com/stats/teamgamelogs"
API_URL_BOXSCORE_SUMMARY = "https://stats.nba.com/stats/boxscoresummaryv2"

# Definir as temporadas fixas
temporadas = ["2024-25", "2023-24"]
header_boxscore_line_score = None

# Função para buscar o ID de um jogador pelo nome
def buscar_id_jogador(nome_jogador):
    headers = {
        "Referer": "https://www.nba.com/",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.121 Safari/537.36"
    }

    params = {
        "IsOnlyCurrentSeason": "0",  # 0 para jogadores de todas as temporadas
        "LeagueID": "00",  # NBA
        "Season": "2024-25" 
    }

    response = requests.get(API_URL_PLAYER_SEARCH, headers=headers, params=params)

    if response.status_code == 200:
        data = response.json()
        jogadores = data['resultSets'][0]['rowSet']

        # Procurar jogador pelo nome (ou parte dele)
        resultados = [jogador for jogador in jogadores if nome_jogador.lower() in jogador[1].lower()]

        if resultados:
            print('\n')
            print("Jogadores encontrados:")
            for i, jogador in enumerate(resultados):
                print(f"{i + 1}. {jogador[1]} (ID: {jogador[0]})")
            
            # Permitir que o usuário selecione o jogador correto
            while True:
                try:
                    escolha = int(input("Escolha o número do jogador: ")) - 1
                    if 0 <= escolha < len(resultados):
                        jogador_escolhido = resultados[escolha]
                        return jogador_escolhido[0]  # ID do jogador
                    else:
                        print("Número inválido. Tente novamente.")
                except ValueError:
                    print("Entrada inválida. Por favor, insira um número.")
        else:
            print("Jogador não encontrado.")
            return None
    else:
        print(f"Erro {response.status_code} na requisição de jogadores.")
        return None

# Função para buscar estatísticas do jogador
def buscar_estatisticas_jogador(player_id):
    headerRequest = {
        "Referer": "https://www.nba.com/",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.121 Safari/537.36"
    }

    stats = []
    
    for temporada in temporadas:
        for season_type in ["Pre Season", "Regular Season", "Playoffs"]:
            params = {
                "PlayerID": player_id, 
                "Season": temporada, 
                "SeasonType": season_type
            }
            response = requests.get(API_URL_STATS, headers=headerRequest, params=params)

            if response.status_code == 200:
                stats = stats + response.json()['resultSets'][0]['rowSet']
                headers = response.json()['resultSets'][0]['headers']
            else:
                print(f"Erro ao buscar estatísticas do jogador para {temporada} {season_type}.")
                return None

    resultado_agrupado = {
        'resultSets': [{
            'headers': headers,
            'rowSet': stats
        }]
    }

    return resultado_agrupado

def exportar_para_excel(dados, nome_arquivo, qtd_registros=10):
    print('Por favor aguarde... exportando estatísticas...')

    colunas = [
        'GAME_DATE', 'PTS', 'REB', 'AST', 'FGA', 'FGM', 'FG3M', 'TOV', 'PF'
    ]

    headers = dados['resultSets'][0]['headers']
    row_data = dados['resultSets'][0]['rowSet']
    
    indices_desejados = [headers.index(col) for col in colunas if col in headers]

    stats_list = []
    for game in row_data:
        stats = {colunas[i]: game[indices_desejados[i]] for i in range(len(indices_desejados))}
        stats_list.append(stats)

    # Limitar a lista ao número de registros fornecido pelo usuário
    stats_list = stats_list[:int(qtd_registros)]

    # Criar o DataFrame
    df = pd.DataFrame(stats_list, columns=colunas)

    # Adicionar as colunas com as somas PTS+REB+AST, PTS+REB e PTS+AST
    df['PTS+REB+AST'] = df['PTS'] + df['REB'] + df['AST']
    df['PTS+REB'] = df['PTS'] + df['REB']
    df['PTS+AST'] = df['PTS'] + df['AST']

    # Calcular as médias para colunas numéricas, ignorando a coluna GAME_DATE
    medias = {col: df[col].mean() for col in df.columns if col != 'GAME_DATE'}

    # Adicionar as médias ao DataFrame (preenchendo a coluna 'GAME_DATE' com 'Média')
    medias['GAME_DATE'] = 'Média'
    df_medias = pd.DataFrame([medias])

    # Concatenar a linha de médias ao DataFrame original
    df = pd.concat([df, df_medias], ignore_index=True)

    # Exportar para o Excel
    df.to_excel(nome_arquivo, index=False)
    print(f"Estatísticas exportadas com sucesso para {nome_arquivo}")

def exportar_estatisticas_time(dados, nome_arquivo, qtd_registros=10):
    print('Por favor aguarde... exportando estatísticas...')

    colunas = [
        'GAME_DATE_EST', 'PTS_QTR1', 'PTS_QTR2', 'PTS_QTR3', 'PTS_QTR4', 'PTS'
    ]

    headers = dados['resultSets'][0]['headers']
    row_data = dados['resultSets'][0]['rowSet']
    
    indices_desejados = [headers.index(col) for col in colunas if col in headers]

    stats_list = []
    for game in row_data:
        stats = {colunas[i]: game[indices_desejados[i]] for i in range(len(indices_desejados))}
        stats_list.append(stats)

    # Limitar a lista ao número de registros fornecido pelo usuário
    stats_list = stats_list[:int(qtd_registros)]

    # Criar o DataFrame
    df = pd.DataFrame(stats_list, columns=colunas)

    # Calcular as médias para colunas numéricas, ignorando a coluna GAME_DATE_EST
    medias = {col: df[col].mean() for col in df.columns if col != 'GAME_DATE_EST'}

    # Adicionar as médias ao DataFrame (preenchendo a coluna 'GAME_DATE' com 'Média')
    medias['GAME_DATE_EST'] = 'Média'
    df_medias = pd.DataFrame([medias])

    # Concatenar a linha de médias ao DataFrame original
    df = pd.concat([df, df_medias], ignore_index=True)

    # Exportar para o Excel
    df.to_excel(nome_arquivo, index=False)
    print(f"Estatísticas exportadas com sucesso para {nome_arquivo}")

# Função para buscar o ID de um time pelo nome
def buscar_id_time(nome_time):

    resultados = [team for team in teams if nome_time.lower() in (team[1].lower(), team[2].lower(), team[5].lower())]

    if resultados:
        print('\n')
        print("Times encontrados:")
        for i, team in enumerate(resultados):
            print(f"{i + 1}. {team[2]} (ID: {team[0]})")
        
        # Permitir que o usuário selecione o time correto
        while True:
            try:
                escolha = int(input("Escolha o número do time: ")) - 1
                if 0 <= escolha < len(resultados):
                    return resultados[escolha][0]  # Retorna o ID do time
                else:
                    print("Número inválido. Tente novamente.")
            except ValueError:
                print("Entrada inválida. Por favor, insira um número.")
    else:
        print("Time não encontrado.")
        return None
    
# Função para buscar estatísticas do time
def buscar_estatisticas_time(team_id, qtd_registros):
    headerRequest = {
        "Referer": "https://www.nba.com/",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.121 Safari/537.36"
    }

    stats = []
    stats_list = []
    
    for temporada in temporadas:
        for season_type in ["Pre Season", "Regular Season", "Playoffs"]:
            params = {
                "TeamID": team_id, 
                "Season": temporada, 
                "SeasonType": season_type
            }
            response = requests.get(API_URL_TEAM_GAMELOGS, headers=headerRequest, params=params)

            if response.status_code == 200:
                stats = stats + response.json()['resultSets'][0]['rowSet']
            else:
                print(f"Erro ao buscar estatísticas do jogador para {temporada} {season_type}.")
                return None

    gamesLimited = stats[:int(qtd_registros)]

    for game in gamesLimited:
        game_id = game[4]  # Game_ID está no índice 2

        print(f"Buscando estatísticas do jogo {game_id} ...")
        row_data = buscar_pontos_jogo(game_id, team_id)
        stats_list.append(row_data)

    resultado_agrupado = {
        'resultSets': [{
            'headers': header_boxscore_line_score,
            'rowSet': stats_list
        }]
    }

    return resultado_agrupado

def buscar_pontos_jogo(game_id, team_id):
    global header_boxscore_line_score

    headers = {
        "Referer": "https://www.nba.com/",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.121 Safari/537.36"
    }

    params = {
        "GameID": game_id
    }

    response = requests.get(API_URL_BOXSCORE_SUMMARY, headers=headers, params=params)

    stat = []
    if response.status_code == 200:
        data = response.json()

        #5 = line_score
        header_boxscore_line_score = data['resultSets'][5]['headers']
        row_data = data['resultSets'][5]['rowSet']

        for game in row_data:

            if game[3] == team_id:
                stat = game
    else:
        print(f"Erro {response.status_code} ao buscar pontos do jogo {game_id}. Mensagem: {response.text}")
        return None
    
    return stat

if __name__ == "__main__":
    sair = False

    while not sair:
        data_hora_atual = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

        escolha = None
        while escolha not in ['1', '2']:
            escolha = input("Você deseja buscar por (1) Jogador ou (2) Time? Digite 1 ou 2: ")
            if escolha not in ['1', '2']:
                print("Opção inválida! Por favor, digite 1 para Jogador ou 2 para Time.")
        
        qtd_registros = None
        while not (qtd_registros and qtd_registros.isdigit() and int(qtd_registros) > 0):
            qtd_registros = input("Digite a quantidade de registros que serão exportados para planilha: ")
            if not (qtd_registros and qtd_registros.isdigit() and int(qtd_registros) > 0):
                print("Entrada inválida! Por favor, insira um número inteiro positivo.")

        if escolha == '1':
            # Permitir que o usuário insira o nome do jogador
            nome_jogador = input("Digite o nome do jogador: ")

            # Busca o ID do jogador pelo nome
            player_id = buscar_id_jogador(nome_jogador)

            if player_id is None:
                # Se não encontrar o jogador, permitir a inserção manual do ID
                player_id = input("Não foi possível acessar a API, insira o ID do jogador manualmente: ")

            # Agora buscamos as estatísticas do jogador
            dados_estatisticas = buscar_estatisticas_jogador(player_id)

            if dados_estatisticas:
                # Se as estatísticas foram retornadas com sucesso, exportamos para Excel
                exportar_para_excel(dados_estatisticas, f"estatisticas_jogador_{nome_jogador}_{data_hora_atual}.xlsx", qtd_registros)
            else:
                print("Não foi possível obter as estatísticas do jogador.")
        elif escolha == '2':
            # Permitir que o usuário insira o nome do time
            nome_time = input("Digite o nome do time: ")

            # Busca o ID do time pelo nome
            team_id = buscar_id_time(nome_time)

            if team_id is None:
                # Se não encontrar o time, permitir a inserção manual do ID
                team_id = input("Não foi encontrado o time, insira o ID do time manualmente: ")

            # Agora buscamos as estatísticas do time
            dados_estatisticas_time = buscar_estatisticas_time(team_id, qtd_registros)

            if dados_estatisticas_time:
                # Se as estatísticas foram retornadas com sucesso, exportamos para Excel
                exportar_estatisticas_time(dados_estatisticas_time, f"estatisticas_time_{nome_time}_{data_hora_atual}.xlsx", qtd_registros)
            else:
                print("Não foi possível obter as estatísticas do time.")
        
        sair_opcao = input("Deseja sair do programa? Digite 's' para sair ou qualquer outra tecla para continuar: ").lower()
        print('\n')
        if sair_opcao == 's':
            sair = True

    print("Programa encerrado.")