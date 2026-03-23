import pygame
import random
import time
import json
import os
import asyncio  # Required for web compatibility

# --- DATA PERSISTENCE ---
STATS_FILE = "cpl_stats.json"

def load_profile():
    if os.path.exists(STATS_FILE):
        try:
            with open(STATS_FILE, "r") as f:
                return json.load(f)
        except:
            pass
    return {
        "matches": 0, "won": 0, "lost": 0, "teams_played": [],
        "max_runs": 0, "max_wickets": 0, "best_bowling": "N/A"
    }

def save_match_to_profile(p_score, c_score, p_team):
    data = load_profile()
    data["matches"] += 1
    if p_team not in data["teams_played"]:
        data["teams_played"].append(p_team)
    
    if p_score > c_score: data["won"] += 1
    elif c_score > p_score: data["lost"] += 1
    
    p_name, p_runs = calculate_pom()
    if p_runs > data["max_runs"]:
        data["max_runs"] = p_runs
        
    for team in bowler_stats:
        for name, stat in bowler_stats[team].items():
            if stat[0] > data["max_wickets"]:
                data["max_wickets"] = stat[0]
                data["best_bowling"] = f"{name} ({stat[0]}/{stat[1]})"

    try:
        with open(STATS_FILE, "w") as f:
            json.dump(data, f)
    except:
        pass # Browsers sometimes restrict local file writing

# --- SETUP ---
pygame.init()
WIDTH, HEIGHT = 1100, 850 
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("CPL Pro - Strategy Edition")
clock = pygame.time.Clock()

# Fonts
font_main = pygame.font.SysFont("Impact", 60)
font_sub = pygame.font.SysFont("Arial", 32, bold=True)
font_stats = pygame.font.SysFont("Courier New", 18, bold=True)
font_tiny = pygame.font.SysFont("Arial", 20, bold=True)

# Colors
FIELD_GREEN = (34, 139, 34); PITCH_COLOR = (210, 180, 140); WHITE = (255, 255, 255)
BLACK = (0, 0, 0); GOLD = (255, 215, 0); RED = (220, 20, 60); HIGHLIGHT = (0, 255, 255)
DARK_GRAY = (50, 50, 50)

team_colors = {
    "India": (0, 0, 255), "Australia": (255, 204, 0), "England": (0, 43, 127),
    "Pakistan": (1, 65, 28), "South Africa": (0, 106, 78), "New Zealand": (30, 30, 30),
    "West Indies": (123, 22, 43), "Mumbai": (0, 75, 160), "Chennai": (255, 230, 0),
    "Delhi": (0, 0, 139), "Bangalore": (200, 20, 40), "Hyderabad": (255, 130, 0),
    "Kolkata": (58, 30, 107), "Punjab": (237, 27, 36)
}

