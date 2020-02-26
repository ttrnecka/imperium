<template>
  <div class="row">
    <div class="col-lg-auto" >
        <div class="form-group">
            <input type="text" class="form-control" id="coach_filter"
              placeholder="Search..." v-bind:value="coach_filter"
              v-on:input="debounceCoachSearch($event.target.value)">
        </div>
        <div class="list-group" id="coach-list" role="tablist">
            <a data-toggle="list" v-for="coach in filteredCoaches"
              @click="getCoach(coach.id)" :key="coach.id"
              class="list-group-item list-group-item-action"
              href="#coachDisplay" role="tab"
              aria-controls="home"
              :class="{ active: coach.short_name == selectedCoach.short_name }">{{ coach.short_name }}</a>
        </div>
    </div>
    <div class="col-lg-8">
      <div class="tab-content show" id="nav-tabContent">
        <div class="tab-pane fade show active" id="coachDisplay"
          role="tabpanel" aria-labelledby="coach">
          <ul class="nav nav-tabs" id="coachTab" role="tablist">
              <li class="nav-item">
                <a class="nav-link active" id="cards-tab" data-toggle="tab"
                  href="#coach_cards" role="tab" aria-controls="coach_cards">
                  {{ selectedCoach.short_name }}'s Cards
                </a>
              </li>
              <li class="nav-item">
                <a class="nav-link" id="info-tab" data-toggle="tab" href="#coach_info"
                  role="tab" aria-controls="coach_info" aria-selected="true">
                  {{ selectedCoach.short_name}}'s Info
                </a>
              </li>
              <li v-if="is_owner" class="nav-item">
                <a class="nav-link" id="dusting-tab" data-toggle="tab"
                  href="#coach_dusting" role="tab" aria-controls="coach_dusting"
                  aria-selected="false">Dusting</a>
              </li>
              <li class="nav-item">
                <a class="nav-link" id="stats-tab" data-toggle="tab"
                  href="#coach_stats" role="tab" aria-controls="coach_stats"
                  aria-selected="false">Stats</a>
              </li>
              <li class="nav-item">
                <a class="nav-link" id="stats-tab" data-toggle="tab"
                  href="#coach_achievements" role="tab"
                  aria-controls="coach_achievements"
                  aria-selected="false">Achievements</a>
              </li>
          </ul>
          <div class="tab-content" id="coachTabContent">
            <div class="tab-pane fade" id="coach_info" role="tabpanel"
              aria-labelledby="info-tab">
                <div class="row">
                    <div class="col-6">
                      <h5 class="coach_info">
                      Bank: <small class="text-muted">
                              {{ selectedCoach.account.amount}} coins
                            </small>
                      </h5>
                    </div>
                    <div class="col-3 text-right">
                        <h5 class="coach_info">BB2 Name:</h5>
                    </div>
                    <div class="col-3">
                        <div v-if="is_webadmin" class="form-group">
                            <select class="form-control col-11 coach_info"
                              @change="linkBB2Name()" id="bb2_name"
                              v-model="selectedCoach.bb2_name">
                                <option selected value="">None</option>
                                <option v-for="name in bb2Names" :key="name" :value="name">{{name}}</option>
                            </select>
                        </div>
                        <div v-else>
                            <h5 class="coach_info">
                              <small class="text-muted">
                                {{selectedCoach.bb2_name}}
                              </small>
                            </h5>
                        </div>
                    </div>
                    <div class="col-12">
                        <h5 class="coach_info">
                          Free Packs:
                          <small class="text-muted">
                            {{ getFreePacks(selectedCoach) }}
                          </small>
                        </h5>
                    </div>
                    <div class="tab-content show col-12"
                      id="accordionTournamentsCoach">
                        <h5 class="coach_info">Tournaments:</h5>
                        <tournament
                          v-for="tournament in tournamentsFor(selectedCoach)"
                          :key="tournament.tournament_id"
                          :id="'tourn'+tournament.tournament_id+'coach'"
                          role="tabpanel" aria-labelledby="tournament"
                          :tournament="tournament" :coaches="coaches"
                          data-parent="#accordionTournamentsCoach" :user="user">
                        </tournament>
                    </div>
                    <div class="col-12">
                    <h5 class="coach_info">Transactions:</h5>
                    <table class="table table-striped">
                        <thead>
                            <tr>
                                <th class="th-lg">Date</th>
                                <th class="th-lg">Bank Change</th>
                                <th class="th-lg">Description</th>
                            </tr>
                        </thead>
                        <tbody>
                            <tr
                              v-for="transaction in
                              selectedCoach.account.transactions.slice().reverse()"
                              :key="transaction.id">
                                <td>
                                  {{ print_date(transaction.date_confirmed) }}
                                </td>
                                <td>{{ transaction.price*-1 }}</td>
                                <td>{{ transaction.description }}</td>
                            </tr>
                        </tbody>
                    </table>
                    </div>
                </div>
            </div>
            <div class="tab-pane fade show active" id="coach_cards"
              role="tabpanel" aria-labelledby="cards-tab">
              <div class="col-auto my-1">
                <div class="form-group">
                  <label for="mixed_team_select">Select team:</label>
                  <select class="form-control"
                    id="mixed_team"
                    v-model="selected_team">
                      <option selected value="All">All</option>
                      <option v-for="team in mixed_teams"
                        :value="team.name" :key="team.code">
                        {{ team.name }} ({{ team.races.join() }})
                      </option>
                  </select>
                </div>
                <div class="row">
                  <div class="col-6">
                    <h5>
                    Collection value: {{ cardsValue(selectedCoach.cards) }}
                    </h5>
                  </div>
                  <div class="col-6">
                  <div
                    class="custom-control custom-checkbox mr-sm-2 text-right">
                    <input type="checkbox" class="custom-control-input"
                      id="sptoggle" v-model="show_starter">
                    <label class="custom-control-label"
                      for="sptoggle">Toggle Starter Pack</label>
                  </div>
                  </div>
                </div>
                <div id="accordionCards">
                  <div class="card" v-for="(ctype,index) in card_types"
                    :key="index">
                    <div class="card-header"
                      :id="ctype.replace(/\s/g, '')+'Cards'">
                      <h5 class="mb-0">
                        <button class="btn btn-link"
                          data-toggle="collapse"
                          :data-target="'#collapse'
                          +ctype.replace(/\s/g, '')"
                          aria-expanded="true"
                          :aria-controls="'collapse'
                          +ctype.replace(/\s/g, '')">
                        {{ ctype }} Cards
                        </button>
                      </h5>
                    </div>
                    <div :id="'collapse'+ctype.replace(/\s/g, '')"
                      class="collapse show"
                      :aria-labelledby="ctype.replace(/\s/g, '')+'Cards'"
                      data-parent="#accordionCards">
                      <div class="card-body table-responsive">
                        <table class="table  table-striped">
                            <thead>
                            <tr>
                                <th>
                                  <i class="fas fa-lock"
                                  title="Locked in another tournament">
                                  </i>
                                </th>
                                <th>Rarity</th>
                                <th>Value</th>
                                <th>Name</th>
                                <th>Skills</th>
                                <th>Race</th>
                                <th class="d-none d-sm-table-cell">
                                  Subtype
                                </th>
                                <th class="d-none d-sm-table-cell">
                                  Quantity
                                </th>
                                <th class="d-xs-table-cell d-sm-none">
                                  Q
                                </th>
                            </tr>
                            </thead>
                            <tbody>
                            <tr
                              v-for="card in
                              sortedCardsWithQuantity(selectedCoach.cards,ctype)"
                              :key="card.card.id"
                              :class="rarityclass(card.card.template.rarity)"
                              data-toggle="popover" data-placement="top"
                              :title="card.card.template.name" data-html="true"
                              :data-content="markdown.makeHtml(
                                card.card.template.description)">
                                <td>
                                  <i v-if="is_locked(card.card) &&
                                    is_loggedcoach(selectedCoach.short_name)"
                                    class="fas fa-lock">
                                  </i>
                                </td>
                                <td>
                                  <img class="rarity"
                                    :src="'static/images/'+card.card.template.rarity+'.jpg'"
                                    :alt="card.card.template.rarity"
                                    :title="card.card.template.rarity"
                                    width="20" height="25" />
                                  </td>
                                <td>{{ card.card.template.value }}</td>
                                <td>{{card.card.template.name}}</td>
                                <td><span v-html="skills_for(card.card)"></span></td>
                                <td>{{ card.card.template.race }}</td>
                                <td class="d-none d-sm-table-cell">
                                  {{ card.card.template.subtype }}
                                </td>
                                <td>{{ card.quantity }}</td>
                            </tr>
                            </tbody>
                        </table>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
            <div v-if="is_owner" class="tab-pane fade"
              id="coach_dusting" role="tabpanel" aria-labelledby="dusting-tab">
              <div class="col-auto my-1">
                <div class="row duster_info">
                  <div class="col-9 col-md-6"><h4>{{duster_type}}</h4></div>
                  <div class="col-3 col-md-6 text-right">
                    <button v-if="is_duster_open()" type="button" :disabled="processing"
                      class="btn btn-info" @click="dust_cancel()">Cancel</button>
                    <button v-if="is_duster_full()" :disabled="processing" type="button"
                      class="btn btn-info" @click="dust_commit()">Commit</button>
                  </div>
                </div>
                <div id="accordionCardsDusting">
                    <div class="card" v-for="(ctype,index) in card_types" :key="index">
                      <div class="card-header" :id="ctype.replace(/\s/g, '')+'CardsDusting'">
                        <h5 class="mb-0">
                          <button class="btn btn-link" data-toggle="collapse"
                            :data-target="'#collapse'+ctype.replace(/\s/g, '')+'Dusting'"
                            aria-expanded="true"
                            :aria-controls="'collapse'+ctype.replace(/\s/g, '')+'Dusting'">
                            {{ ctype }} Cards
                          </button>
                        </h5>
                      </div>
                      <div :id="'collapse'+ctype.replace(/\s/g, '')+'Dusting'"
                        class="collapse show"
                        :aria-labelledby="ctype.replace(/\s/g, '')+'CardsDusting'"
                        data-parent="#accordionCardsDusting">
                        <div class="card-body table-responsive">
                          <table class="table table-fixed table-striped">
                            <thead>
                            <tr>
                              <th>Rarity</th>
                              <th class="d-none d-sm-table-cell">Value</th>
                              <th>Name</th>
                              <th>Skills</th>
                              <th class="d-none d-sm-table-cell">Race</th>
                              <th class="d-none d-sm-table-cell">Subtype</th>
                              <th style="width: 15%"></th>
                            </tr>
                            </thead>
                            <tbody>
                            <tr v-for="card in
                              sortedCardsWithoutQuantity(selectedCoach.cards,ctype,false)"
                              :key="card.id" :class="rarityclass(card.template.rarity)">
                              <template v-if="!card.is_starter">
                              <td>
                                <img class="rarity"
                                  :src="'static/images/'+card.template.rarity+'.jpg'"
                                  :alt="card.template.rarity"
                                  :title="card.template.rarity" width="20" height="25" />
                              </td>
                              <td class="d-none d-sm-table-cell">
                                {{ card.template.value }}
                                </td>
                              <td :title="card.template.description">
                                {{ card.template.name }}
                              </td>
                              <td><span v-html="skills_for(card)"></span></td>
                              <td class="d-none d-sm-table-cell">
                                {{ card.template.race }}
                              </td>
                              <td class="d-none d-sm-table-cell">
                                {{ card.template.subtype }}
                              </td>
                              <td class="text-right">
                                <button v-if="is_in_duster(card)" :disabled="processing"
                                  type="button" class="col-12 btn btn-danger"
                                  @click="dust_remove(card)">Remove</button>
                                <button v-else type="button" :disabled="processing"
                                  class="col-12 btn btn-success"
                                  @click="dust_add(card)">Add</button>
                              </td>
                              </template>
                            </tr>
                            </tbody>
                          </table>
                        </div>
                      </div>
                    </div>
                </div>
              </div>
            </div>
            <div class="tab-pane fade" id="coach_achievements"
              role="tabpanel" aria-labelledby="coach-achievements">
              <div class="col-auto my-1">
                <div class="row">
                  <h4 class="col-12">Achievements</h4>
                </div>
                <div class="row">
                  <h5 class="col-12">Hidden Quests</h5>
                </div>
                <div v-for="(ach,index) in quest_achievements(selectedCoach)"
                  :key="'quest'+index" class="row">
                  <template v-if="ach.completed">
                    <div class="col-9">
                      <div class="progress position-relative mb-2">
                        <div class="progress-bar"
                          :class="ach.completed ? 'bg-success' : ''" role="progressbar"
                          :style="'width: '+progress(ach.best/ach.target)+'%;'"
                          aria-valuenow="0" aria-valuemin="0" aria-valuemax="100">
                        </div>
                        <span class="justify-content-center d-flex position-absolute w-100">
                          {{ach.desc}} {{ach.best}} / {{ach.target}}
                        </span>
                      </div>
                    </div>
                    <div class="col-3">
                      <button type="button" :disabled="!achievement_ready(ach)"
                        :class="achievement_state_class(ach)"
                        class="col-12 mb-2 ml-2 btn">
                        {{ach.award_text}}<span v-if="ach.completed"> ✓</span>
                      </button>
                    </div>
                  </template>
                </div>
                <div class="row">
                    <h5 class="col-12">Conclave Achievements</h5>
                </div>
                <div v-for="(ach,index) in conclave_achievements(selectedCoach)"
                  :key="'conclave'+index" class="row">
                  <div class="col-9">
                    <div class="progress position-relative mb-2">
                      <div class="progress-bar"
                        :class="ach.completed ? 'bg-success' : ''" role="progressbar"
                        :style="'width: '+progress(ach.best/ach.target)+'%;'"
                        aria-valuenow="0" aria-valuemin="0" aria-valuemax="100">
                      </div>
                      <span class="justify-content-center d-flex position-absolute w-100">
                        {{ach.desc}} {{ach.best}} / {{ach.target}}
                      </span>
                    </div>
                  </div>
                  <div class="col-3">
                    <button type="button" :disabled="!achievement_ready(ach)"
                      :class="achievement_state_class(ach)"
                      class="col-12 mb-2 ml-2 btn">
                      {{ach.award_text}}<span v-if="ach.completed"> ✓</span>
                    </button>
                  </div>
                </div>
                <div class="row">
                    <h5 class="col-12">Match Achievements (Any Team)</h5>
                </div>
                <div v-for="(ach,index) in match_achievements(selectedCoach)"
                  :key="'match_ach'+index" class="row">
                  <div class="col-9">
                    <div class="progress position-relative mb-2">
                      <div class="progress-bar" :class="ach.completed ? 'bg-success' : ''"
                        role="progressbar"
                        :style="'width: '+progress(ach.best/ach.target)+'%;'"
                        aria-valuenow="0" aria-valuemin="0" aria-valuemax="100">
                      </div>
                      <span class="justify-content-center d-flex position-absolute w-100">
                        {{ach.desc}} {{ach.best}} / {{ach.target}}
                      </span>
                    </div>
                  </div>
                  <div class="col-3">
                    <button type="button" :disabled="!achievement_ready(ach)"
                      :class="achievement_state_class(ach)"
                      class="col-12 mb-2 ml-2 btn">
                      {{ach.award_text}}<span v-if="ach.completed"> ✓</span>
                    </button>
                  </div>
                </div>
                <div class="row">
                    <h5 class="col-12">Mixed Team Achievements</h5>
                </div>
                <div v-for="(ta,index) in team_achievements(selectedCoach)"
                  :key="index" class="row">
                  <h6 class="col-12">{{ta.team_name}}</h6>
                  <template v-for="stat in
                    ['played','touchdowns','casualties','kills','passes','wins']">
                    <template v-for="n in [1,2,3]">
                      <div class="col-9" :key="'progress'+stat+n">
                        <div class="progress position-relative mb-2">
                          <div class="progress-bar"
                            :class="ta.achievements[stat][n].completed ? 'bg-success' : ''"
                            role="progressbar"
                            :style="'width: '+progress(
                              ta.achievements[stat][n].best/ta.achievements[stat][n].target
                            )+'%;'"
                            aria-valuenow="0" aria-valuemin="0" aria-valuemax="100">
                          </div>
                          <span class="justify-content-center d-flex position-absolute w-100">
                          {{ta.achievements[stat][n].desc}} {{ta.achievements[stat][n].best}}
                          /
                          {{ta.achievements[stat][n].target}}
                          </span>
                        </div>
                      </div>
                      <div class="col-3" :key="'button'+stat+n">
                        <button type="button"
                          :disabled="!achievement_ready(ta.achievements[stat][n])"
                          :class="achievement_state_class(ta.achievements[stat][n])"
                          class="col-12 mb-2 ml-2 btn">
                          {{ta.achievements[stat][n].award_text}}
                          <span v-if="ta.achievements[stat][n].completed"> ✓</span>
                        </button>
                      </div>
                    </template>
                  </template>
                </div>
              </div>
            </div>
            <div class="tab-pane fade" id="coach_stats"
              role="tabpanel" aria-labelledby="coach-stats">
              <div class="col-auto my-1">
                <div class="tab-pane fade show active"
                  id="coachStatsDisplay" role="tabpanel"
                  aria-labelledby="coachStats">
                  <ul class="nav nav-tabs" id="coachStatsTab" role="tablist">
                    <li class="nav-item">
                      <a class="nav-link active" id="stats-tab"
                        data-toggle="tab" href="#stats_summary"
                        role="tab" aria-controls="stats_summary">Summary</a>
                    </li>
                    <li class="nav-item" v-for="(team,index)
                      in team_stats(selectedCoach)" :key="index">
                      <a class="nav-link" :id="'stats-tab'+index" data-toggle="tab"
                      :href="'#stats_'+index" role="tab"
                      aria-controls="stats_team">{{team.team_name}}</a>
                    </li>
                  </ul>
                  <div class="tab-content" id="coachStatsTabContent">
                    <div class="tab-pane fade show active" id="stats_summary"
                      role="tabpanel" aria-labelledby="stats-summary-tab">
                      <div class="row mt-2">
                        <div class="col-3"><h5>Wins:</h5></div>
                        <div class="col-1"><h5><small class="text-muted">
                          {{getStat(selectedCoach,'wins')}}</small></h5></div>
                        <div class="col-3"><h5>Draws:</h5></div>
                        <div class="col-1"><h5><small class="text-muted">
                          {{getStat(selectedCoach,'draws')}}</small></h5></div>
                        <div class="col-3"><h5>Losses:</h5></div>
                        <div class="col-1"><h5><small class="text-muted">
                          {{getStat(selectedCoach,'losses')}}</small></h5></div>
                        <div class="col-3"><h5>Matches:</h5></div>
                        <div class="col-1"><h5><small class="text-muted">
                          {{getStat(selectedCoach,'matches')}}</small></h5></div>
                        <div class="col-3"><h5>Points:</h5></div>
                        <div class="col-1"><h5><small class="text-muted">
                          {{getStat(selectedCoach,'points')}}</small></h5></div>
                        <div class="col-3"><h5 title="Points Per Game">PPG:</h5></div>
                        <div class="col-1"><h5><small class="text-muted">
                          {{(getStat(selectedCoach,'points')
                          /
                          getStat(selectedCoach,'matches')).toFixed(2)}}
                          </small></h5>
                        </div>

                        <div class="col-3"><h5>Blocks:</h5></div>
                        <div class="col-1"><h5><small class="text-muted">
                          {{getStat(selectedCoach,'inflictedtackles')}}</small></h5></div>
                        <div class="col-3"><h5 title="Armor Breaks">ABs:</h5></div>
                        <div class="col-1"><h5><small class="text-muted">
                          {{getStat(selectedCoach,'inflictedinjuries')}}</small></h5></div>
                        <div class="col-3"><h5>KOs:</h5></div>
                        <div class="col-1"><h5><small class="text-muted">
                          {{getStat(selectedCoach,'inflictedko')}}</small></h5></div>
                        <div class="col-3"><h5 title="Casualties">Cas:</h5></div>
                        <div class="col-1"><h5><small class="text-muted">
                          {{getStat(selectedCoach,'inflictedcasualties')}}</small></h5></div>
                        <div class="col-3"><h5>Kills:</h5></div>
                        <div class="col-1"><h5><small class="text-muted">
                          {{getStat(selectedCoach,'inflicteddead')}}</small></h5></div>
                        <div class="col-3"><h5 title="Blocks Per Game">BPG:</h5></div>
                        <div class="col-1"><h5><small class="text-muted">
                          {{(getStat(selectedCoach,'inflictedtackles')
                          /
                          getStat(selectedCoach,'matches')).toFixed(2)}}
                          </small></h5>
                        </div>

                        <div class="col-3"><h5>TDs:</h5></div>
                        <div class="col-1"><h5><small class="text-muted">
                          {{getStat(selectedCoach,'inflictedtouchdowns')}}</small></h5></div>
                        <div class="col-3"><h5>Passes:</h5></div>
                        <div class="col-1"><h5><small class="text-muted">
                          {{getStat(selectedCoach,'inflictedpasses')}}</small></h5></div>
                        <div class="col-3"><h5>Passed [m]:</h5></div>
                        <div class="col-1"><h5><small class="text-muted">
                          {{getStat(selectedCoach,'inflictedmeterspassing')}}</small></h5>
                        </div>
                        <div class="col-3"><h5>Ran [m]:</h5></div>
                        <div class="col-1"><h5><small class="text-muted">
                          {{getStat(selectedCoach,'inflictedmetersrunning')}}</small></h5>
                        </div>
                        <div class="col-3"><h5 title="Interceptions">Int:</h5></div>
                        <div class="col-1"><h5><small class="text-muted">
                          {{getStat(selectedCoach,'inflictedinterceptions')}}</small></h5>
                        </div>
                        <div class="col-3"><h5 title="Touchdowns Per Game">TDPG:</h5></div>
                        <div class="col-1"><h5><small class="text-muted">
                          {{(getStat(selectedCoach,'inflictedtouchdowns')
                          /
                          getStat(selectedCoach,'matches')).toFixed(2)}}
                          </small></h5>
                        </div>
                      </div>
                    </div>
                    <div v-for="(team,index) in team_stats(selectedCoach)"
                      class="tab-pane fade" :key="index"
                      :id="'stats_'+index" role="tabpanel" aria-labelledby="stats-team-tab">
                      <div class="row mt-2">
                        <div class="col-3"><h5>Wins:</h5></div>
                        <div class="col-1"><h5><small class="text-muted">
                          {{getTeamStat(team,'wins')}}</small></h5></div>
                        <div class="col-3"><h5>Draws:</h5></div>
                        <div class="col-1"><h5><small class="text-muted">
                          {{getTeamStat(team,'draws')}}</small></h5></div>
                        <div class="col-3"><h5>Losses:</h5></div>
                        <div class="col-1"><h5><small class="text-muted">
                          {{getTeamStat(team,'losses')}}</small></h5></div>
                        <div class="col-3"><h5>Matches:</h5></div>
                        <div class="col-1"><h5><small class="text-muted">
                          {{getTeamStat(team,'matches')}}</small></h5></div>
                        <div class="col-3"><h5>Points:</h5></div>
                        <div class="col-1"><h5><small class="text-muted">
                          {{getTeamStat(team,'points')}}</small></h5></div>
                        <div class="col-3"><h5 title="Points Per Game">PPG:</h5></div>
                        <div class="col-1"><h5><small class="text-muted">
                          {{(getTeamStat(team,'points')
                          /
                          getTeamStat(team,'matches')).toFixed(2)}}
                          </small></h5>
                        </div>

                        <div class="col-3"><h5>Blocks:</h5></div>
                        <div class="col-1"><h5><small class="text-muted">
                          {{getTeamStat(team,'inflictedtackles')}}</small></h5></div>
                        <div class="col-3"><h5 title="Armor Breaks">ABs:</h5></div>
                        <div class="col-1"><h5><small class="text-muted">
                          {{getTeamStat(team,'inflictedinjuries')}}</small></h5></div>
                        <div class="col-3"><h5>KOs:</h5></div>
                        <div class="col-1"><h5><small class="text-muted">
                          {{getTeamStat(team,'inflictedko')}}</small></h5></div>
                        <div class="col-3"><h5 title="Casualties">Cas:</h5></div>
                        <div class="col-1"><h5><small class="text-muted">
                          {{getTeamStat(team,'inflictedcasualties')}}</small></h5></div>
                        <div class="col-3"><h5>Kills:</h5></div>
                        <div class="col-1"><h5><small class="text-muted">
                          {{getTeamStat(team,'inflicteddead')}}</small></h5></div>
                        <div class="col-3"><h5 title="Blocks Per Game">BPG:</h5></div>
                        <div class="col-1"><h5><small class="text-muted">
                          {{(getTeamStat(team,'inflictedtackles')
                          /
                          getTeamStat(team,'matches')).toFixed(2)}}
                          </small></h5>
                        </div>

                        <div class="col-3"><h5>TDs:</h5></div>
                        <div class="col-1"><h5><small class="text-muted">
                          {{getTeamStat(team,'inflictedtouchdowns')}}</small></h5></div>
                        <div class="col-3"><h5>Passes:</h5></div>
                        <div class="col-1"><h5><small class="text-muted">
                          {{getTeamStat(team,'inflictedpasses')}}</small></h5></div>
                        <div class="col-3"><h5>Passed [m]:</h5></div>
                        <div class="col-1"><h5><small class="text-muted">
                          {{getTeamStat(team,'inflictedmeterspassing')}}</small></h5></div>
                        <div class="col-3"><h5>Ran [m]:</h5></div>
                        <div class="col-1"><h5><small class="text-muted">
                          {{getTeamStat(team,'inflictedmetersrunning')}}</small></h5></div>
                        <div class="col-3"><h5 title="Interceptions">Int:</h5></div>
                        <div class="col-1"><h5><small class="text-muted">
                          {{getTeamStat(team,'inflictedinterceptions')}}</small></h5></div>
                        <div class="col-3"><h5 title="Touchdowns Per Game">TDPG:</h5></div>
                        <div class="col-1"><h5><small class="text-muted">
                          {{(getTeamStat(team,'inflictedtouchdowns')
                          /
                          getTeamStat(team,'matches')).toFixed(2)}}
                          </small></h5>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { mapState, mapGetters } from 'vuex';
