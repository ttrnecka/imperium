export default {
    name: 'injury-picker',
    delimiters: ['[[',']]'],
    data () {
      return {
        injuries: [
            ["SmashedKnee","Niggle"], ["DamagedBack","Niggle"], ["SmashedAnkle","MA-"], ["SmashedHip","MA-"], ["SeriousConcussion","AV-"], ["FracturedSkull","AV-"],
            ["BrokenNeck","AG-"],["SmashedCollarBone","STR-"]
        ],
        selected_injury:"DISABLED"
      }
    },
    watch: {
        selected_injury: function(newValue,oldValue) {
            this.$emit('injured',newValue);
        },
    },
    template:   `<div>
                    <select v-model="selected_injury" class="form-control">
                        <option value="DISABLED" disabled selected>Injury?</option>
                        <option value="">Cancel</option>
                        <option value="X">Reset</option>
                        <option v-for="cas in injuries" :title="cas[0]" :value="cas[0]">[[ cas[0].replace(/([A-Z])/g, ' $1').trim() + " (" + cas[1] + ")" ]]</option>
                    </select>
                </div>`
}