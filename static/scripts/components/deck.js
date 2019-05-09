export default {
    name: 'deck',
    data () {
      return {
          processing:false,
      }
    },
    delimiters: ['[[',']]'],
    props: ['coach','tournament'],
    template:   `<div class="modal fade" :id="'deckC'+coach.id+'T'+tournament.id" tabindex="-1" role="dialog" aria-labelledby="deck" aria-hidden="true">
                    <div class="modal-dialog modal-lg">
                    <div class="modal-content">
                        <div class="modal-header">
                            <h5 class="modal-title">Deck for [[coach.short_name]] in [[tournament.name ]]</h5>
                            <button type="button" class="close" data-dismiss="modal" aria-label="Close">
                            <span aria-hidden="true">&times;</span>
                            </button>
                        </div>
                        <div class="modal-body">
                            ...
                        </div>
                    </div>
                    </div>
                </div>`
}