team_rosters = {
    "India": ["Rohit Sharma", "Yashasvi Jaiswal", "Virat Kohli", "Suryakumar Yadav", "Rishabh Pant", "Hardik Pandya", "Ravindra Jadeja", "Axar Patel", "Kuldeep Yadav", "Jasprit Bumrah", "Arshdeep Singh"],
    "Australia": ["Travis Head", "David Warner", "Mitchell Marsh", "Glenn Maxwell", "Marcus Stoinis", "Tim David", "Matthew Wade", "Pat Cummins", "Mitchell Starc", "Adam Zampa", "Josh Hazlewood"],
    "England": ["Jos Buttler", "Phil Salt", "Will Jacks", "Jonny Bairstow", "Harry Brook", "Liam Livingstone", "Moeen Ali", "Sam Curran", "Jofra Archer", "Adil Rashid", "Reece Topley"],
    "Pakistan": ["Babar Azam", "Mohammad Rizwan", "Usman Khan", "Fakhar Zaman", "Azam Khan", "Iftikhar Ahmed", "Imad Wasim", "Shadab Khan", "Shaheen Afridi", "Naseem Shah", "Haris Rauf"],
    "South Africa": ["Quinton de Kock", "Reeza Hendricks", "Aiden Markram", "Heinrich Klaasen", "David Miller", "Tristan Stubbs", "Marco Jansen", "Keshav Maharaj", "Kagiso Rabada", "Anrich Nortje", "Tabraiz Shamsi"],
    "New Zealand": ["Finn Allen", "Devon Conway", "Kane Williamson", "Daryl Mitchell", "Glenn Phillips", "Mark Chapman", "James Neesham", "Mitchell Santner", "Matt Henry", "Trent Boult", "Lockie Ferguson"],
    "West Indies": ["Brandon King", "Johnson Charles", "Nicholas Pooran", "Rovman Powell", "Sherfane Rutherford", "Andre Russell", "Romario Shepherd", "Roston Chase", "Akeal Hosein", "Alzarri Joseph", "Gudakesh Motie"],
    "Mumbai": ["Ishan Kishan", "Rohit Sharma", "Naman Dhir", "Suryakumar Yadav", "Tilak Varma", "Hardik Pandya", "Tim David", "Romario Shepherd", "Gerald Coetzee", "Jasprit Bumrah", "Piyush Chawla"],
    "Chennai": ["Ruturaj Gaikwad", "Rachin Ravindra", "Ajinkya Rahane", "Daryl Mitchell", "Shivam Dube", "Ravindra Jadeja", "MS Dhoni", "Sameer Rizvi", "Shardul Thakur", "Tushar Deshpande", "Matheesha Pathirana"],
    "Delhi": ["Prithvi Shaw", "David Warner", "Jake Fraser-McGurk", "Rishabh Pant", "Tristan Stubbs", "Abishek Porel", "Axar Patel", "Kuldeep Yadav", "Anrich Nortje", "Khaleel Ahmed", "Mukesh Kumar"],
    "Bangalore": ["Virat Kohli", "Faf du Plessis", "Will Jacks", "Rajat Patidar", "Glenn Maxwell", "Cameron Green", "Dinesh Karthik", "Mahipal Lomror", "Karn Sharma", "Mohammed Siraj", "Yash Dayal"],
    "Hyderabad": ["Travis Head", "Abhishek Sharma", "Aiden Markram", "Heinrich Klaasen", "Nitish Reddy", "Abdul Samad", "Shahbaz Ahmed", "Pat Cummins", "Bhuvneshwar Kumar", "Jaydev Unadkat", "T Natarajan"],
    "Kolkata": ["Phil Salt", "Sunil Narine", "Angkrish Raghuvanshi", "Shreyas Iyer", "Venkatesh Iyer", "Rinku Singh", "Andre Russell", "Ramandeep Singh", "Mitchell Starc", "Varun Chakaravarthy", "Harshit Rana"],
    "Punjab": ["Shikhar Dhawan", "Jonny Bairstow", "Prabhsimran Singh", "Sam Curran", "Jitesh Sharma", "Liam Livingstone", "Shashank Singh", "Ashutosh Sharma", "Harpreet Brar", "Harshal Patel", "Kagiso Rabada"]
}

# --- GLOBAL VARIABLES ---
state = 'MENU'; mode = ''; total_overs = 1; max_balls = 0; current_balls = 0
score = 0; wickets = 0; target = -1; innings = 1; batsman_val = 0; bowler_val = 0
toss_msg = ""; user_batting = True; player_team = ""; cpu_team = ""; selection_index = 0
is_fullscreen = False; player_captain = ""; out_batsmen = []; available_players = []
opener_select_stage = 0; match_stats = {}; bowler_stats = {}; team_final_scores = {}
striker_name = ""; non_striker_name = ""; striker_runs = 0; striker_balls = 0
non_striker_runs = 0; non_striker_balls = 0; curr_bowler_name = ""; balls_in_over = 0
striker_4s = 0; striker_6s = 0; non_striker_4s = 0; non_striker_6s = 0
flash_msg = ""; flash_timer = 0; over_log = []

