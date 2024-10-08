from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404
from .models import League, Match, LeagueTeam, LeagueStanding, Team, TeamSeasonStatistics
import http.client
import json, requests

# Create your views here.
# Đặt headers cho API
headers = {
	"x-rapidapi-key": "69add1c8a2mshd66c5aa11eccb10p1c1f6bjsnd3f6750e5f0a",
	"x-rapidapi-host": "api-football-v1.p.rapidapi.com"
}

leagues_id_list = [39]  # ID các giải đấu , 140, 135, 78, 61
season_list = [2024]

#---------------------------------------------------------------------------------------------------------------
def fetch_and_save_leagues(request):
    url = "https://api-football-v1.p.rapidapi.com/v3/leagues"
    
    response = requests.get(url, headers=headers)
    leagues = response.json()

    for league in leagues['response']:
        league_data = league['league']
        country_data = league['country']

        league_id = league_data['id']
        league_name = league_data['name']
        league_type = league_data['type']
        league_logo = league_data.get('logo')
        country_name = country_data['name']
        country_code = country_data.get('code')
        country_flag = country_data.get('flag')

        League.objects.update_or_create(
            api_id=league_id,
            defaults={
                'api_id': league_id,
                'name': league_name,
                'type': league_type,
                'image': league_logo,
                'country': country_name,
                'country_code': country_code,
                'country_flag': country_flag,
            }
        )

    return HttpResponse("Leagues imported successfully.")

#---------------------------------------------------------------------------------------------------------------
def fetch_and_save_standings(request):
    url = "https://api-football-v1.p.rapidapi.com/v3/standings"

    for league in leagues_id_list:
        for season in season_list:
            querystring = {"league": league, "season": season}
            response = requests.get(url, headers=headers, params=querystring)
            standings = response.json()

            # Kiểm tra xem có dữ liệu không
            if standings['results'] > 0:
                for standing in standings['response']:
                    league_data = standing['league']
                    league_id = league_data['id']
                    league_name = league_data['name']
                    country_name = league_data['country']
                    season = league_data['season']
                    
                    for team_standing in league_data['standings'][0]:  # Giả sử bạn chỉ cần standings đầu tiên
                        team = team_standing['team']
                        rank = team_standing['rank']
                        team_id = team['id']
                        team_name = team['name']
                        logo = team['logo']
                        points = team_standing['points']
                        goals_diff = team_standing['goalsDiff']
                        
                        all_stats = team_standing['all']
                        played = all_stats['played']
                        win = all_stats['win']
                        draw = all_stats['draw']
                        lose = all_stats['lose']
                        goals_for = all_stats['goals']['for']
                        goals_against = all_stats['goals']['against']
                        update_time = team_standing['update']

                        # Lưu hoặc cập nhật dữ liệu vào cơ sở dữ liệu
                        LeagueStanding.objects.update_or_create(
                            league_id=league_id,
                            season=season,
                            rank=rank,
                            defaults={
                                'league_name': league_name,
                                'country_name': country_name,
                                'team_id': team_id,
                                'team_name': team_name,
                                'logo': logo,
                                'points': points,
                                'goals_diff': goals_diff,
                                'played': played,
                                'win': win,
                                'draw': draw,
                                'lose': lose,
                                'goals_for': goals_for,
                                'goals_against': goals_against,
                                'update_time': update_time,
                            }
                        )

    return HttpResponse("Standings imported successfully.")

