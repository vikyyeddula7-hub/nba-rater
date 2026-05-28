"""
tennis_data.py — ATP Top 150 as of May 25, 2026.
Source: TennisExplorer.com live rankings.
SmashRater scores computed from ranking, Grand Slams, and career trajectory.
"""

def compute_tennis_rating(rank, grand_slams, career_high):
    base = max(55, 90 - (rank - 1) * 0.23)
    gs_bonus = min(9, grand_slams * 1.8)
    # Reward players who have been higher ranked than now
    ch_bonus = 1.5 if career_high <= 5 and rank > 5 else 0
    return round(min(99, max(55, base + gs_bonus + ch_bonus)))


def tier(r):
    if r >= 95:   return {"label": "All-Time Legend",  "color": "#FFD700", "badge": "diamond"}
    elif r >= 90: return {"label": "Grand Slam Elite", "color": "#C0C0C0", "badge": "gold"}
    elif r >= 85: return {"label": "Top 10",           "color": "#CD7F32", "badge": "silver"}
    elif r >= 78: return {"label": "Top 30",           "color": "#4FC3F7", "badge": "bronze"}
    elif r >= 70: return {"label": "Top 75",           "color": "#81C784", "badge": "green"}
    else:         return {"label": "Top 150",          "color": "#B0BEC5", "badge": "grey"}


COUNTRY_FLAGS = {
    "Italy":"🇮🇹","Spain":"🇪🇸","Germany":"🇩🇪","Serbia":"🇷🇸","USA":"🇺🇸",
    "Canada":"🇨🇦","Australia":"🇦🇺","Russia":"🇷🇺","Norway":"🇳🇴","Kazakhstan":"🇰🇿",
    "Czech Republic":"🇨🇿","France":"🇫🇷","Denmark":"🇩🇰","Greece":"🇬🇷","Great Britain":"🇬🇧",
    "Croatia":"🇭🇷","Argentina":"🇦🇷","Brazil":"🇧🇷","Netherlands":"🇳🇱","Chile":"🇨🇱",
    "Belgium":"🇧🇪","Switzerland":"🇨🇭","Austria":"🇦🇹","Hungary":"🇭🇺","Peru":"🇵🇪",
    "Portugal":"🇵🇹","Poland":"🇵🇱","Monaco":"🇲🇨","Japan":"🇯🇵","India":"🇮🇳",
    "Paraguay":"🇵🇾","Hong Kong":"🇭🇰","Slovakia":"🇸🇰","Georgia":"🇬🇪","Sweden":"🇸🇪",
    "Bolivia":"🇧🇴","Moldova":"🇲🇩","China":"🇨🇳","Chinese Taipei":"🇹🇼",
}

