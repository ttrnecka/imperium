"""Updates statistics and process achievements script"""
import os, sys, getopt
import json
import logging
from logging.handlers import RotatingFileHandler

import bb2
from web import db, app
from models.data_models import Coach
from models.marsh_models import leaderboard_coach_schema
from services import Notificator, CoachService
from misc.stats import StatsHandler

app.app_context().push()

ROOT = os.path.dirname(__file__)

# run the application
def main(argv):
    """main()"""
    try:
        opts, args = getopt.getopt(argv,"rs:")
    except getopt.GetoptError:
        print('recalculate_old_stats.py -r -s <season>')
        sys.exit(2)
    refresh = False
    for opt, arg in opts:
        if opt == '-r':
            refresh = True
            print("Recalculating statistics from the scratch")
        if opt == '-s':
            season = arg
            print(f"Using data for season {season}")
        
    logger = logging.getLogger('collector')
    logger.propagate = False
    logger.setLevel(logging.INFO)
    handler = RotatingFileHandler(
        os.path.join(ROOT, 'logs/collector.log'),
        maxBytes=10000000, backupCount=5,
        encoding='utf-8', mode='a')
    handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
    logger.addHandler(handler)

    st = StatsHandler(season)
    stats = st.get_stats(refresh)
    matches_folder = st.matches_folder()

    st.set_folders()

    # stats rebuilding
    matchfiles = [f for f in os.listdir(matches_folder)
                  if os.path.isfile(os.path.join(matches_folder, f))]

    if not 'matchfiles' in stats:
        stats['matchfiles'] = []
    
    for file_name in matchfiles:
        file = open(os.path.join(matches_folder, file_name), "r")
        data = json.loads(file.read())
        file.close()

        match = bb2.Match(data)

        st.create_folder(st.competition_folder(match.competition()))
        st.write_file(os.path.join(st.competition_folder(match.competition()), match.uuid()), data)

        if data['uuid'] in stats['matchfiles']:
            continue
        stats['matchfiles'].append(data['uuid'])

        logger.info("Processing stat calculation of match %s ", data['uuid'])

        # ignore concedes
        if bb2.is_concede(data):
            logger.info("Match %s is concede", data['uuid'])
            continue

        # initialize coaches
        coach1 = data['match']['coaches'][0]
        if not coach1['coachname'] in stats['coaches']:
            stats['coaches'][coach1['coachname']] = {'wins':0, 'losses':0, 'draws':0,
                                                     'matches':0, 'points':0, 'max':{}}
            stats['coaches'][coach1['coachname']]['name'] = coach1['coachname']
            stats['coaches'][coach1['coachname']]['teams'] = {}
        coach2 = data['match']['coaches'][1]
        if not coach2['coachname'] in stats['coaches']:
            stats['coaches'][coach2['coachname']] = {'wins':0, 'losses':0, 'draws':0,
                                                     'matches':0, 'points':0, 'max':{}}
            stats['coaches'][coach2['coachname']]['name'] = coach2['coachname']
            stats['coaches'][coach2['coachname']]['teams'] = {}

        # initialize teams
        team1 = data['match']['teams'][0]
        idraces1 = str(team1['idraces'])
        if not idraces1 in stats['teams']:
            stats['teams'][idraces1] = {'wins':0, 'losses':0, 'draws':0,
                                                'matches':0, 'points':0}
            stats['teams'][idraces1]['idraces'] = idraces1
        team2 = data['match']['teams'][1]
        idraces2 = str(team2['idraces'])
        if not idraces2 in stats['teams']:
            stats['teams'][idraces2] = {'wins':0, 'losses':0, 'draws':0,
                                                'matches':0, 'points':0}
            stats['teams'][idraces2]['idraces'] = idraces2

        #alias coaches and teams
        coach1_stats = stats['coaches'][coach1['coachname']]
        coach2_stats = stats['coaches'][coach2['coachname']]
        team1_stats = stats['teams'][idraces1]
        team2_stats = stats['teams'][idraces2]

        # initialize the team under coach
        if idraces1 not in coach1_stats['teams']:
            coach1_stats['teams'][idraces1] = {'wins':0, 'losses':0, 'draws':0,
                                                       'matches':0, 'points':0}
        if idraces2 not in coach2_stats['teams']:
            coach2_stats['teams'][idraces2] = {'wins':0, 'losses':0, 'draws':0,
                                                       'matches':0, 'points':0}

        # coach team alias
        coach1_team_stats = coach1_stats['teams'][idraces1]
        coach2_team_stats = coach2_stats['teams'][idraces2]

        coach1_stats['matches'] += 1
        team1_stats['matches'] += 1
        coach1_team_stats['matches'] += 1
        coach2_stats['matches'] += 1
        team2_stats['matches'] += 1
        coach2_team_stats['matches'] += 1

        for stat in ["inflictedtouchdowns", "inflictedtackles", "inflictedcasualties",
                     'inflictedinjuries', 'inflictedko', 'inflicteddead', 'inflictedmetersrunning',
                     'inflictedpasses', 'inflictedcatches', 'inflictedinterceptions',
                     'sustainedexpulsions', 'sustainedcasualties', 'sustainedko',
                     'sustainedinjuries', 'sustaineddead', 'inflictedmeterspassing',]:
            if not stat in coach1_stats:
                coach1_stats[stat] = 0
            coach1_stats[stat] += team1[stat]
            if not stat in coach2_stats:
                coach2_stats[stat] = 0
            coach2_stats[stat] += team2[stat]

            if not stat in team1_stats:
                team1_stats[stat] = 0
            team1_stats[stat] += team1[stat]
            if not stat in team2_stats:
                team2_stats[stat] = 0
            team2_stats[stat] += team2[stat]

            if not stat in coach1_team_stats:
                coach1_team_stats[stat] = 0
            coach1_team_stats[stat] += team1[stat]
            if not stat in coach2_team_stats:
                coach2_team_stats[stat] = 0
            coach2_team_stats[stat] += team2[stat]

        #sustd workaround
        if not 'sustainedtouchdowns' in coach1_stats:
            coach1_stats['sustainedtouchdowns'] = 0
        coach1_stats['sustainedtouchdowns'] += team2['inflictedtouchdowns']
        if not 'sustainedtouchdowns' in coach2_stats:
            coach2_stats['sustainedtouchdowns'] = 0
        coach2_stats['sustainedtouchdowns'] += team1['inflictedtouchdowns']

        if not 'sustainedtouchdowns' in team1_stats:
            team1_stats['sustainedtouchdowns'] = 0
        team1_stats['sustainedtouchdowns'] += team2['inflictedtouchdowns']
        if not 'sustainedtouchdowns' in team2_stats:
            team2_stats['sustainedtouchdowns'] = 0
        team2_stats['sustainedtouchdowns'] += team1['inflictedtouchdowns']

        if not 'sustainedtouchdowns' in coach1_team_stats:
            coach1_team_stats['sustainedtouchdowns'] = 0
        coach1_team_stats['sustainedtouchdowns'] += team2['inflictedtouchdowns']
        if not 'sustainedtouchdowns' in coach2_team_stats:
            coach2_team_stats['sustainedtouchdowns'] = 0
        coach2_team_stats['sustainedtouchdowns'] += team1['inflictedtouchdowns']

        # inflictedpushouts fix
        if not 'inflictedpushouts' in coach1_stats:
            coach1_stats['inflictedpushouts'] = 0
        coach1_stats['inflictedpushouts'] += sum(
            [player['stats']['inflictedpushouts'] for player in team1['roster']]
        )
        if not 'inflictedpushouts' in coach2_stats:
            coach2_stats['inflictedpushouts'] = 0
        coach2_stats['inflictedpushouts'] += sum(
            [player['stats']['inflictedpushouts'] for player in team2['roster']]
        )

        if not 'inflictedpushouts' in team1_stats:
            team1_stats['inflictedpushouts'] = 0
        team1_stats['inflictedpushouts'] += sum(
            [player['stats']['inflictedpushouts'] for player in team1['roster']]
        )

        if not 'inflictedpushouts' in team2_stats:
            team2_stats['inflictedpushouts'] = 0
        team2_stats['inflictedpushouts'] += sum(
            [player['stats']['inflictedpushouts'] for player in team2['roster']]
        )

        if not 'inflictedpushouts' in coach1_team_stats:
            coach1_team_stats['inflictedpushouts'] = 0
        coach1_team_stats['inflictedpushouts'] += sum(
            [player['stats']['inflictedpushouts'] for player in team1['roster']]
        )

        if not 'inflictedpushouts' in coach2_team_stats:
            coach2_team_stats['inflictedpushouts'] = 0
        coach2_team_stats['inflictedpushouts'] += sum(
            [player['stats']['inflictedpushouts'] for player in team2['roster']]
        )

        # max tracking
        for stat in ["inflictedtouchdowns", "inflictedtackles", "inflictedcasualties",
                     'inflictedinjuries', 'inflictedinterceptions']:
            if not stat in coach1_stats['max']:
                coach1_stats['max'][stat] = 0
            if team1[stat] > coach1_stats['max'][stat]:
                coach1_stats['max'][stat] = team1[stat]

            if not stat in coach2_stats['max']:
                coach2_stats['max'][stat] = 0
            if team2[stat] > coach2_stats['max'][stat]:
                coach2_stats['max'][stat] = team2[stat]

        if not 'max_cas_win' in coach1_stats['max']:
            coach1_stats['max']['max_cas_win'] = 0
        if not 'max_cas_win' in coach2_stats['max']:
            coach2_stats['max']['max_cas_win'] = 0
        if not 'max_tvdiff_win' in coach1_stats['max']:
            coach1_stats['max']['max_tvdiff_win'] = 0
        if not 'max_tvdiff_win' in coach2_stats['max']:
            coach2_stats['max']['max_tvdiff_win'] = 0
        # wins/drawslosses
        if team1['inflictedtouchdowns'] > team2['inflictedtouchdowns']:
            coach1_stats['wins'] += 1
            coach1_stats['points'] += 3
            coach2_stats['losses'] += 1

            team1_stats['wins'] += 1
            team1_stats['points'] += 3
            team2_stats['losses'] += 1

            coach1_team_stats['wins'] += 1
            coach1_team_stats['points'] += 3
            coach2_team_stats['losses'] += 1

            # cas achievement check
            if team1['sustainedcasualties'] > coach1_stats['max']['max_cas_win']:
                coach1_stats['max']['max_cas_win'] = team1['sustainedcasualties']

            # down TV achievement check
            tv_diff = team2['value'] - team1['value']
            if tv_diff > coach1_stats['max']['max_tvdiff_win']:
                coach1_stats['max']['max_tvdiff_win'] = tv_diff

        elif team1['inflictedtouchdowns'] < team2['inflictedtouchdowns']:
            coach2_stats['wins'] += 1
            coach2_stats['points'] += 3
            coach1_stats['losses'] += 1

            team2_stats['wins'] += 1
            team2_stats['points'] += 3
            team1_stats['losses'] += 1

            coach2_team_stats['wins'] += 1
            coach2_team_stats['points'] += 3
            coach1_team_stats['losses'] += 1

            # cas achievement check
            if team2['sustainedcasualties'] > coach2_stats['max']['max_cas_win']:
                coach2_stats['max']['max_cas_win'] = team2['sustainedcasualties']

            # down TV achievement check
            tv_diff = team1['value'] - team2['value']
            if tv_diff > coach2_stats['max']['max_tvdiff_win']:
                coach2_stats['max']['max_tvdiff_win'] = tv_diff
        else:
            coach1_stats['draws'] += 1
            coach1_stats['points'] += 1
            coach2_stats['draws'] += 1
            coach2_stats['points'] += 1

            team1_stats['draws'] += 1
            team1_stats['points'] += 1
            team2_stats['draws'] += 1
            team2_stats['points'] += 1

            coach1_team_stats['draws'] += 1
            coach1_team_stats['points'] += 1
            coach2_team_stats['draws'] += 1
            coach2_team_stats['points'] += 1

        tcoach = CoachService.link_bb2_coach(coach1['coachname'],team1['teamname'])
        if tcoach:
            msg = f"{coach1['coachname']} account linked to {tcoach.short_name()}"
            Notificator("achievement").notify(msg)
            logger.info(msg)
        tcoach = CoachService.link_bb2_coach(coach2['coachname'],team2['teamname'])
        if tcoach:
            msg = f"{coach2['coachname']} account linked to {tcoach.short_name()}"
            Notificator("achievement").notify(msg)
            logger.info(msg)
        db.session.commit()
        logger.info("Stats calculation of match %s completed", data['uuid'])

    try:
        all_coaches = Coach.query.all()
        stats['coaches_extra']=leaderboard_coach_schema.dump(all_coaches).data
        stats['coaches'].pop('', None)
        st.save_stats(stats)
    except Exception as exp:
        logger.error(exp)
        raise exp
    logger.info("Stats recalculated")

if __name__ == "__main__":
    main(sys.argv[1:])
