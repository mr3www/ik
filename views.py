from django.http import HttpResponse
from django.shortcuts import render
from .models import League, Match, LeagueTeam
import http.client
import json

# Create your views here.
# Đặt headers cho API
headers = {
    'x-rapidapi-host': "api-football-v1.p.rapidapi.com",
    'x-rapidapi-key': "YOUR_API_KEY"  # Thay thế bằng API key của bạn
}

leagues_id_list = [39, 140, 135, 78, 61]  # ID các giải đấu
season_list = 2024

#---------------------------------------------------------------------------------------------------------------
def fetch_and_save_leagues(request):
    conn = http.client.HTTPSConnection("api-football-v1.p.rapidapi.com")
    conn.request("GET", "/v3/leagues", headers=headers)
    
    res = conn.getresponse()
    data = res.read()
    leagues = json.loads(data)

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

    conn.close()
    return HttpResponse("Leagues imported successfully.")

#---------------------------------------------------------------------------------------------------------------
def fetch_and_save_matches(request):
    conn = http.client.HTTPSConnection("api-football-v1.p.rapidapi.com")

    for league_id in leagues_id_list:
        conn.request("GET", f"/v3/fixtures?league={league_id}&season={season_list}", headers=headers)
        res = conn.getresponse()
        data = res.read()
        matches = json.loads(data)

        for match in matches['response']:
            fixture_data = match['fixture']
            fixture_venue = fixture_data['venue']
            fixture_status = fixture_data['status']
            league_data = match['league']
            teams_data = match['teams']
            home_teams_data = teams_data['home']
            away_teams_data = teams_data['away']
            score_data = match['score']
            ht_score_data = score_data['halftime']
            ft_score_data = score_data['fulltime']  
            et_score_data = score_data['extratime']
            pk_score_data = score_data['penalty']

            # Trích xuất thông tin cần thiết
            match_id = fixture_data['id']
            league_id = league_data['id']
            league_name = league_data['id']
            country_name = league_data['country']
            season = league_data['season']
            home_team_id = home_teams_data['id']
            away_team_id = away_teams_data['id']
            home_team_name = home_teams_data['name']
            date = fixture_data['date']
            venue_id = fixture_venue['id']
            venue_name = fixture_venue['name']
            venue_city = fixture_venue['city']
            status = fixture_status['long']
            referee = fixture_data['referee']
            ht_home = ht_score_data['home']
            ht_away = ht_score_data['away']
            ft_home = ft_score_data['home']
            ft_away = ft_score_data['away']
            et_home = et_score_data['home']
            et_away = et_score_data['away']
            pk_home = pk_score_data['home']
            pk_away = pk_score_data['away']

            # Cập nhật hoặc tạo mới League
            Match.objects.update_or_create(
                api_id=match_id,
                defaults={
                    'api_id': match_id,
                    'season': season,
                    'league_id': league_id,
                    'country_name': country_name,
                    'home': home_team_id,
                    'away': away_team_id,
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

            Match.objects.update_or_create(
                    api_id=match_id,
                    defaults={
                        'api_id': match_id,
                        'season': season,
                        'league_id': league_id,
                        'country_name': country_name,
                        'home': home_team_id,
                        'away': away_team_id,
                        'date': date,
                        'status': status,
                        'referee': referee,
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

            # Cập nhật hoặc tạo mới LeagueTeam
            LeagueTeam.objects.update_or_create(
                    team_id=home_team_id,
                    defaults={
                        'league_id': league_id,
                        'league_name': league_name,
                        'team_id': home_team_id,
                        'team_name': home_team_name,
                    }
                )   

    conn.close()
    return HttpResponse("Matches imported successfully.")