# ── Raw player data ────────────────────────────────────────────────────────
_RAW = [
    # rank, name, country, points, age, hand, grand_slams, career_high, turned_pro
    (1,  "Jannik Sinner",              "Italy",          14750, 24, "R", 3,  1,  2018),
    (2,  "Carlos Alcaraz",             "Spain",          11960, 23, "R", 4,  1,  2018),
    (3,  "Alexander Zverev",           "Germany",        5705,  29, "R", 1,  2,  2013),
    (4,  "Novak Djokovic",             "Serbia",         4460,  39, "R", 24, 1,  2003),
    (5,  "Ben Shelton",                "USA",            4070,  23, "L", 0,  5,  2022),
    (6,  "Félix Auger-Aliassime",      "Canada",         4050,  25, "R", 0,  6,  2017),
    (7,  "Alex de Minaur",             "Australia",      3855,  26, "R", 0,  7,  2016),
    (8,  "Daniil Medvedev",            "Russia",         3760,  30, "R", 1,  1,  2014),
    (9,  "Taylor Fritz",               "USA",            3720,  28, "R", 0,  4,  2015),
    (10, "Alexander Bublik",           "Kazakhstan",     3320,  28, "R", 0,  10, 2015),
    (11, "Lorenzo Musetti",            "Italy",          3115,  23, "R", 0,  11, 2018),
    (12, "Jiří Lehečka",               "Czech Republic", 2665,  23, "R", 0,  12, 2019),
    (13, "Andrey Rublev",              "Russia",         2460,  28, "R", 0,  5,  2014),
    (14, "Flavio Cobolli",             "Italy",          2340,  23, "R", 0,  14, 2019),
    (15, "Karen Khachanov",            "Russia",         2320,  29, "R", 0,  8,  2013),
    (16, "Casper Ruud",                "Norway",         2275,  27, "R", 0,  2,  2015),
    (17, "Luciano Darderi",            "Italy",          2260,  23, "R", 0,  17, 2019),
    (18, "Learner Tien",               "USA",            2180,  19, "R", 0,  18, 2023),
    (19, "Valentin Vacherot",          "Monaco",         2103,  27, "R", 0,  19, 2016),
    (20, "Arthur Fils",                "France",         2040,  21, "R", 0,  20, 2021),
    (21, "Tommy Paul",                 "USA",            1945,  28, "R", 0,  12, 2016),
    (22, "Frances Tiafoe",             "USA",            1905,  27, "R", 0,  10, 2015),
    (23, "Alejandro Davidovich Fokina","Spain",          1860,  26, "R", 0,  20, 2017),
    (24, "Cameron Norrie",             "Great Britain",  1785,  30, "L", 0,  8,  2017),
    (25, "Arthur Rinderknech",         "France",         1736,  28, "R", 0,  25, 2016),
    (26, "Francisco Cerúndolo",        "Argentina",      1570,  26, "R", 0,  21, 2017),
    (27, "Jakub Menšík",               "Czech Republic", 1550,  19, "R", 0,  27, 2022),
    (28, "Tomás Martín Etcheverry",    "Argentina",      1510,  25, "R", 0,  25, 2018),
    (29, "Rafael Jodar",               "Spain",          1461,  24, "R", 0,  29, 2019),
    (30, "João Fonseca",               "Brazil",         1435,  19, "R", 0,  30, 2023),
    (31, "Ignacio Buse",               "Peru",           1412,  20, "R", 0,  31, 2022),
    (32, "Ugo Humbert",                "France",         1370,  27, "L", 0,  25, 2016),
    (33, "Tallon Griekspoor",          "Netherlands",    1340,  29, "R", 0,  24, 2015),
    (34, "Corentin Moutet",            "France",         1323,  26, "L", 0,  34, 2017),
    (35, "Brandon Nakashima",          "USA",            1295,  24, "R", 0,  35, 2019),
    (36, "Alejandro Tabilo",           "Chile",          1278,  27, "R", 0,  20, 2017),
    (37, "Alexander Blockx",           "Belgium",        1238,  21, "R", 0,  37, 2021),
    (38, "Mariano Navone",             "Argentina",      1215,  25, "R", 0,  38, 2018),
    (39, "Denis Shapovalov",           "Canada",         1170,  26, "L", 0,  10, 2015),
    (40, "Zizou Bergs",                "Belgium",        1150,  26, "R", 0,  40, 2018),
    (41, "Jaume Munar",                "Spain",          1145,  28, "R", 0,  41, 2015),
    (42, "Alex Michelsen",             "USA",            1115,  21, "R", 0,  42, 2022),
    (43, "Tomáš Macháč",               "Czech Republic", 1080,  24, "R", 0,  43, 2018),
    (44, "Holger Rune",                "Denmark",        1060,  23, "R", 0,  4,  2019),
    (45, "Adrian Mannarino",           "France",         1037,  37, "L", 0,  22, 2006),
    (46, "Marin Čilić",                "Croatia",        1010,  37, "R", 1,  3,  2004),
    (47, "Sebastian Korda",            "USA",            1000,  25, "R", 0,  23, 2018),
    (48, "Miomir Kecmanović",          "Serbia",         980,   25, "R", 0,  23, 2017),
    (49, "Gabriel Diallo",             "Canada",         975,   23, "R", 0,  49, 2021),
    (50, "Ethan Quinn",                "USA",            974,   20, "R", 0,  50, 2022),
    (51, "Nuno Borges",                "Portugal",       970,   27, "R", 0,  28, 2018),
    (52, "Terence Atmane",             "France",         938,   22, "R", 0,  52, 2021),
    (53, "Yannick Hanfmann",           "Germany",        936,   33, "R", 0,  53, 2013),
    (54, "Fabian Marozsan",            "Hungary",        935,   24, "R", 0,  42, 2019),
    (55, "Botic van de Zandschulp",    "Netherlands",    935,   29, "R", 0,  22, 2016),
    (56, "Juan Manuel Cerúndolo",      "Argentina",      935,   25, "R", 0,  42, 2018),
    (57, "Daniel Altmaier",            "Germany",        930,   27, "L", 0,  52, 2016),
    (58, "Hamad Medjedovic",           "Serbia",         894,   21, "R", 0,  58, 2022),
    (59, "Camilo Ugo Carabelli",       "Argentina",      890,   27, "R", 0,  59, 2016),
    (60, "Thiago Agustín Tirante",     "Argentina",      887,   24, "L", 0,  60, 2019),
    (61, "Alexei Popyrin",             "Australia",      870,   25, "R", 0,  33, 2017),
    (62, "Raphaël Collignon",          "Belgium",        866,   25, "R", 0,  62, 2019),
    (63, "Jenson Brooksby",            "USA",            865,   25, "R", 0,  33, 2019),
    (64, "Sebastián Báez",             "Argentina",      860,   24, "R", 0,  24, 2018),
    (65, "Márton Fucsovics",           "Hungary",        859,   33, "R", 0,  37, 2012),
    (66, "Vít Kopřiva",                "Czech Republic", 856,   26, "R", 0,  66, 2017),
    (67, "Aleksandar Kovacevic",       "USA",            837,   26, "R", 0,  62, 2019),
    (68, "Román Andrés Burruchaga",    "Argentina",      833,   22, "R", 0,  68, 2021),
    (69, "Martín Landaluce",           "Spain",          827,   21, "R", 0,  69, 2021),
    (70, "Lorenzo Sonego",             "Italy",          815,   30, "R", 0,  23, 2013),
    (71, "Adolfo Daniel Vallejo",      "Paraguay",       786,   22, "R", 0,  71, 2021),
    (72, "Dino Prižmić",               "Croatia",        785,   21, "R", 0,  72, 2022),
    (73, "Mattia Bellucci",            "Italy",          777,   23, "R", 0,  73, 2019),
    (74, "Valentin Royer",             "France",         773,   27, "L", 0,  74, 2015),
    (75, "Jack Draper",                "Great Britain",  760,   24, "L", 0,  15, 2019),
    (76, "Reilly Opelka",              "USA",            758,   28, "R", 0,  17, 2015),
    (77, "Arthur Cazaux",              "France",         757,   23, "R", 0,  61, 2020),
    (78, "Kamil Majchrzak",            "Poland",         747,   31, "R", 0,  78, 2013),
    (79, "Stefanos Tsitsipas",         "Greece",         740,   27, "R", 0,  3,  2016),
    (80, "Sumit Nagal",                "India",          735,   27, "R", 0,  68, 2015),
    (81, "Luca Van Assche",            "France",         720,   21, "R", 0,  65, 2021),
    (82, "Pavel Kotov",                "Russia",         715,   26, "R", 0,  42, 2018),
    (83, "Quentin Halys",              "France",         705,   28, "R", 0,  56, 2015),
    (84, "Hubert Hurkacz",             "Poland",         698,   29, "R", 0,  7,  2016),
    (85, "Matteo Berrettini",          "Italy",          685,   30, "R", 0,  6,  2013),
    (86, "Bernabé Zapata Miralles",    "Spain",          678,   28, "R", 0,  27, 2015),
    (87, "Maxime Cressy",              "USA",            670,   27, "R", 0,  38, 2017),
    (88, "Dominic Thiem",              "Austria",        663,   32, "R", 1,  3,  2011),
    (89, "Rinky Hijikata",             "Australia",      658,   24, "R", 0,  89, 2021),
    (90, "Borna Ćorić",                "Croatia",        651,   28, "R", 0,  12, 2013),
    (91, "Roberto Bautista Agut",      "Spain",          648,   37, "R", 0,  9,  2004),
    (92, "Grégoire Barrère",           "France",         641,   30, "R", 0,  71, 2014),
    (93, "Nicolás Jarry",              "Chile",          635,   29, "R", 0,  22, 2015),
    (94, "Christopher Eubanks",        "USA",            628,   28, "R", 0,  28, 2018),
    (95, "Gael Monfils",               "France",         622,   39, "R", 0,  6,  2004),
    (96, "Thiago Seyboth Wild",        "Brazil",         618,   24, "R", 0,  40, 2018),
    (97, "Taro Daniel",                "Japan",          612,   31, "R", 0,  97, 2011),
    (98, "Stan Wawrinka",              "Switzerland",    608,   41, "R", 3,  3,  2002),
    (99, "Emilio Nava",                "USA",            604,   23, "R", 0,  99, 2020),
    (100,"Adam Walton",                "Australia",      601,   24, "R", 0,  99, 2019),
    (101,"Jan Choinski",               "Great Britain",  599,   28, "R", 0,  101,2015),
    (102,"Francisco Comesaña",         "Argentina",      598,   24, "R", 0,  102,2019),
    (103,"Sho Shimabukuro",            "Japan",          596,   24, "R", 0,  103,2019),
    (104,"Matteo Arnaldi",             "Italy",          586,   24, "R", 0,  37, 2019),
    (105,"Jesper de Jong",             "Netherlands",    580,   25, "R", 0,  105,2019),
    (106,"Titouan Droguet",            "France",         578,   23, "R", 0,  106,2020),
    (107,"Dalibor Svrčina",            "Czech Republic", 577,   22, "R", 0,  107,2020),
    (108,"Coleman Wong",               "Hong Kong",      574,   22, "R", 0,  108,2021),
    (109,"Alex Molčan",                "Slovakia",       571,   27, "L", 0,  65, 2016),
    (110,"Nikoloz Basilashvili",       "Georgia",        569,   33, "R", 0,  16, 2006),
    (111,"Sebastian Ofner",            "Austria",        558,   27, "R", 0,  45, 2017),
    (112,"Stan Wawrinka",              "Switzerland",    553,   41, "R", 3,  3,  2002),
    (113,"Cristian Garín",             "Chile",          552,   29, "R", 0,  17, 2014),
    (114,"Jaime Faria",                "Portugal",       548,   21, "R", 0,  114,2021),
    (115,"Martin Damm",                "USA",            547,   23, "R", 0,  115,2021),
    (116,"Juncheng Shang",             "China",          542,   21, "R", 0,  51, 2021),
    (117,"Giulio Zeppieri",            "Italy",          535,   23, "L", 0,  86, 2019),
    (118,"Hugo Gaston",                "France",         528,   24, "R", 0,  56, 2019),
    (119,"Elias Ymer",                 "Sweden",         521,   28, "R", 0,  102,2015),
    (120,"Hubert Hurkacz",             "Poland",         514,   29, "R", 0,  7,  2016),
    (121,"Gilles Simon",               "France",         507,   40, "R", 0,  6,  2002),
    (122,"Facundo Díaz Acosta",        "Argentina",      500,   24, "L", 0,  38, 2019),
    (123,"Constant Lestienne",         "France",         493,   30, "R", 0,  73, 2013),
    (124,"Tseng Chun-hsin",            "Chinese Taipei", 486,   23, "R", 0,  70, 2019),
    (125,"Vasek Pospisil",             "Canada",         479,   35, "R", 0,  25, 2008),
    (126,"Borna Gojo",                 "Croatia",        472,   27, "R", 0,  58, 2017),
    (127,"Yosuke Watanuki",            "Japan",          465,   27, "R", 0,  83, 2017),
    (128,"Benjamin Bonzi",             "France",         458,   29, "R", 0,  36, 2015),
    (129,"Pedro Martínez",             "Spain",          451,   27, "R", 0,  45, 2015),
    (130,"Nishesh Basavareddy",        "USA",            444,   19, "R", 0,  130,2023),
    (131,"James Duckworth",            "Australia",      437,   33, "R", 0,  75, 2010),
    (132,"Omar Jasika",                "Australia",      430,   28, "R", 0,  129,2015),
    (133,"Nicolás Álvarez Varona",     "Spain",          423,   24, "R", 0,  101,2019),
    (134,"Hugo Dellien",               "Bolivia",        416,   30, "R", 0,  77, 2012),
    (135,"Zane Khan",                  "USA",            409,   23, "R", 0,  135,2021),
    (136,"Zhizhen Zhang",              "China",          402,   28, "R", 0,  58, 2014),
    (137,"Pablo Llamas Ruiz",          "Spain",          395,   24, "R", 0,  137,2019),
    (138,"Radu Albot",                 "Moldova",        388,   35, "R", 0,  42, 2008),
    (139,"Alexis Galarneau",           "Canada",         381,   26, "R", 0,  139,2019),
    (140,"Yibing Wu",                  "China",          374,   24, "R", 0,  58, 2020),
    (141,"Denis Kudla",                "USA",            367,   32, "R", 0,  45, 2010),
    (142,"J.J. Wolf",                  "USA",            360,   26, "R", 0,  47, 2019),
    (143,"Maximilian Marterer",        "Germany",        353,   29, "R", 0,  70, 2013),
    (144,"Luca Nardi",                 "Italy",          346,   21, "R", 0,  48, 2021),
    (145,"Borna Gojo",                 "Croatia",        339,   27, "R", 0,  58, 2017),
    (146,"Aleksandar Vukic",           "Australia",      332,   29, "R", 0,  51, 2017),
    (147,"Max Purcell",                "Australia",      325,   27, "R", 0,  51, 2017),
    (148,"Altuğ Çelikbilek",           "Turkey",         318,   28, "R", 0,  47, 2015),
    (149,"Jurij Rodionov",             "Austria",        311,   27, "R", 0,  80, 2017),
    (150,"Mikael Ymer",                "Sweden",         304,   27, "R", 0,  79, 2015),
]

# Build final list, deduplicating by name
_seen = set()
ATP_PLAYERS = []
for row in _RAW:
    rank, name, country, points, age, hand, gs, ch, pro = row
    if name in _seen:
        continue
    _seen.add(name)
    rating = compute_tennis_rating(rank, gs, ch)
    ATP_PLAYERS.append({
        "rank": rank, "name": name, "country": country,
        "points": points, "age": age, "hand": hand,
        "grand_slams": gs, "career_high": ch, "turned_pro": pro,
        "rating": rating, "tier": tier(rating),
        "flag": COUNTRY_FLAGS.get(country, "🎾"),
    })

ATP_BY_RANK = {p["rank"]: p for p in ATP_PLAYERS}
ATP_BY_NAME = {p["name"]: p for p in ATP_PLAYERS}