import Cards from '@/mixins/cards';
import tournament from '@/components/tournament.vue';

export default {
  name: 'coach-content',
  mixins: [Cards],
  components: {
    tournament,
  },
  data() {
    return {
      coach_filter: '',
      selected_team: 'All',
      processing: false,
      selectedCoach: {
        short_name: '',
        account: {
          amount: 0,
          transactions: [],
        },
        tournaments: [],
        cards: [],
        id: 0,
        achievements: {},
        stats: {},
        free_packs: '',
      },
    };
  },
  methods: {
    getFreePacks(coach) {
      return coach.free_packs.split(',').map((e) => {
        switch (e) {
          case 'player':
            return 'Player';
          case 'training':
            return 'Training';
          case 'special':
            return 'Special Play';
          case 'booster_budget':
            return 'Booster';
          case 'booster_premium':
            return 'Booster Premium';
          default:
            return '';
        }
      }).join(', ');
    },
    tournamentsFor(coach) {
      return this.tournaments.filter((e) => coach.tournaments.includes(e.id));
    },
    quest_achievements(coach) {
      if (coach.achievements.quests) {
        return ['collect3legends', 'buildyourownlegend'].map((e) => coach.achievements.quests[e]);
      }
      return [];
    },
    conclave_achievements(coach) {
      if (coach.achievements.conclave) {
        return ['getcursed1', 'getcursed2', 'getcursed3', 'getblessed1', 'getblessed2',
          'getblessed3'].map((e) => coach.achievements.conclave[e]);
      }
      return [];
    },
    team_achievements(coach) {
      if (coach.achievements.team) {
        return [32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42].map((e) => ({
          team_name: this.mixed_teams.find((t) => t.idraces === e).name,
          achievements: coach.achievements.team[e],
        }));
      }
      return [];
    },
    match_achievements(coach) {
      if (coach.achievements.match) {
        return ['passingtotal1', 'passingtotal2', 'runningtotal1', 'runningtotal2',
          'surfstotal1', 'surfstotal2', 'blocks1game1', 'blocks1game2',
          'breaks1game1', 'breaks1game2', 'cas1game1', 'cas1game2',
          'int1game1', 'score1game1', 'score1game2', 'sufferandwin1',
          'sufferandwin2', 'winwithall', 'win500down'].map((e) => coach.achievements.match[e]);
      }
      return [];
    },
    team_stats(coach) {
      if (coach.stats.teams) {
        return [32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42].map((e) => ({
          team_name: this.mixed_teams.find((t) => t.idraces === e).name,
          stats: coach.stats.teams[e],
        }));
      }
      return [];
    },
    getStat(coach, ...args) {
      let pointer = coach.stats;
      for (let i = 0; i < args.length; i += 1) {
        if (pointer[args[i]]) {
          pointer = pointer[args[i]];
        } else {
          return 0;
        }
      }
      return pointer;
    },
    getTeamStat(team, ...args) {
      if (team.stats && team.stats[args[0]]) {
        return team.stats[args[0]];
      }
      return 0;
    },
    getCoach(id) {
      const path = `/coaches/${id}`;
      this.axios.get(path)
        .then((res) => {
          const idx = this.coaches.findIndex((x) => x.id === parseInt(id, 10));
          this.$set(this.coaches, idx, res.data);
          this.selectedCoach = this.coaches[idx];
          this.$nextTick(() => {
            this.$('[data-toggle="popover"]').popover();
          });
        })
        .catch((error) => {
          console.error(error);
        });
    },
    debounceCoachSearch(val) {
      const that = this;
      if (this.search_timeout) clearTimeout(this.search_timeout);
      this.search_timeout = setTimeout(() => {
        that.coach_filter = val;
      }, 300);
    },
    linkBB2Name() {
      const { id } = this.selectedCoach;
      const path = `/coaches/${id}`;
      this.axios.put(path, { name: this.selectedCoach.bb2_name })
        .then((res) => {
          const idx = this.coaches.findIndex((x) => x.id === parseInt(id, 10));
          this.set(this.coaches, idx, res.data);
          this.selectedCoach = this.coaches[idx];
          this.flash('BB2 name updated', 'success', { timeout: 3000 });
        })
        .catch((error) => {
          if (error.response) {
            this.flash(error.response.data.message, 'error', { timeout: 3000 });
          } else {
            console.error(error);
          }
        });
    },
    is_duster() {
      return (this.loggedCoach.duster && this.loggedCoach.duster.type);
    },
    is_in_duster(card) {
      return (this.is_duster() ? this.loggedCoach.duster.cards.includes(card.id) : false);
    },
    is_duster_full() {
      return (this.is_duster() ? this.loggedCoach.duster.cards.length === 10 : false);
    },
    is_duster_open() {
      return (this.is_duster() && this.loggedCoach.duster.status === 'OPEN');
    },
    dust_add(card) {
      this.dust('add', card);
    },
    dust_remove(card) {
      this.dust('remove', card);
    },
    dust_cancel() {
      this.dust('cancel');
    },
    dust_commit() {
      this.dust('commit');
    },
    dust(method, card) {
      let path;
      if (card) {
        path = `/duster/${method}/${card.id}`;
      } else {
        path = `/duster/${method}`;
      }
      let msg;
      this.processing = true;
      this.axios.get(path)
        .then((res) => {
          if (method === 'add') {
            msg = `Card ${card.template.name} flagged for dusting`;
          } else if (method === 'remove') {
            msg = `Card ${card.template.name} - dusting flag removed`;
          } else if (method === 'cancel') {
            msg = 'Dusting cancelled';
          } else if (method === 'commit') {
            const freeCmd = (res.data.type === 'Tryouts' ? '!genpack player <type>' : '!genpack training or !genpack special');
            msg = `Dusting committed! Use ${freeCmd} to generate a free pack!`;
            this.getCoach(this.loggedCoach.id);
          }
          this.loggedCoach.duster = res.data;
          this.flash(msg, 'success', { timeout: 3000 });
        })
        .catch((error) => {
          if (error.response) {
            this.flash(error.response.data.message, 'error', { timeout: 3000 });
          } else {
            console.error(error);
          }
        })
        .then(() => {
          this.processing = false;
        });
    },
    is_loggedcoach(name) {
      if (this.loggedCoach !== undefined
         && (this.loggedCoach.bb2_name === name || this.loggedCoach.short_name === name)) {
        return true;
      }
      return false;
    },
    progress(number) {
      if (number > 1) {
        return 100;
      }
      return number * 100;
    },
    achievement_state_class(ach) {
      if (this.progress(ach.best / ach.target) === 100) {
        return 'btn-success';
      }
      return 'btn-secondary';
    },
    achievement_ready(ach) {
      if (this.progress(ach.best / ach.target) === 100 && !ach.completed) {
        return true;
      }
      return false;
    },
    selectCoach() {
      const c = this.loggedCoach;
      if (c && c.deleted === false) {
        this.getCoach(this.loggedCoach.id);
      } else if (this.coaches.length > 0) {
        this.getCoach(this.coaches[0].id);
      }
    },
  },
  computed: {
    duster_type() {
      if (this.is_duster()) {
        return this.loggedCoach.duster.type;
      }
      return 'No dusting in progress';
    },
    orderedCoaches() {
      const { coaches } = this;
      return coaches.sort((a, b) => a.name.localeCompare(b.name));
    },
    filteredCoaches() {
      return this.orderedCoaches.filter((coach) => coach.name
        .toLowerCase().includes(this.coach_filter.toLowerCase()));
    },
    is_owner() {
      return (this.loggedCoach && this.selectedCoach && this.loggedCoach.id === this.selectedCoach.id);
    },
    ...mapState([
      'user', 'coaches', 'tournaments', 'bb2Names', 'initial_load',
    ]),
    ...mapGetters([
      'loggedCoach', 'is_webadmin',
    ]),
  },
  watch: {
    initial_load: function (newValue) {
      console.log(newValue);
      if (newValue) {
        this.selectCoach();
      }
    },
  },
};
</script>
