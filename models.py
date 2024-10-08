from django.db import models
from django.utils.text import slugify
import uuid

# Create your models here.

#---------------------------------------------------------------------------------------------------------------
class Country(models.Model): # request("GET", "/v3/fixtures?league=39&season=2020", headers=headers)
    id = models.AutoField(primary_key=True)  # Sử dụng AutoField cho id tự động tăng
    country_code = models.CharField(max_length=2, unique=True)  # Mã quốc gia, ví dụ "AL"
    country_name = models.CharField(max_length=255)  # Tên quốc gia, ví dụ "Albania"
    country_flag = models.URLField(max_length=500)  # URL của cờ quốc gia

    def __str__(self):
        return self.country_name

#---------------------------------------------------------------------------------------------------------------
class League(models.Model):  # request("GET", "/v3/leagues", headers=headers)
    id = models.AutoField(primary_key=True)  # Sử dụng AutoField cho id tự động tăng
    api_id = models.IntegerField(null=True, blank=True, db_index=True, unique=True)  # ID từ API-FOOTBALL
    name = models.CharField(max_length=255, db_index=True)
    type = models.CharField(max_length=50)  # Type ('League' or 'Cup')
    image = models.URLField(blank=True, null=True)
    country = models.CharField(max_length=255, null=True)
    country_code = models.CharField(max_length=10, null=True)
    country_flag = models.URLField(blank=True, null=True)

    def __str__(self):
        return self.name
    
#---------------------------------------------------------------------------------------------------------------
class LeagueTeam(models.Model):
    id = models.AutoField(primary_key=True)
    league_id = models.PositiveIntegerField(unique=True)  # Đảm bảo rằng league_id là duy nhất
    league_name = models.CharField(max_length=255)
    team_id = models.PositiveIntegerField()
    team_name = models.CharField(max_length=255)

    def __str__(self):
        return f"{self.league_name} - {self.team_name}"

#---------------------------------------------------------------------------------------------------------------
class Team(models.Model):  # request("GET", "/v3/teams?id={33}", headers=headers) . Need to find teamsid from League Standing
    id = models.AutoField(primary_key=True)  # Sử dụng AutoField cho id tự động tăng
    api_id = models.IntegerField( null=True, blank=True, db_index=True, unique=True)  # ID từ API-FOOTBALL
    name = models.CharField(max_length=255, db_index=True)
    code = models.CharField(max_length=10, blank=True, null=True)
    country = models.CharField(max_length=255)
    founded = models.IntegerField(null=True, blank=True)
    image = models.URLField(blank=True, null=True)
    venue_id = models.IntegerField(null=True, blank=True, db_index=True, unique=True)
    venue_name = models.CharField(max_length=255)
    venue_address = models.CharField(max_length=255, blank=True, null=True)
    venue_city = models.CharField(max_length=255, blank=True, null=True)
    venue_capacity = models.IntegerField(blank=True, null=True)
    venue_surface = models.CharField(max_length=50, blank=True, null=True)
    venue_image = models.URLField(blank=True, null=True)

    def __str__(self):
        return self.name

#---------------------------------------------------------------------------------------------------------------
class Match(models.Model):  #request("GET", "/v3/fixtures?league={39}&season={2020}", headers=headers)
    id = models.AutoField(primary_key=True)  # Sử dụng AutoField cho id tự động tăng
    api_id = models.IntegerField(null=True, blank=True, db_index=True, unique=True)  # ID từ API-FOOTBALL
    season = models.IntegerField(null=True, blank=True)
    league_id = models.ForeignKey(League, to_field='api_id', related_name='matches', on_delete=models.CASCADE, unique=False)
    country_name = models.CharField(max_length=255)
    home = models.ForeignKey(Team, to_field='api_id', related_name='home_matches', on_delete=models.CASCADE)
    away = models.ForeignKey(Team, to_field='api_id', related_name='away_matches', on_delete=models.CASCADE)
    date = models.DateTimeField(db_index=True)
    status = models.CharField(max_length=100)
    referee = models.CharField(max_length=255, null=True, blank=True)
    venue_id = models.IntegerField(null=True, blank=True)
    venue_name = models.CharField(max_length=255, null=True, blank=True)
    venue_city = models.CharField(max_length=255, null=True, blank=True)
    ht_home = models.IntegerField(null=True, blank=True)
    ht_away = models.IntegerField(null=True, blank=True)
    ft_home = models.IntegerField(null=True, blank=True)
    ft_away = models.IntegerField(null=True, blank=True)
    et_home = models.IntegerField(null=True, blank=True)
    et_away = models.IntegerField(null=True, blank=True)
    pk_home = models.IntegerField(null=True, blank=True)
    pk_away = models.IntegerField(null=True, blank=True)

    def __str__(self):
        return f"{self.home} vs {self.away} - {self.league_id}"