#---------------------------------------------------------------------------------------------------------------
def fetch_and_save_teams(request):  # 1 Team = 1 Request. 
    # team_ids = LeagueStanding.objects.values_list('team_id', flat=True)
    # Prepare the query parameters
    team_ids = [49, 66, 51, 34, 36, 47, 65, 55, 48, 35, 33, 46, 45, 57, 52, 41, 39]
    # [40, 50, 42, 49, 66, 51, 34, 36, 47, 65, 55, 48, 35, 33, 46, 45, 57, 52, 41, 39]

    for team_id in team_ids:
        # Prepare the query parameters for each team ID
        querystring = {"id": team_id}

        # Make the API request
        response = requests.get("https://api-football-v1.p.rapidapi.com/v3/teams", headers=headers, params=querystring)

        if response.status_code == 200:
            data = response.json()
            # Check if the response contains the team data
            if 'response' in data and data['response']:
                team_data = data['response'][0]['team']  # Access the team data
                venue_data = data['response'][0]['venue']
            
                # Save or update the team in the database
                try:
                    team, created = Team.objects.update_or_create(
                        api_id=team_data['id'],
                        defaults={
                            'api_id': team_data['id'],   
                            'name': team_data['name'],  
                            'code': team_data.get('code', ''),
                            'country': team_data.get('country', ''),
                            'founded': team_data.get('founded', None),
                            'image': team_data.get('logo', ''),  
                            'venue_id': venue_data.get('id'),
                            'venue_name': venue_data.get('name'),
                            'venue_address': venue_data.get('address'),
                            'venue_city': venue_data.get('city'),
                            'venue_capacity': venue_data.get('capacity'),
                            'venue_surface': venue_data.get('surface'),
                            'venue_image': venue_data.get('image'),

                            # Add other fields if available
                        }
                    )
                    print(f"{'Created' if created else 'Updated'}: {team.name}")
                except Exception as e:
                    print(f"Error saving team: {str(e)}")

        else:
            print(f"Failed to fetch data : {response.status_code}")

    return HttpResponse("Matches imported successfully.")
    
#---------------------------------------------------------------------------------------------------------------
def fetch_and_save_matches(request):
    url = "https://api-football-v1.p.rapidapi.com/v3/fixtures"
    querystring = {"league": "39", "season": "2024"}

    headers = {
        "x-rapidapi-key": "69add1c8a2mshd66c5aa11eccb10p1c1f6bjsnd3f6750e5f0a",
        "x-rapidapi-host": "api-football-v1.p.rapidapi.com"
    }

    response = requests.get(url, headers=headers, params=querystring)
    matches = response.json()

    for match in matches['response']:
        fixture_data = match['fixture']
        league_data = match['league']
        teams_data = match['teams']
        score_data = match['score']

        # Trích xuất thông tin từ fixture
        match_id = fixture_data['id']
        date = fixture_data['date']
        venue_id = fixture_data['venue']['id']
        venue_name = fixture_data['venue']['name']
        venue_city = fixture_data['venue']['city']
        status = fixture_data['status']['long']
        referee = fixture_data.get('referee', 'Unknown')  # Tránh lỗi nếu referee không có trong dữ liệu

        # Trích xuất thông tin từ league
        league_id = league_data['id']
        league_name = league_data['name']
        country_name = league_data['country']
        season = league_data['season']

        # Trích xuất thông tin từ teams
        home_team_id = teams_data['home']['id']
        away_team_id = teams_data['away']['id']

        home_team_name = teams_data['home']['name']
        away_team_name = teams_data['away']['name']

        # Trích xuất thông tin từ score
        ht_score_data = score_data['halftime']
        ft_score_data = score_data['fulltime']
        et_score_data = score_data['extratime']
        pk_score_data = score_data['penalty']

        ht_home = ht_score_data['home']
        ht_away = ht_score_data['away']
        ft_home = ft_score_data['home']
        ft_away = ft_score_data['away']
        et_home = et_score_data.get('home')  # Xử lý trường hợp extratime là null
        et_away = et_score_data.get('away')
        pk_home = pk_score_data.get('home')
        pk_away = pk_score_data.get('away')

        home_team = Team.objects.get(api_id=home_team_id)
        away_team = Team.objects.get(api_id=away_team_id)
        league_id_new = League.objects.get(api_id=league_id)

        # Cập nhật hoặc tạo mới Match
        Match.objects.update_or_create(
            api_id=match_id,
            defaults={
                'api_id': match_id,
                'season': season,
                'league_id': league_id_new,
                'country_name': country_name,
                'home': home_team,
                'away': away_team,
                'date': date,
                'status': status,
                'referee': referee,
                'venue_id': venue_id,
                'venue_name': venue_name,
                'venue_city': venue_city,
                'ht_home': ht_home,
                'ht_away': ht_away,
                'ft_home': ft_home,
                'ft_away': ft_away,
                'et_home': et_home,
                'et_away': et_away,
                'pk_home': pk_home,
                'pk_away': pk_away,
            }
        )

        # Cập nhật hoặc tạo mới LeagueTeam cho cả đội nhà và đội khách
        LeagueTeam.objects.update_or_create(
            team_id=home_team_id,
            defaults={
                'league_id': league_id_new.id,
                'league_name': league_name,
                'team_id': home_team_id,
                'team_name': home_team_name,
            }
        )

    return HttpResponse("Matches imported successfully.")