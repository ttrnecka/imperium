import { shallowMount } from '@vue/test-utils';
import Cards from '@/mixins/cards';

const card_1 = {
  template: {
    description: 'Has **Payout**',
    skill_access: "GS",
  },
};

const Component = {
  render() {},
  mixins: [Cards],
};
describe('Cards Mixin', () => {
  it('has_keyword returns true for Payout', () => {
    const wrapper = shallowMount(Component);
    expect(wrapper.vm.has_keyword(card_1, 'Payout')).toBe(true);
  });
  it('has_keyword returns false for Payout!', () => {
    const wrapper = shallowMount(Component);
    expect(wrapper.vm.has_keyword(card_1, 'Payout!')).toBe(false);
  });

  it('skill_access_for returns all skills from the access tree', () => {
    const wrapper = shallowMount(Component);
    const skills = wrapper.vm.skill_access_for(card_1);
    expect(skills).toContain("Dauntless");
    expect(skills).toContain("Break Tackle");
    expect(skills).not.toContain("Hail Mary Pass");
  });

  it('contains correct skill_to_group_map', () => {
    const wrapper = shallowMount(Component);
    expect(wrapper.vm.skill_to_group_map["Accurate"]).toBe("P");
    expect(wrapper.vm.skill_to_group_map["Disturbing Presence"]).toBe("M");
    expect(wrapper.vm.skill_to_group_map["DisturbingPresence"]).toBe("M");
  });

  it('is_skill_double - Dodge is double for non A access player', () => {
    const wrapper = shallowMount(Component);
    expect(wrapper.vm.is_skill_double(card_1, "Dodge")).toBe(true);
  });

  it('is_skill_double - Mighty Blow is double for non A access player', () => {
    const wrapper = shallowMount(Component);
    expect(wrapper.vm.is_skill_double(card_1, "Mighty Blow")).toBe(false);
  });

  it('is_locked - properly handles in_development_deck and in_imperium_deck flags', () => {
    const wrapper = shallowMount(Component);
    expect(wrapper.vm.is_locked({ in_development_deck: true, in_imperium_deck: true })).toBe(true);
    expect(wrapper.vm.is_locked({ in_development_deck: false, in_imperium_deck: true })).toBe(true);
    expect(wrapper.vm.is_locked({ in_development_deck: true, in_imperium_deck: false })).toBe(true);
    expect(wrapper.vm.is_locked({ in_development_deck: false, in_imperium_deck: false })).toBe(false);
  });
});
