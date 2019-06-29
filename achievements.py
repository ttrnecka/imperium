"""Configures default achievements on coaches"""
# run the application
if __name__ == "__main__":
    from sqlalchemy.orm.attributes import flag_modified

    from models.achievements_template import achievements_template
    from models.general import MIXED_TEAMS
    from models.data_models import Coach
    from web import db, app

    app.app_context().push()

    for coach in Coach.query.all():
        if not coach.achievements:
            coach.achievements = achievements_template
        else:
            # match achievements
            for key, ach in achievements_template['match'].items():
                for attr in ['desc', 'award_text', 'award', 'target']:
                    coach.achievements['match'][key][attr] = ach[attr]

          # team achievements
            for team in MIXED_TEAMS:
                for metric in ['played', 'touchdowns', 'casualties', 'kills', 'passes', 'wins']:
                    for key, ach in achievements_template['team'][str(team['idraces'])][metric].items():
                        for attr in ['desc', 'award_text', 'award', 'target']:
                            coach.achievements['team'][str(team['idraces'])][metric][key][attr] = ach[attr]

        flag_modified(coach, "achievements")

    db.session.commit()
