from flask_admin.contrib.sqla import ModelView
from misc.helpers import current_coach
from flask import redirect, url_for
from models.data_models import Tournament
from services import TournamentService

class ImperiumModelView(ModelView):
    column_exclude_list = ['date_created', 'date_modified', ]
    def is_accessible(self):
        return current_coach() and current_coach().short_name() == "TomasT"

    def inaccessible_callback(self, name, **kwargs):
        # redirect to login page if user doesn't have access
        return redirect(url_for('index'))

class CoachView(ImperiumModelView):
    can_create = False
    column_exclude_list = ['achievements', 'date_created', 'date_modified', 'disc_id', 'deleted_name']
    column_filters = ['name','deleted', 'bb2_name', 'deleted']

class TournamentView(ImperiumModelView):
    can_create = False
    column_labels = dict(discord_channel='Room', tournament_id='ID', deck_value_limit='Value Limit', deck_limit='Card Limit')
    column_exclude_list = [ 'date_created', 'date_modified', 'type', 'mode', 'signup_close_date',
      'expected_start_date', 'expected_end_date', 'deadline_date', 'reserve_limit',
      'sponsor_description', 'special_rules', 'prizes', 'unique_prize', 'conclave_triggers', 'conclave_triggered', 'banned_cards'
    ]
    column_filters = ['region', 'status', 'admin', 'phase']
    column_editable_list = ['region', 'status', 'admin', 'phase']

    form_choices = {
      'status': [
          ('RUNNING', 'RUNNING'),
          ('OPEN', 'OPEN'),
          ('FINISHED', 'FINISHED'),
      ],
      'region': [
          ('GMAN', 'GMAN'),
          ('REL', 'REL'),
          ('Big O', 'Big O'),
      ],
      'phase': [
          (Tournament.DB_PHASE, Tournament.DB_PHASE),
          (Tournament.LOCKED_PHASE, Tournament.LOCKED_PHASE),
          (Tournament.SP_PHASE, Tournament.SP_PHASE),
          (Tournament.IND_PHASE, Tournament.IND_PHASE),
          (Tournament.BB_PHASE, Tournament.BB_PHASE),
      ]
    }

    def after_model_change(self, form, model, is_created):
      TournamentService.update_tournament_in_sheet(model)