"""Updates statistics and process achievements script"""
import os, sys, getopt
import json
import logging
from logging.handlers import RotatingFileHandler
import datetime as DT

from sqlalchemy.orm.attributes import flag_modified

import bb2
from web import db, app, STORE, STATS_FILE, get_stats
from models.data_models import Coach
from services import NotificationService, AchievementNotificationService, CoachService

app.app_context().push()

ROOT = os.path.dirname(__file__)

# run the application
def main(argv):
    """main()"""
    try:
        opts, args = getopt.getopt(argv,"r")
    except getopt.GetoptError:
        print('update_stats.py -r')
        sys.exit(2)
    refresh = False
    for opt, arg in opts:
        if opt == '-r':
            refresh = True
            print("Recalculating statistics from the scratch")
        
    logger = logging.getLogger('collector')
    logger.setLevel(logging.INFO)
    handler = RotatingFileHandler(
        os.path.join(ROOT, 'logs/collector.log'),
        maxBytes=10000000, backupCount=5,
        encoding='utf-8', mode='a')
    handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
    logger.addHandler(handler)

    matches_folder = os.path.join(STORE, "matches")
    start_date = DT.date.today() - DT.timedelta(days=1)

    agent = bb2.api.Agent(app.config['BB2_API_KEY'])

    stats = get_stats(refresh)

    logger.info("Getting matches since %s", start_date)

    try:
        data = agent.matches(start=start_date)
    except Exception as exc:
        logger.error(exc)
        raise exc

    logger.info("Matches colleted")

    if not os.path.isdir(STORE):
        os.mkdir(STORE)

    if not os.path.isdir(matches_folder):
        os.mkdir(matches_folder)

    for match in data['matches']:
        filename = os.path.join(matches_folder, f"{match['uuid']}.json")
        if os.path.isfile(filename):
            logger.info("File %s exists", filename)
            continue
        logger.info("Collecting match %s", match['uuid'])
        try:
            detailed = agent.match(id=match['uuid'])
            file = open(filename, "a")
            file.write(json.dumps(detailed))
            file.close()
        except Exception as exc:
            logger.error(exc)
            raise exc
        logger.info("Match %s saved", match['uuid'])

    # stats rebuilding
    matchfiles = [f for f in os.listdir(matches_folder)
                  if os.path.isfile(os.path.join(matches_folder, f))]

    if not 'matchfiles' in stats:
        stats['matchfiles'] = []
    
    for file_name in matchfiles:
        file = open(os.path.join(matches_folder, file_name), "r")
        data = json.loads(file.read())
        file.close()

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

        idraces1 = str(team1['idraces'])
        idraces2 = str(team2['idraces'])

        # initialize teams
        team1 = data['match']['teams'][0]
        if not idraces1 in stats['teams']:
            stats['teams'][idraces1] = {'wins':0, 'losses':0, 'draws':0,
                                                'matches':0, 'points':0}
            stats['teams'][idraces1]['idraces'] = idraces1
        team2 = data['match']['teams'][1]
        if not idraces1 in stats['teams']:
            stats['teams'][idraces1] = {'wins':0, 'losses':0, 'draws':0,
                                                'matches':0, 'points':0}
            stats['teams'][idraces1]['idraces'] = idraces1

        #alias coaches and teams
        coach1_stats = stats['coaches'][coach1['coachname']]
        coach2_stats = stats['coaches'][coach2['coachname']]
        team1_stats = stats['teams'][idraces1]
        team2_stats = stats['teams'][idraces1]

        # initialize the team under coach
        idraces1 = str(idraces1)
        idraces2 = str(idraces1)
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
            AchievementNotificationService.notify(msg)
            logger.info(msg)
        tcoach = CoachService.link_bb2_coach(coach2['coachname'],team2['teamname'])
        if tcoach:
            msg = f"{coach2['coachname']} account linked to {tcoach.short_name()}"
            AchievementNotificationService.notify(msg)
            logger.info(msg)
        db.session.commit()
        logger.info("Stats calculation of match %s completed", data['uuid'])

    try:
        stats['coaches'].pop('', None)
        file = open(STATS_FILE, "w")
        file.write(json.dumps(stats))
        file.close()
    except Exception as exp:
        logger.error(exp)
        raise exp
    logger.info("Stats recalculated")

    logger.info("Achievement processing")
    # update achievements
    for coach in Coach.query.all():
        if not coach.bb2_name:
            continue
        coach.achievements['match']['winwithall']['best'] = 0
        coach_stats = stats['coaches'][coach.bb2_name]
        # team achievements
        for team_id, data in coach_stats['teams'].items():
            team_id = str(team_id)
            # win for all achievement
            if data['wins'] > 0:
                coach.achievements['match']['winwithall']['best'] += 1

            for key, ach in coach.achievements['team'][team_id]['played'].items():
                ach['best'] = data['matches']
            for key, ach in coach.achievements['team'][team_id]['wins'].items():
                ach['best'] = data['wins']
            for key, ach in coach.achievements['team'][team_id]['touchdowns'].items():
                ach['best'] = data['inflictedtouchdowns']
            for key, ach in coach.achievements['team'][team_id]['casualties'].items():
                ach['best'] = data['inflictedcasualties']
            for key, ach in coach.achievements['team'][team_id]['kills'].items():
                ach['best'] = data['inflicteddead']
            for key, ach in coach.achievements['team'][team_id]['passes'].items():
                ach['best'] = data['inflictedpasses']

        # match achievements
        coach.achievements['match']['passingtotal1']['best'] = coach_stats['inflictedmeterspassing']
        coach.achievements['match']['passingtotal2']['best'] = coach_stats['inflictedmeterspassing']

        coach.achievements['match']['runningtotal1']['best'] = coach_stats['inflictedmetersrunning']
        coach.achievements['match']['runningtotal2']['best'] = coach_stats['inflictedmetersrunning']

        coach.achievements['match']['surfstotal1']['best'] = coach_stats['inflictedpushouts']
        coach.achievements['match']['surfstotal2']['best'] = coach_stats['inflictedpushouts']

        coach.achievements['match']['blocks1game1']['best'] = coach_stats['max']['inflictedtackles']
        coach.achievements['match']['blocks1game2']['best'] = coach_stats['max']['inflictedtackles']

        coach.achievements['match']['breaks1game1']['best'] = coach_stats['max']['inflictedinjuries']
        coach.achievements['match']['breaks1game2']['best'] = coach_stats['max']['inflictedinjuries']

        coach.achievements['match']['cas1game1']['best'] = coach_stats['max']['inflictedcasualties']
        coach.achievements['match']['cas1game2']['best'] = coach_stats['max']['inflictedcasualties']

        coach.achievements['match']['score1game1']['best'] = coach_stats['max']['inflictedtouchdowns']
        coach.achievements['match']['score1game2']['best'] = coach_stats['max']['inflictedtouchdowns']

        coach.achievements['match']['int1game1']['best'] = coach_stats['max']['inflictedinterceptions']

        coach.achievements['match']['sufferandwin1']['best'] = coach_stats['max']['max_cas_win']
        coach.achievements['match']['sufferandwin2']['best'] = coach_stats['max']['max_cas_win']

        flag_modified(coach, "achievements")
        db.session.commit()

        # update achievements
        coach_mention = f'<@{coach.disc_id}>'
        for key, achievement in coach.achievements['match'].items():
            if achievement['target'] <= achievement['best'] and not achievement['completed']:
                achievement_bank_text = f"{achievement['award_text']} awarded - {achievement['desc']}"
                AchievementNotificationService.notify(
                    f"{coach.short_name()}: {achievement['desc']} - completed"
                )
                call, arg = achievement['award'].split(",")
                res, error = getattr(coach, call)(arg, achievement['desc'])
                if res:
                    logger.info("%s: %s awarded", coach_mention, {achievement['desc']})
                    NotificationService.notify(
                        f"{coach_mention}: {achievement_bank_text}"
                    )
                    coach.achievements['match'][key]['completed'] = True
                    flag_modified(coach, "achievements")
                else:
                    logger.error(error)
                    NotificationService.notify(
                        f"{coach_mention}: {achievement['award_text']} " +
                        f"could not be awarded - {error}"
                    )
        for key1, stat in coach.achievements['team'].items():
            for key2, item in stat.items():
                for key3, achievement in item.items():
                    if (achievement['target'] <= achievement['best'] and
                            not achievement['completed']):
                        achievement_bank_text = f"{achievement['award_text']} awarded - {achievement['desc']}"
                        AchievementNotificationService.notify(
                            f"{coach.short_name()}: {achievement['desc']} - completed"
                        )
                        call, arg = achievement['award'].split(",")
                        res, error = getattr(coach, call)(arg, achievement['desc'])
                        if res:
                            logger.info("%s: %s awarded", coach_mention, {achievement['desc']})
                            coach.achievements['team'][key1][key2][key3]['completed'] = True
                            flag_modified(coach, "achievements")
                            NotificationService.notify(
                                f"{coach_mention}: {achievement_bank_text}"
                            )
                        else:
                            logger.error(error)
                            NotificationService.notify(
                                f"{coach_mention}: {achievement['award_text']} could " +
                                f"not be awarded - {error}"
                            )
        db.session.commit()
    logger.info("Achievement processed")

if __name__ == "__main__":
    main(sys.argv[1:])