#---------------------------------------------------------------------------------------------------------------
class Player(models.Model):  # request("GET", "/v3/players?id={276}&season={2020}", headers=headers)
    id = models.AutoField(primary_key=True)  # Sử dụng AutoField cho id tự động tăng
    api_id = models.IntegerField(null=True, blank=True, db_index=True, unique=True)  # ID từ API-FOOTBALL
    name = models.CharField(max_length=255)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    date_of_birth = models.DateField(blank=True, null=True)
    nationality = models.CharField(max_length=100, blank=True, null=True)
    height = models.CharField(max_length=10, blank=True, null=True)  # e.g., "1.80m"
    position = models.CharField(max_length=50)
    image = models.URLField(blank=True, null=True)
    slug = models.SlugField(max_length=255, unique=True, blank=True)  # Thêm slug cho URL thân thiện

    def full_name(self):
        return f"{self.first_name} {self.last_name}"

    def __str__(self):
        return f"{self.name}"

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

#---------------------------------------------------------------------------------------------------------------
class PlayerTeam(models.Model):  # Crawling Data From Transfermarkt
    id = models.AutoField(primary_key=True)  # Sử dụng AutoField cho id tự động tăng
    api_id = models.IntegerField(null=True, blank=True, db_index=True, unique=True)  # Thêm api_id nếu cần
    player = models.ForeignKey(Player, on_delete=models.CASCADE)
    team = models.ForeignKey(Team, on_delete=models.CASCADE)
    joined = models.DateField()
    left = models.DateField(null=True, blank=True)

    def __str__(self):
        return f"{self.player.full_name()} - {self.team.name}"

#---------------------------------------------------------------------------------------------------------------
class Injury(models.Model):  # Crawling Data From Soccerway or Transfermarkt
    id = models.AutoField(primary_key=True)  # Sử dụng AutoField cho id tự động tăng
    api_id = models.IntegerField(null=True, blank=True, db_index=True, unique=True)  # Thêm api_id nếu cần
    league = models.ForeignKey(League, to_field='api_id', related_name='injuries', on_delete=models.CASCADE)  # Mối quan hệ với League
    player = models.ForeignKey(Player, to_field='api_id', related_name='injuries', on_delete=models.CASCADE)  # Mối quan hệ với Player
    team = models.ForeignKey(Team, to_field='api_id', related_name='injuries', on_delete=models.CASCADE)  # Mối quan hệ với Team
    injury_type = models.CharField(max_length=255)  # Loại chấn thương
    injury_date = models.DateField()  # Ngày bị chấn thương
    expected_return = models.DateField(null=True, blank=True)  # Ngày dự kiến trở lại

    def __str__(self):
        return f"Injury: {self.player.name} ({self.injury_type}) - {self.injury_date}"