# --- FUNCTIONS ---
def draw_clean_field():
    pygame.draw.circle(screen, WHITE, (WIDTH//2, 350), 380, 3)
    pygame.draw.rect(screen, PITCH_COLOR, (WIDTH//2-80, 150, 160, 400))

def draw_back_hint():
    back_text = font_tiny.render("ESC: BACK | F: FULLSCREEN", True, WHITE)
    screen.blit(back_text, (20, 20))

def draw_text_centered(text, y, font, color=WHITE):
    surf = font.render(text, True, color)
    rect = surf.get_rect(center=(WIDTH//2, y))
    screen.blit(surf, rect)

def draw_dice(x, y, value):
    if value == 0: return
    size = 70
    pygame.draw.rect(screen, WHITE, (x, y, size, size), 0, 10)
    pygame.draw.rect(screen, BLACK, (x, y, size, size), 2, 10)
    dots = {1: [(35, 35)], 2: [(18, 18), (52, 52)], 3: [(18, 18), (35, 35), (52, 52)],
            4: [(18, 18), (18, 52), (52, 18), (52, 52)], 5: [(18, 18), (18, 52), (35, 35), (52, 18), (52, 52)],
            6: [(18, 18), (18, 35), (18, 52), (52, 18), (52, 35), (52, 52)]}
    for dot in dots[value]:
        pygame.draw.circle(screen, BLACK, (x + dot[0], y + dot[1]), 6)

def calculate_pom():
    best_p = "N/A"; max_r = -1
    for t in match_stats:
        for p, v in match_stats[t].items():
            if v[0] > max_r: max_r = v[0]; best_p = p
    return best_p, max_r

def reset_match():
    global score, wickets, current_balls, innings, target, state, player_team, cpu_team, match_stats, bowler_stats, team_final_scores, balls_in_over, out_batsmen, player_captain, selection_index, batsman_val, bowler_val, striker_4s, striker_6s, non_striker_4s, non_striker_6s, flash_timer, over_log
    score = wickets = current_balls = balls_in_over = batsman_val = bowler_val = flash_timer = 0
    striker_4s = striker_6s = non_striker_4s = non_striker_6s = 0
    player_team = cpu_team = ""; innings = 1; target = -1; state = 'MENU'
    match_stats = {}; bowler_stats = {}; team_final_scores = {}; out_batsmen = []; player_captain = ""; selection_index = 0
    over_log = []

# --- WEB MAIN LOOP ---
async def main():
    global state, mode, total_overs, max_balls, current_balls, score, wickets, target, innings, batsman_val, bowler_val
    global toss_msg, user_batting, player_team, cpu_team, selection_index, is_fullscreen, player_captain, out_batsmen
    global available_players, opener_select_stage, match_stats, bowler_stats, team_final_scores, striker_name, non_striker_name
    global striker_runs, striker_balls, non_striker_runs, non_striker_balls, curr_bowler_name, balls_in_over
    global striker_4s, striker_6s, non_striker_4s, non_striker_6s, flash_msg, flash_timer, over_log, screen

    running = True
    while running:
        screen.fill(FIELD_GREEN)
        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT: running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_f:
                    is_fullscreen = not is_fullscreen
                    screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.FULLSCREEN if is_fullscreen else 0)
                if event.key == pygame.K_ESCAPE and state != 'MENU':
                    state = 'MENU'

        current_batting_team = player_team if user_batting else cpu_team
        bowling_team = cpu_team if user_batting else player_team
        batting_color = team_colors.get(current_batting_team, BLACK)

        # State Machine Logic
        if state == 'MENU':
            draw_text_centered("CRICKET PREMIER LEAGUE", 150, font_main, GOLD)
            draw_text_centered("1: INTERNATIONAL | 2: NATIONAL | 3: PROFILE", 350, font_sub)
            for event in events:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_1: mode, state = 'International', 'SELECT_TEAMS'; selection_index = 0
                    if event.key == pygame.K_2: mode, state = 'National', 'SELECT_TEAMS'; selection_index = 0
                    if event.key == pygame.K_3: state = 'PROFILE'

        elif state == 'PROFILE':
            draw_back_hint()
            p_data = load_profile()
            draw_text_centered("PLAYER CAREER STATS", 80, font_main, HIGHLIGHT)
            stats_list = [
                f"Matches Played: {p_data['matches']}",
                f"Wins: {p_data['won']} | Losses: {p_data['lost']}",
                f"Teams Used: {', '.join(p_data['teams_played'][-3:])}",
                f"Highest Indiv. Score: {p_data['max_runs']}",
                f"Best Bowling Figure: {p_data['best_bowling']}"
            ]
            for i, txt in enumerate(stats_list):
                draw_text_centered(txt, 220 + (i * 55), font_sub, WHITE)
            draw_text_centered("PRESS ESC TO RETURN", 700, font_tiny, GOLD)

        elif state == 'SELECT_TEAMS':
            draw_back_hint()
            teams_list = list(team_rosters.keys())[:7] if mode == 'International' else list(team_rosters.keys())[7:]
            draw_text_centered(f"SELECT {'YOUR TEAM' if player_team == '' else 'OPPONENT'}", 80, font_main, GOLD)
            for i, team in enumerate(teams_list):
                color = team_colors.get(team, WHITE) if i == selection_index else WHITE
                draw_text_centered(team, 150 + (i * 40), font_sub, color)
            for event in events:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_UP: selection_index = (selection_index - 1) % len(teams_list)
                    if event.key == pygame.K_DOWN: selection_index = (selection_index + 1) % len(teams_list)
                    if event.key == pygame.K_SPACE:
                        if player_team == "": player_team = teams_list[selection_index]; time.sleep(0.2)
                        else: cpu_team = teams_list[selection_index]; state = 'SELECT_OVERS'

        elif state == 'SELECT_OVERS':
            draw_text_centered("SELECT OVERS", 200, font_main, GOLD)
            draw_text_centered("A(1), B(2), C(5), D(10), E(20)", 350, font_sub)
            for event in events:
                if event.type == pygame.KEYDOWN:
                    keys = {pygame.K_a:1, pygame.K_b:2, pygame.K_c:5, pygame.K_d:10, pygame.K_e:20}
                    if event.key in keys:
                        total_overs = keys[event.key]; max_balls = total_overs * 6; state = 'SELECT_CAPTAIN'
                        available_players = list(team_rosters[player_team]); selection_index = 0

        elif state == 'SELECT_CAPTAIN':
            draw_text_centered("SELECT YOUR CAPTAIN", 100, font_main, GOLD)
            for i, p in enumerate(available_players):
                color = HIGHLIGHT if i == selection_index else WHITE
                draw_text_centered(p, 180 + (i * 40), font_sub, color)
            for event in events:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_UP: selection_index = (selection_index - 1) % 11
                    if event.key == pygame.K_DOWN: selection_index = (selection_index + 1) % 11
                    if event.key == pygame.K_SPACE:
                        player_captain = available_players[selection_index]; state = 'TOSS'; selection_index = 0

        elif state == 'TOSS':
            draw_text_centered(f"CAPTAIN {player_captain.upper()} READY FOR TOSS", 100, font_tiny, HIGHLIGHT)
            draw_text_centered("TOSS: [H] HEADS or [T] TAILS", 250, font_sub, GOLD)
            for event in events:
                if event.type == pygame.KEYDOWN:
                    if event.key in [pygame.K_h, pygame.K_t]:
                        if random.choice([True, False]): state = 'TOSS_CHOICE'
                        else:
                            choice = random.choice(['Batting', 'Bowling'])
                            toss_msg = f"{cpu_team} won and chose {choice}!"; user_batting = (choice == 'Bowling'); state = 'PRE_MATCH_ROSTERS'

        elif state == 'TOSS_CHOICE':
            draw_text_centered("YOU WON THE TOSS!", 200, font_main, HIGHLIGHT)
            draw_text_centered("1: BAT | 2: BOWL", 350, font_sub, WHITE)
            for event in events:
                if event.type == pygame.KEYDOWN:
                    user_batting = (event.key == pygame.K_1); toss_msg = "You chose to Bat!" if user_batting else "You chose to Bowl!"; state = 'PRE_MATCH_ROSTERS'

        elif state == 'PRE_MATCH_ROSTERS':
            pygame.draw.rect(screen, BLACK, (50, 50, WIDTH-100, HEIGHT-100))
            draw_text_centered("PLAYING XI", 80, font_main, GOLD)
            p_team_txt = font_sub.render(player_team.upper(), True, team_colors.get(player_team, WHITE))
            c_team_txt = font_sub.render(cpu_team.upper(), True, team_colors.get(cpu_team, WHITE))
            screen.blit(p_team_txt, (200, 160)); screen.blit(c_team_txt, (WIDTH-450, 160))
            for i in range(11):
                screen.blit(font_stats.render(team_rosters[player_team][i], True, WHITE), (200, 210 + (i*35)))
                screen.blit(font_stats.render(team_rosters[cpu_team][i], True, WHITE), (WIDTH-450, 210 + (i*35)))
            draw_text_centered("PRESS SPACE TO START", 780, font_tiny, HIGHLIGHT)
            for event in events:
                if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE: state = 'TOSS_RESULT'

        elif state == 'TOSS_RESULT':
            for t in [player_team, cpu_team]:
                if t not in match_stats: match_stats[t] = {p: [0, 0, 0, 0] for p in team_rosters[t]}
                if t not in bowler_stats: bowler_stats[t] = {} 
            draw_text_centered(toss_msg, 300, font_sub, GOLD); draw_text_centered("SPACE TO SELECT OPENERS", 450, font_tiny)
            for event in events:
                if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                    if user_batting:
                        available_players = list(team_rosters[player_team]); out_batsmen = []; state = 'CHOOSE_BATSMAN'; opener_select_stage = 0; selection_index = 0
                    else:
                        striker_name, non_striker_name = team_rosters[cpu_team][0], team_rosters[cpu_team][1]
                        striker_runs = striker_balls = striker_4s = striker_6s = 0
                        non_striker_runs = non_striker_balls = non_striker_4s = non_striker_6s = 0
                        out_batsmen = [striker_name, non_striker_name]; available_players = list(team_rosters[player_team]); state = 'CHOOSE_BOWLER'

        elif state == 'CHOOSE_BATSMAN':
            title = "SELECT STRIKER" if opener_select_stage == 0 else "SELECT NEXT BATSMAN"
            draw_text_centered(title, 80, font_main, GOLD)
            for i, p in enumerate(available_players):
                color = HIGHLIGHT if i == selection_index else WHITE
                draw_text_centered(p, 180 + (i * 40), font_sub, color)
            for event in events:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_UP: selection_index = (selection_index - 1) % len(available_players)
                    if event.key == pygame.K_DOWN: selection_index = (selection_index + 1) % len(available_players)
                    if event.key == pygame.K_SPACE:
                        choice = available_players.pop(selection_index)
                        if opener_select_stage == 0:
                            striker_name, striker_runs, striker_balls, striker_4s, striker_6s = choice, 0, 0, 0, 0; opener_select_stage = 1; selection_index = 0
                            if len(out_batsmen) > 0: out_batsmen.append(striker_name); state = 'PLAYING'
                        else:
                            non_striker_name, non_striker_runs, non_striker_balls, non_striker_4s, non_striker_6s = choice, 0, 0, 0, 0
                            out_batsmen.extend([striker_name, non_striker_name]); state = 'CHOOSE_BOWLER' if not user_batting else 'PLAYING'
                            if user_batting: curr_bowler_name = random.choice(team_rosters[cpu_team][5:]); balls_in_over = 0; over_log = []

        elif state == 'CHOOSE_BOWLER':
            draw_text_centered("SELECT BOWLER", 100, font_main, GOLD)
            for i, p in enumerate(available_players):
                color = HIGHLIGHT if i == selection_index else WHITE
                draw_text_centered(p, 180 + (i * 40), font_sub, color)
            for event in events:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_UP: selection_index = (selection_index - 1) % len(available_players)
                    if event.key == pygame.K_DOWN: selection_index = (selection_index + 1) % len(available_players)
                    if event.key == pygame.K_SPACE:
                        curr_bowler_name = available_players[selection_index]; balls_in_over = 0; over_log = []; state = 'PLAYING'

        elif state == 'PLAYING':
            draw_clean_field()
            pygame.draw.rect(screen, batting_color, (0, 0, WIDTH, 50))
            ov_num = current_balls // 6; ov_balls = current_balls % 6
            draw_text_centered(f"{score} / {wickets} ({ov_num}.{ov_balls} ov)", 220, font_main, BLACK)
            
            if target != -1:
                req_runs = target - score
                rem_balls = max_balls - current_balls
                draw_text_centered(f"Need {req_runs} runs in {rem_balls} balls", 280, font_sub, BLACK)

            draw_dice(WIDTH//2 - 85, 330, batsman_val); draw_dice(WIDTH//2 + 15, 330, bowler_val)
            
            log_x = WIDTH - 120
            for i, res in enumerate(over_log):
                bg_color = RED if res == 'W' else GOLD if res == '6' or res == '4' else DARK_GRAY
                pygame.draw.circle(screen, bg_color, (log_x, 150 + (i * 60)), 25)
                log_txt = font_tiny.render(str(res), True, WHITE)
                log_rect = log_txt.get_rect(center=(log_x, 150 + (i * 60)))
                screen.blit(log_txt, log_rect)

            if flash_timer > 0:
                msg_color = RED if "WICKET" in flash_msg else GOLD
                draw_text_centered(flash_msg, 450, font_main, msg_color)
                flash_timer -= 1

            pygame.draw.rect(screen, batting_color, (0, 650, WIDTH, 200))
            text_color = WHITE if batting_color[0] < 150 else BLACK
            screen.blit(font_stats.render(f"* {striker_name}: {striker_runs}({striker_balls}) | 4s:{striker_4s} 6s:{striker_6s}", True, HIGHLIGHT if text_color == WHITE else RED), (50, 680))
            screen.blit(font_stats.render(f"  {non_striker_name}: {non_striker_runs}({non_striker_balls}) | 4s:{non_striker_4s} 6s:{non_striker_6s}", True, text_color), (50, 715))
            screen.blit(font_stats.render(f"BOWLER: {curr_bowler_name} | Over: {balls_in_over}/6", True, text_color), (WIDTH-450, 680))

            for event in events:
                if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                    batsman_val, bowler_val = random.randint(1, 6), random.randint(1, 6)
                    current_balls += 1; striker_balls += 1; balls_in_over += 1
                    if curr_bowler_name not in bowler_stats[bowling_team]: bowler_stats[bowling_team][curr_bowler_name] = [0, 0, 0]

                    if batsman_val == bowler_val:
                        flash_msg = "WICKET!"; flash_timer = 60 
                        over_log.append('W')
                        wickets += 1; bowler_stats[bowling_team][curr_bowler_name][0] += 1
                        bowler_stats[bowling_team][curr_bowler_name][2] += 1
                        match_stats[current_batting_team][striker_name] = [striker_runs, striker_balls, striker_4s, striker_6s]
                        if wickets < 10:
                            if user_batting:
                                available_players = [p for p in team_rosters[player_team] if p not in out_batsmen]
                                state = 'CHOOSE_BATSMAN'; opener_select_stage = 0; selection_index = 0
                            else:
                                striker_name = team_rosters[cpu_team][wickets+1]; out_batsmen.append(striker_name)
                                striker_runs = striker_balls = striker_4s = striker_6s = 0
                    else:
                        if batsman_val == 6: flash_msg = "BIG SIX!"; flash_timer = 60
                        over_log.append(str(batsman_val))
                        score += batsman_val; striker_runs += batsman_val
                        bowler_stats[bowling_team][curr_bowler_name][1] += batsman_val
                        bowler_stats[bowling_team][curr_bowler_name][2] += 1
                        if batsman_val == 4: striker_4s += 1
                        if batsman_val == 6: striker_6s += 1
                        
                        if batsman_val % 2 != 0:
                            striker_name, non_striker_name = non_striker_name, striker_name
                            striker_runs, non_striker_runs = non_striker_runs, striker_runs
                            striker_balls, non_striker_balls = non_striker_balls, striker_balls
                            striker_4s, non_striker_4s = non_striker_4s, striker_4s
                            striker_6s, non_striker_6s = non_striker_6s, striker_6s

                    if balls_in_over == 6 and current_balls < max_balls:
                        striker_name, non_striker_name = non_striker_name, striker_name
                        striker_runs, non_striker_runs = non_striker_runs, striker_runs
                        striker_balls, non_striker_balls = non_striker_balls, striker_balls
                        striker_4s, non_striker_4s = non_striker_4s, striker_4s
                        striker_6s, non_striker_6s = non_striker_6s, striker_6s
                        if not user_batting:
                            available_players = team_rosters[player_team]; state = 'CHOOSE_BOWLER'; selection_index = 0
                        else:
                            curr_bowler_name = random.choice(team_rosters[cpu_team][5:]); balls_in_over = 0; over_log = []

                    if (target != -1 and score >= target) or wickets >= 10 or current_balls >= max_balls:
                        match_stats[current_batting_team][striker_name] = [striker_runs, striker_balls, striker_4s, striker_6s]
                        match_stats[current_batting_team][non_striker_name] = [non_striker_runs, non_striker_balls, non_striker_4s, non_striker_6s]
                        team_final_scores[current_batting_team] = [score, wickets]; state = 'INNINGS_BREAK_STATS'

        elif state == 'INNINGS_BREAK_STATS':
            pygame.draw.rect(screen, BLACK, (50, 50, 1000, 750))
            draw_text_centered(f"{current_batting_team.upper()} BATTING", 80, font_sub, GOLD)
            header_bat = font_stats.render(f"{'PLAYER'.ljust(20)}{'R(B)'.ljust(12)}{'4s'.ljust(6)}{'6s'.ljust(6)}{'S/R'}", True, HIGHLIGHT)
            screen.blit(header_bat, (150, 130))
            y_pos = 165
            for name, vals in match_stats[current_batting_team].items():
                if vals[1] > 0 or name == striker_name or name == non_striker_name:
                    runs_balls = f"{vals[0]}({vals[1]})"
                    sr = round((vals[0]/vals[1])*100, 1) if vals[1] > 0 else 0.0
                    row_str = f"{name.ljust(20)}{runs_balls.ljust(12)}{str(vals[2]).ljust(6)}{str(vals[3]).ljust(6)}{str(sr)}"
                    screen.blit(font_stats.render(row_str, True, WHITE), (150, y_pos))
                    y_pos += 30
            draw_text_centered(f"{bowling_team.upper()} BOWLING", 480, font_sub, GOLD)
            header_bowl = font_stats.render(f"{'PLAYER'.ljust(20)}{'W'.ljust(6)}{'R'.ljust(6)}{'OVERS'.ljust(10)}{'ECON'}", True, HIGHLIGHT)
            screen.blit(header_bowl, (150, 520))
            y_pos_bowl = 555
            for name, vals in bowler_stats[bowling_team].items():
                ov = f"{vals[2]//6}.{vals[2]%6}"
                econ = round(vals[1] / (vals[2]/6), 2) if vals[2] > 0 else 0.00
                row_bowl = f"{name.ljust(20)}{str(vals[0]).ljust(6)}{str(vals[1]).ljust(6)}{ov.ljust(10)}{str(econ)}"
                screen.blit(font_stats.render(row_bowl, True, WHITE), (150, y_pos_bowl))
                y_pos_bowl += 30
            draw_text_centered(f"TOTAL: {team_final_scores[current_batting_team][0]}-{team_final_scores[current_batting_team][1]}", 780, font_tiny, HIGHLIGHT)
            for event in events:
                if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                    if innings == 1:
                        target, score, wickets, current_balls, balls_in_over, innings = team_final_scores[current_batting_team][0]+1, 0, 0, 0, 0, 2
                        user_batting = not user_batting; over_log = []
                        if user_batting:
                            available_players = list(team_rosters[player_team]); out_batsmen = []; state = 'CHOOSE_BATSMAN'; opener_select_stage = 0
                        else:
                            striker_name, non_striker_name = team_rosters[cpu_team][0], team_rosters[cpu_team][1]
                            striker_runs = striker_balls = striker_4s = striker_6s = 0
                            non_striker_runs = non_striker_balls = non_striker_4s = non_striker_6s = 0
                            out_batsmen = [striker_name, non_striker_name]; available_players = list(team_rosters[player_team]); state = 'CHOOSE_BOWLER'
                    else: state = 'GAMEOVER'

        elif state == 'GAMEOVER':
            pygame.draw.rect(screen, BLACK, (10, 10, WIDTH-20, HEIGHT-20))
            draw_text_centered("MATCH FINISHED", 100, font_main, HIGHLIGHT)
            p_score, p_wickets = team_final_scores[player_team]
            c_score, c_wickets = team_final_scores[cpu_team]
            if p_score > c_score: result_text = f"{player_team.upper()} WON BY {p_score - c_score} RUNS!"
            elif c_score > p_score: result_text = f"{cpu_team.upper()} WON BY {c_score - p_score} RUNS!"
            else: result_text = "THE MATCH IS A TIE!"
            draw_text_centered(result_text, 250, font_sub, GOLD)
            draw_text_centered(f"{player_team}: {p_score}-{p_wickets}", 380, font_sub, team_colors.get(player_team, WHITE))
            draw_text_centered(f"{cpu_team}: {c_score}-{c_wickets}", 450, font_sub, team_colors.get(cpu_team, WHITE))
            p_name, p_runs = calculate_pom()
            draw_text_centered(f"PLAYER OF THE MATCH: {p_name} ({p_runs} Runs)", 600, font_sub, HIGHLIGHT)
            draw_text_centered("PRESS R TO SAVE & RESTART", 780, font_tiny, WHITE)
            for event in events:
                # Inside your game loop:
for event in pygame.event.get():
                if event.type == pygame.KEYDOWN and event.key == pygame.K_r:
                    save_match_to_profile(p_score, c_score, player_team); reset_match()

        pygame.display.flip()
        clock.tick(60)
        await asyncio.sleep(0) # IMPORTANT: Prevents browser lock-up

    pygame.quit()

# Run the game
if __name__ == "__main__":
    asyncio.run(main())