#---------------------------------------------------------------------------------------------------------------
class TeamSeasonStatistics(models.Model):  #request("GET", "/v3/teams/statistics?league={39}&season={2020}&team={33}", headers=headers)
    id = models.AutoField(primary_key=True)  # Sử dụng AutoField cho ID
    api_id = models.IntegerField(db_index=True)  # Thêm trường api_id để lưu ID từ API
    team = models.ForeignKey('Team', to_field='api_id', on_delete=models.CASCADE, related_name='season_statistics')
    league = models.ForeignKey('League', to_field='api_id', on_delete=models.CASCADE, related_name='season_statistics')
    
    # Các thống kê lớn
    biggest_goals_home = models.IntegerField(default=0)
    biggest_goals_away = models.IntegerField(default=0)
    biggest_against_home = models.IntegerField(default=0)
    biggest_against_away = models.IntegerField(default=0)
    biggest_lose_home = models.CharField(max_length=10, null=True, blank=True)  # Ví dụ: "1-6"
    biggest_lose_away = models.CharField(max_length=10, null=True, blank=True)
    
    # Chuỗi trận lớn nhất
    biggest_streak_draws = models.IntegerField(default=0)
    biggest_streak_loses = models.IntegerField(default=0)
    biggest_streak_wins = models.IntegerField(default=0)
    
    # Chiến thắng lớn nhất
    biggest_wins_home = models.CharField(max_length=10, null=True, blank=True)  # Ví dụ: "9-0"
    biggest_wins_away = models.CharField(max_length=10, null=True, blank=True)  # Ví dụ: "1-4"
    
    # Clean sheet và không ghi bàn
    clean_sheet_home = models.IntegerField(default=0)
    clean_sheet_away = models.IntegerField(default=0)
    failed_to_score_home = models.IntegerField(default=0)
    failed_to_score_away = models.IntegerField(default=0)
    
    # Kết quả trận đấu
    draws_away = models.IntegerField(default=0)
    draws_home = models.IntegerField(default=0)
    loses_away = models.IntegerField(default=0)
    loses_home = models.IntegerField(default=0)
    wins_away = models.IntegerField(default=0)
    wins_home = models.IntegerField(default=0)
    
    # Phong độ gần đây
    form = models.CharField(max_length=10, null=True, blank=True)  # Ví dụ: "LWLWD"
    
    # Tổng số bàn thắng và bị thủng lưới
    goals_total_home = models.IntegerField(default=0)
    goals_total_away = models.IntegerField(default=0)
    against_total_home = models.IntegerField(default=0)
    against_total_away = models.IntegerField(default=0)
    
    # Trung bình bàn thắng và thủng lưới
    goals_avg_home = models.FloatField(default=0.0)
    goals_avg_away = models.FloatField(default=0.0)
    against_avg_home = models.FloatField(default=0.0)
    against_avg_away = models.FloatField(default=0.0)
    
    # Bàn thắng theo thời gian
    goals_0_15 = models.IntegerField(default=0)
    goals_16_30 = models.IntegerField(default=0)
    goals_31_45 = models.IntegerField(default=0)
    goals_46_60 = models.IntegerField(default=0)
    goals_61_75 = models.IntegerField(default=0)
    goals_76_90 = models.IntegerField(default=0)
    goals_91_105 = models.IntegerField(default=0)
    goals_106_120 = models.IntegerField(default=0)
    
    # Bị thủng lưới theo thời gian
    against_0_15 = models.IntegerField(default=0)
    against_16_30 = models.IntegerField(default=0)
    against_31_45 = models.IntegerField(default=0)
    against_46_60 = models.IntegerField(default=0)
    against_61_75 = models.IntegerField(default=0)
    against_76_90 = models.IntegerField(default=0)
    against_91_105 = models.IntegerField(default=0)
    against_106_120 = models.IntegerField(default=0)
    
    # Đội hình yêu thích
    favorite_lineups = models.CharField(max_length=20, null=True, blank=True)  # Ví dụ: "4-2-3-1"
    favorite_lineups_count = models.IntegerField(default=0)
    secondary_lineups = models.CharField(max_length=20, null=True, blank=True)  # Ví dụ: "4-3-1-2"
    secondary_lineups_count = models.IntegerField(default=0)
    
    # Phạt đền
    penalty_missed = models.IntegerField(default=0)
    penalty_scored = models.IntegerField(default=0)

    def __str__(self):
        return f'{self.team.name} - {self.league.name} ({self.id})'

#---------------------------------------------------------------------------------------------------------------
class PlayerSeasonStatistics(models.Model):    #request("GET", "/v3/players?league={39}&season={2020}", headers=headers)
    id = models.AutoField(primary_key=True)  # Sử dụng AutoField cho ID
    api_id = models.IntegerField(unique=True)  # Thêm trường api_id để lưu ID từ API
    player = models.ForeignKey('Player', to_field='api_id', related_name='season_statistics' ,on_delete=models.CASCADE)
    team = models.ForeignKey('Team', to_field='api_id', related_name='player_statistics' ,on_delete=models.CASCADE)
    league = models.ForeignKey('League', to_field='api_id', related_name='player_statistics' ,on_delete=models.CASCADE)
    
    appearances = models.IntegerField(default=0)
    starting = models.IntegerField(default=0)
    subs_in = models.IntegerField(default=0)
    subs_out = models.IntegerField(default=0)
    bench = models.IntegerField(default=0)
    minutes = models.IntegerField(default=0)
    captain = models.BooleanField(default=False)
    rating = models.DecimalField(max_digits=4, decimal_places=2, null=True, blank=True)  # Điểm trên thang 10
    
    # Thống kê tấn công
    shots_on = models.IntegerField(default=0)
    shots_total = models.IntegerField(default=0)
    goals = models.IntegerField(default=0)
    conceded = models.IntegerField(default=0)
    assists = models.IntegerField(default=0)
    saves = models.IntegerField(default=0)
    
    # Thống kê chuyền bóng
    passes_total = models.IntegerField(default=0)
    passes_key = models.IntegerField(default=0)
    passes_accuracy = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)  # Tỷ lệ chính xác
    
    # Thống kê phòng ngự
    tackles_total = models.IntegerField(default=0)
    blocks = models.IntegerField(default=0)
    interceptions = models.IntegerField(default=0)
    
    # Thống kê tranh chấp và đi bóng
    duels_total = models.IntegerField(default=0)
    duels_won = models.IntegerField(default=0)
    dribbles_attempts = models.IntegerField(default=0)
    dribbles_success = models.IntegerField(default=0)
    dribbles_past = models.IntegerField(default=0)
    
    # Thống kê phạm lỗi
    fouls_drawn = models.IntegerField(default=0)
    fouls_committed = models.IntegerField(default=0)
    
    # Thống kê thẻ phạt
    yellow_card = models.IntegerField(default=0)
    yellowred_card = models.IntegerField(default=0)
    red_card = models.IntegerField(default=0)
    
    # Thống kê phạt đền
    penalty_won = models.IntegerField(default=0)
    penalty_committed = models.IntegerField(default=0)
    penalty_scored = models.IntegerField(default=0)
    penalty_missed = models.IntegerField(default=0)
    penalty_saved = models.IntegerField(default=0)

    def __str__(self):
        return f'{self.player.name} - {self.team.name} ({self.id})'

#---------------------------------------------------------------------------------------------------------------
class LeagueStanding(models.Model):
    league_id = models.IntegerField()
    league_name = models.CharField(max_length=100)
    country_name = models.CharField(max_length=100)
    season = models.IntegerField()
    rank = models.IntegerField()
    team_id = models.IntegerField()
    team_name = models.CharField(max_length=100)
    logo = models.URLField()
    points = models.IntegerField()
    goals_diff = models.IntegerField()
    played = models.IntegerField()
    win = models.IntegerField()
    draw = models.IntegerField()
    lose = models.IntegerField()
    goals_for = models.IntegerField()
    goals_against = models.IntegerField()
    update_time = models.DateTimeField()

    class Meta:
        unique_together = ('league_id', 'season', 'rank')

#---------------------------------------------------------------------------------------------------------------
class StandingDescription(models.Model): #request("GET", "/v3/standings?league={39}&season={2020}", headers=headers)
    league = models.ForeignKey('League', to_field='api_id', related_name='standing_descriptions', on_delete=models.CASCADE)
    season = models.CharField(max_length=20)  # Ví dụ: '2023-2024'
    rank = models.IntegerField()  # Ví dụ: 1, 2, 3,..., 20
    description = models.CharField(max_length=255, null=True, blank=True)  # Mô tả như "Promotion - Champions League", hoặc null

    def __str__(self):
        return f'League: {self.league.name}, Season: {self.season}, Rank: {self.rank}'

    class Meta:
        unique_together = ('league', 'season', 'rank')  # Đảm bảo mỗi league, season, rank là duy nhất

#---------------------------------------------------------------------------------------------------------------
class StandingDeduction(models.Model):  #Crawling Data to check if whether it have team be deduction points for any reason
    league = models.ForeignKey(League, to_field='api_id', on_delete=models.CASCADE)
    season = models.CharField(max_length=10)  # Ví dụ: "2023-2024"
    team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='standing_deductions')  # Thêm related_name
    description = models.TextField(null=True, blank=True)
    points_deduction = models.IntegerField(default=0)  # Số điểm bị trừ

    def __str__(self):
        return f"{self.league} - {self.season} - Team: {self.team} - Reason: {self.description} - Points deduction: {self.points_deduction}"

#---------------------------------------------------------------------------------------------------------------
#https://rapidapi.com/people-api-people-api-default/api/football-news11/playground/apiendpoint_7ba472f9-5c31-4342-a378-3fcfd45c7181
class News(models.Model):  # request("GET", "/api/news-by-date?date=2024-01-01&lang=en&page=1", headers=headers)
    id = models.AutoField(primary_key=True)  # Sử dụng AutoField cho ID
    api_id = models.IntegerField(unique=True)  # Thêm trường api_id để lưu ID từ API
    title = models.CharField(max_length=255)  # Tiêu đề tin tức
    image_url = models.URLField(max_length=200, null=True, blank=True)  # URL hình ảnh
    original_url = models.URLField(max_length=200)  # URL gốc của tin tức
    published_at = models.DateTimeField()  # Ngày giờ phát hành
    slug = models.SlugField(max_length=255, unique=True)  # Slug cho tin tức

    def __str__(self):
        return self.title

#---------------------------------------------------------------------------------------------------------------
